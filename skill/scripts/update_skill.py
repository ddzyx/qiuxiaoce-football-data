#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""安全地检查并应用球小策 Skill 官方更新包。"""

import argparse
import difflib
import hashlib
import io
import json
import os
import re
import shutil
import stat
import sys
import tempfile
import urllib.error
import urllib.request
import zipfile
from datetime import datetime

VERSION_URL = "https://www.qiuxiaoce.com/wp-json/abv2-creator/v1/skill/version"
DOWNLOAD_URL = "https://www.qiuxiaoce.com/wp-json/abv2-creator/v1/skill/download"
USER_AGENT = "QiuXiaoCe-Skill-Updater/2.4.3"
ALLOWED_EXTENSIONS = {".md", ".py", ".json", ".txt"}
MAX_FILE_BYTES = 2 * 1024 * 1024
MAX_PACKAGE_BYTES = 20 * 1024 * 1024
REQUIRED_FILES = {
    "SKILL.md",
    "scripts/fetch_match.py",
    "scripts/query_backtest.py",
    "scripts/check_quota.py",
    "scripts/update_skill.py",
    "references/api_schema.json",
}
STATE_FILENAME = ".qiuxiaoce-manifest.json"
OVERRIDES_DIRNAME = "local-overrides"


def emit(payload, exit_code=0):
    """输出结构化 JSON 并返回退出码。"""
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return exit_code


def parse_version(value):
    """将语义化版本转换为可比较元组。"""
    numbers = re.findall(r"\d+", str(value or ""))
    if not numbers:
        return (0, 0, 0)
    numbers = [int(item) for item in numbers[:3]]
    while len(numbers) < 3:
        numbers.append(0)
    return tuple(numbers)


def read_local_version(skill_dir):
    """从 SKILL.md frontmatter 读取本地版本。"""
    path = os.path.join(skill_dir, "SKILL.md")
    try:
        with open(path, "r", encoding="utf-8") as handle:
            for line in handle:
                match = re.match(r"^version:\s*['\"]?([^'\"\s]+)", line.strip())
                if match:
                    return match.group(1)
    except OSError:
        pass
    return "0.0.0"


def fetch_json(url):
    """下载并解析 JSON。"""
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_bytes(url):
    """下载二进制更新包。"""
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=45) as response:
        data = response.read(MAX_PACKAGE_BYTES + 1)
        if len(data) > MAX_PACKAGE_BYTES:
            raise ValueError("更新包超过大小限制")
        return data


def safe_extract(zip_bytes, target_dir):
    """校验 ZIP 路径与文件类型后，手工解压到临时目录。"""
    extracted = []
    total_bytes = 0
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        for info in archive.infolist():
            raw_name = info.filename.replace("\\", "/")
            if not raw_name or raw_name.endswith("/"):
                continue
            if raw_name.startswith("/") or re.match(r"^[A-Za-z]:", raw_name):
                raise ValueError("更新包包含绝对路径")
            normalized = os.path.normpath(raw_name).replace(os.sep, "/")
            if normalized in (".", "..") or normalized.startswith("../") or "/../" in normalized:
                raise ValueError("更新包包含越界路径")
            mode = (info.external_attr >> 16) & 0o170000
            if mode == stat.S_IFLNK:
                raise ValueError("更新包不允许包含符号链接")
            extension = os.path.splitext(normalized)[1].lower()
            if extension not in ALLOWED_EXTENSIONS:
                raise ValueError("更新包包含不允许的文件类型：%s" % normalized)
            if info.file_size > MAX_FILE_BYTES:
                raise ValueError("更新包单个文件超过大小限制：%s" % normalized)
            total_bytes += info.file_size
            if total_bytes > MAX_PACKAGE_BYTES:
                raise ValueError("更新包解压后超过总大小限制")

            destination = os.path.join(target_dir, *normalized.split("/"))
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            with archive.open(info, "r") as source, open(destination, "wb") as target:
                shutil.copyfileobj(source, target)
            extracted.append(normalized)
    return sorted(extracted)


def sha256_file(path):
    """计算文件 SHA-256。"""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_manifest(staged_dir, manifest):
    """按服务端签名清单校验解压后的文件集合与 SHA-256。"""
    if not isinstance(manifest, dict) or not manifest:
        raise ValueError("服务端未提供有效文件哈希清单")
    expected = sorted(manifest.keys())
    missing = [name for name in expected if not os.path.isfile(os.path.join(staged_dir, *name.split("/")))]
    if missing:
        raise ValueError("更新包缺少清单文件：%s" % ", ".join(missing[:5]))
    actual = []
    for root, _, files in os.walk(staged_dir):
        for filename in files:
            path = os.path.join(root, filename)
            actual.append(os.path.relpath(path, staged_dir).replace(os.sep, "/"))
    unexpected = sorted(set(actual) - set(expected))
    if unexpected:
        raise ValueError("更新包包含清单外文件：%s" % ", ".join(unexpected[:5]))
    mismatched = []
    for name, expected_hash in manifest.items():
        path = os.path.join(staged_dir, *name.split("/"))
        if sha256_file(path) != str(expected_hash).lower():
            mismatched.append(name)
    if mismatched:
        raise ValueError("更新包文件哈希校验失败：%s" % ", ".join(mismatched[:5]))


def load_installed_state(skill_dir):
    """读取上次更新写入的官方文件哈希清单；不存在时返回 None。"""
    path = os.path.join(skill_dir, STATE_FILENAME)
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as handle:
            state = json.load(handle)
    except (OSError, ValueError):
        return None
    if not isinstance(state, dict) or not isinstance(state.get("files"), dict):
        return None
    return state


def write_installed_state(skill_dir, version, manifest):
    """更新成功后记录官方版本与文件哈希，作为下次识别本地改动的基线。"""
    path = os.path.join(skill_dir, STATE_FILENAME)
    payload = {
        "version": str(version),
        "updated_at": datetime.now().isoformat(timespec="seconds"),
        "files": {name: str(value).lower() for name, value in manifest.items()},
    }
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass


def iter_local_files(skill_dir):
    """遍历用户安装目录中的普通文件，跳过隐藏文件、缓存与字节码。"""
    results = []
    for root, dirs, files in os.walk(skill_dir):
        dirs[:] = [name for name in dirs if not name.startswith(".") and name != "__pycache__"]
        for filename in files:
            if filename.startswith(".") or filename.endswith(".pyc"):
                continue
            path = os.path.join(root, filename)
            if os.path.islink(path):
                continue
            results.append(os.path.relpath(path, skill_dir).replace(os.sep, "/"))
    return sorted(results)


def classify_local_drift(skill_dir, incoming_manifest):
    """识别用户对官方文件的改动与用户自行新增的文件。"""
    incoming = set(incoming_manifest.keys())
    state = load_installed_state(skill_dir)
    baseline = state.get("files") if state else None
    user_modified = []
    user_extra = []
    for relative in iter_local_files(skill_dir):
        path = os.path.join(skill_dir, *relative.split("/"))
        if relative not in incoming:
            user_extra.append(relative)
            continue
        try:
            local_hash = sha256_file(path)
        except OSError:
            continue
        if baseline and relative in baseline:
            if local_hash != baseline[relative]:
                user_modified.append(relative)
        elif local_hash != str(incoming_manifest[relative]).lower():
            user_modified.append(relative)
    return sorted(user_modified), sorted(user_extra)


def apply_update(skill_dir, staged_dir, user_modified, user_extra, remote_version, manifest):
    """备份旧目录并切换到已验证的新目录，保留用户增量并归档用户改动，失败时回滚。"""
    parent_dir = os.path.dirname(skill_dir)
    backup_root = os.path.join(parent_dir, "skill-backups")
    os.makedirs(backup_root, exist_ok=True)
    backup_dir = os.path.join(
        backup_root,
        "qiuxiaoce-skill-%s-%s" % (datetime.now().strftime("%Y%m%d%H%M%S"), os.getpid()),
    )

    os.replace(skill_dir, backup_dir)
    restored = []
    archived = []
    try:
        shutil.copytree(staged_dir, skill_dir)

        for relative in user_extra:
            source = os.path.join(backup_dir, *relative.split("/"))
            target = os.path.join(skill_dir, *relative.split("/"))
            if os.path.isfile(source) and not os.path.exists(target):
                os.makedirs(os.path.dirname(target), exist_ok=True)
                shutil.copy2(source, target)
                restored.append(relative)

        if user_modified:
            overrides_root = os.path.join(skill_dir, OVERRIDES_DIRNAME)
            for relative in user_modified:
                source = os.path.join(backup_dir, *relative.split("/"))
                target = os.path.join(overrides_root, *relative.split("/"))
                if os.path.isfile(source):
                    os.makedirs(os.path.dirname(target), exist_ok=True)
                    shutil.copy2(source, target)
                    archived.append(relative)

        write_installed_state(skill_dir, remote_version, manifest)

        for relative in ("scripts/fetch_match.py", "scripts/query_backtest.py", "scripts/check_quota.py", "scripts/update_skill.py"):
            path = os.path.join(skill_dir, *relative.split("/"))
            if os.path.isfile(path):
                try:
                    os.chmod(path, 0o755)
                except OSError:
                    pass
    except Exception:
        if os.path.exists(skill_dir):
            shutil.rmtree(skill_dir)
        os.replace(backup_dir, skill_dir)
        raise
    return backup_dir, restored, archived


def list_pending_overrides(skill_dir):
    """列出 local-overrides 中尚未处理的归档文件（相对官方路径）。"""
    root = os.path.join(skill_dir, OVERRIDES_DIRNAME)
    if not os.path.isdir(root):
        return []
    results = []
    for current_root, dirs, files in os.walk(root):
        dirs[:] = [name for name in dirs if not name.startswith(".")]
        for filename in files:
            if filename.startswith("."):
                continue
            path = os.path.join(current_root, filename)
            results.append(os.path.relpath(path, root).replace(os.sep, "/"))
    return sorted(results)


def build_conflict_report(skill_dir):
    """为每个归档的本地改动生成与官方新版的统一差异，供 LLM 分析取舍。"""
    root = os.path.join(skill_dir, OVERRIDES_DIRNAME)
    conflicts = []
    for relative in list_pending_overrides(skill_dir):
        archived_path = os.path.join(root, *relative.split("/"))
        official_path = os.path.join(skill_dir, *relative.split("/"))
        old_lines = []
        new_lines = []
        try:
            with open(archived_path, "r", encoding="utf-8", errors="replace") as handle:
                old_lines = handle.readlines()
        except OSError:
            pass
        if os.path.isfile(official_path):
            try:
                with open(official_path, "r", encoding="utf-8", errors="replace") as handle:
                    new_lines = handle.readlines()
            except OSError:
                pass
        diff_lines = list(difflib.unified_diff(
            old_lines, new_lines,
            fromfile="我的版本（%s/%s）" % (OVERRIDES_DIRNAME, relative),
            tofile="官方新版（%s）" % relative,
            lineterm="",
        ))
        conflicts.append({
            "file": relative,
            "archived_at": "%s/%s" % (OVERRIDES_DIRNAME, relative),
            "official_exists": os.path.isfile(official_path),
            "diff": "\n".join(diff_lines[:400]),
            "diff_truncated": len(diff_lines) > 400,
        })
    return conflicts


def resolve_conflict(skill_dir, relative, choice):
    """按用户决定处理归档冲突：user=恢复本地版本覆盖官方，official=放弃归档。"""
    normalized = os.path.normpath(str(relative).replace("\\", "/")).replace(os.sep, "/")
    if (not normalized or normalized in (".", "..") or normalized.startswith("/")
            or normalized.startswith("../") or "/../" in normalized
            or re.match(r"^[A-Za-z]:", normalized)):
        raise ValueError("非法的冲突文件路径")
    archived_path = os.path.join(skill_dir, OVERRIDES_DIRNAME, *normalized.split("/"))
    if not os.path.isfile(archived_path):
        raise ValueError("归档不存在：%s" % normalized)
    if choice == "user":
        target = os.path.join(skill_dir, *normalized.split("/"))
        os.makedirs(os.path.dirname(target), exist_ok=True)
        shutil.copy2(archived_path, target)
    os.remove(archived_path)
    current = os.path.dirname(archived_path)
    root = os.path.join(skill_dir, OVERRIDES_DIRNAME)
    while current.startswith(root) and current != root:
        if os.listdir(current):
            break
        os.rmdir(current)
        current = os.path.dirname(current)


def main():
    """检查远端版本，或在校验通过后应用更新。"""
    parser = argparse.ArgumentParser(description="球小策 Skill 安全更新工具")
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--check", action="store_true", help="只检查远端版本，不修改本地文件")
    action.add_argument("--apply", action="store_true", help="校验并应用远端更新包")
    parser.add_argument("--dry-run", action="store_true", help="下载并校验更新包，但不切换目录")
    parser.add_argument("--force", action="store_true", help="允许同版本或降级覆盖；仅限明确排障时使用")
    parser.add_argument("--diff", action="store_true", help="列出 local-overrides 中待处理的本地改动及与官方新版的差异")
    parser.add_argument("--resolve", metavar="FILE", help="处理指定的归档冲突文件（相对官方路径，如 templates/template_tactical.md）")
    parser.add_argument("--choice", choices=["user", "official"], default="official",
                        help="配合 --resolve：user=恢复我的版本覆盖官方；official=采用官方新版并放弃归档（默认）")
    args = parser.parse_args()

    script_path = os.path.abspath(__file__)
    skill_dir = os.path.dirname(os.path.dirname(script_path))
    if (os.path.islink(skill_dir)
            or not os.path.isfile(os.path.join(skill_dir, "SKILL.md"))
            or not os.path.isdir(os.path.join(skill_dir, "scripts"))):
        return emit({"error": True, "message": "无法确认安全的 Skill 安装目录。"}, 1)

    if args.diff:
        conflicts = build_conflict_report(skill_dir)
        return emit({
            "success": True,
            "pending_conflicts": len(conflicts),
            "conflicts": conflicts,
            "message": "无待处理的本地改动。" if not conflicts
            else "存在 %d 个本地改动与官方新版不一致，请分析差异并询问用户取舍。" % len(conflicts),
        }, 0)
    if args.resolve:
        try:
            resolve_conflict(skill_dir, args.resolve, args.choice)
        except (ValueError, OSError) as error:
            return emit({"error": True, "stage": "resolve", "message": str(error)}, 1)
        return emit({
            "success": True,
            "resolved": args.resolve,
            "choice": args.choice,
            "remaining_conflicts": list_pending_overrides(skill_dir),
            "message": "已按用户决定处理：%s（%s）。" % (
                args.resolve, "恢复我的版本" if args.choice == "user" else "采用官方新版"),
        }, 0)

    local_version = read_local_version(skill_dir)
    try:
        remote = fetch_json(VERSION_URL)
    except (urllib.error.URLError, TimeoutError, ValueError) as error:
        return emit({"error": True, "stage": "version", "message": str(error)}, 1)

    remote_version = str(remote.get("version") or "")
    update_available = parse_version(remote_version) > parse_version(local_version)
    base = {
        "success": True,
        "local_version": local_version,
        "remote_version": remote_version,
        "update_available": update_available,
        "release_date": remote.get("release_date"),
        "changelog": remote.get("changelog"),
    }

    if args.check or (not args.apply and not args.dry_run):
        base["message"] = "发现新版本；确认后使用 --apply 更新。" if update_available else "当前已是最新版本。"
        return emit(base, 0)
    if not update_available and not args.force:
        base["applied"] = False
        base["message"] = "远端版本不高于本地版本，未执行覆盖。确需重装时请显式使用 --force。"
        return emit(base, 0)

    incoming_manifest = remote.get("files")
    if isinstance(incoming_manifest, dict) and incoming_manifest:
        user_modified, user_extra = classify_local_drift(skill_dir, incoming_manifest)
    else:
        user_modified, user_extra = [], []
    if user_modified or user_extra:
        base["local_customizations"] = {
            "modified_official_files": user_modified,
            "user_added_files": user_extra,
        }

    try:
        package = fetch_bytes(str(remote.get("download_url") or DOWNLOAD_URL))
    except (urllib.error.URLError, TimeoutError, ValueError) as error:
        return emit({"error": True, "stage": "download", "message": str(error)}, 1)

    try:
        with tempfile.TemporaryDirectory(prefix="qiuxiaoce-skill-") as temp_dir:
            staged_dir = os.path.join(temp_dir, "staged")
            os.makedirs(staged_dir, exist_ok=True)
            extracted = safe_extract(package, staged_dir)
            missing_required = sorted(REQUIRED_FILES - set(extracted))
            if missing_required:
                raise ValueError("更新包缺少核心文件：%s" % ", ".join(missing_required))
            verify_manifest(staged_dir, incoming_manifest)
            staged_version = read_local_version(staged_dir)
            if parse_version(staged_version) != parse_version(remote_version):
                raise ValueError("更新包内 SKILL.md 版本与服务端版本不一致")
            if args.dry_run:
                base.update({
                    "applied": False,
                    "dry_run": True,
                    "verified_files": len(extracted),
                    "message": "更新包已通过校验，未修改本地文件；用户新增文件会保留，用户改过的官方文件会归档到 local-overrides/。",
                })
                return emit(base, 0)
            backup_dir, restored, archived = apply_update(
                skill_dir, staged_dir, user_modified, user_extra,
                remote_version, incoming_manifest,
            )
    except (OSError, ValueError, zipfile.BadZipFile) as error:
        return emit({"error": True, "stage": "verify_or_apply", "message": str(error)}, 1)

    message = "Skill 已更新，原版本已备份。"
    if restored:
        message += " 已保留 %d 个用户新增文件。" % len(restored)
    if archived:
        message += (" %d 个被本地修改过的官方文件已更新为新版，旧版归档于 %s/；"
                    "请运行 --diff 分析差异并询问用户取舍后，用 --resolve 处理。" % (len(archived), OVERRIDES_DIRNAME))
    base.update({
        "applied": True,
        "verified_files": len(extracted),
        "backup_dir": backup_dir,
        "user_files_restored": restored,
        "modified_files_archived": archived,
        "message": message,
    })
    return emit(base, 0)


if __name__ == "__main__":
    sys.exit(main())
