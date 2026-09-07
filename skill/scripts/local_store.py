#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""球小策 Skill 本地数据层（SQLite，零依赖，仅用 Python 标准库）。

职责：
1. 自动建库（首次运行任意命令即创建，位于 Skill 同级 data/ 目录）；
2. 读穿缓存：接口响应按「端点 + 归一化参数」落库，TTL 内命中不再扣点；
3. 事实表：赛果 fixtures / 研报 reports 永久留存，构成用户自己的分析数据集；
4. 本地分析：query 提供只读 SQL（LLM 可直接对本地库复盘），stats/export 辅助。

安全：不存储 API Key；query 仅允许 SELECT。
更新安全：update_skill.py 的白名单文件类型不含 .db，升级 Skill 不会覆盖本库。
"""

import argparse
import csv
import hashlib
import json
import os
import sqlite3
import sys
import time

SCHEMA_VERSION = 1

# 数据层 TTL（秒）；None 表示永久留存
TTL_RULES = [
    ("match-pack", 2 * 3600),
    ("injuries", 6 * 3600),
    ("quotes", 30 * 60),
    ("market", 30 * 60),
    ("today", 6 * 3600),
    ("form", 6 * 3600),
    ("standings", 12 * 3600),
    ("fixtures", 12 * 3600),
    ("teams", 12 * 3600),
    ("leagues", 12 * 3600),
    ("players", 12 * 3600),
]
DEFAULT_TTL = 24 * 3600


def db_path():
    """库文件固定放在 Skill 根目录下的 data/（脚本所在目录的上一级）。"""
    skill_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(skill_root, "data")
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, "qiuxiaoce_local.db")


def connect():
    """打开数据库并确保表结构存在（WAL 模式防并发锁）。"""
    conn = sqlite3.connect(db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    ensure_schema(conn)
    return conn


def ensure_schema(conn):
    """幂等建表：缓存表 + 事实表 + 元信息表。"""
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS meta (
            key TEXT PRIMARY KEY,
            value TEXT
        );
        CREATE TABLE IF NOT EXISTS cache (
            cache_key TEXT PRIMARY KEY,
            endpoint TEXT NOT NULL,
            params TEXT NOT NULL DEFAULT '',
            payload TEXT NOT NULL,
            fetched_at REAL NOT NULL,
            expires_at REAL
        );
        CREATE INDEX IF NOT EXISTS idx_cache_endpoint ON cache(endpoint);
        CREATE TABLE IF NOT EXISTS fixtures (
            fixture_id INTEGER PRIMARY KEY,
            date TEXT,
            timestamp INTEGER,
            season INTEGER,
            round TEXT,
            league_id INTEGER,
            league_name TEXT,
            home_team_id INTEGER,
            home_team TEXT,
            away_team_id INTEGER,
            away_team TEXT,
            home_goals INTEGER,
            away_goals INTEGER,
            ht_home INTEGER,
            ht_away INTEGER,
            status TEXT,
            lottery_code TEXT,
            lottery_code_beidan TEXT,
            source_endpoint TEXT,
            fetched_at REAL NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_fixtures_date ON fixtures(date);
        CREATE INDEX IF NOT EXISTS idx_fixtures_league ON fixtures(league_id, season);
        CREATE TABLE IF NOT EXISTS reports (
            post_id INTEGER PRIMARY KEY,
            title TEXT,
            date TEXT,
            lottery_id TEXT,
            lottery_type TEXT,
            home_team TEXT,
            away_team TEXT,
            kickoff TEXT,
            actual_score TEXT,
            is_correct TEXT,
            hit_items TEXT,
            recommendation TEXT,
            content_text TEXT,
            ai_prediction TEXT,
            fetched_at REAL NOT NULL
        );
        """
    )
    row = conn.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()
    if row is None:
        conn.execute(
            "INSERT INTO meta (key, value) VALUES ('schema_version', ?), ('created_at', ?)",
            (str(SCHEMA_VERSION), time.strftime("%Y-%m-%d %H:%M:%S")),
        )
    conn.commit()


def ttl_for(endpoint):
    """按端点前缀取 TTL；None 表示永久。"""
    for prefix, ttl in TTL_RULES:
        if prefix in endpoint:
            return ttl
    return DEFAULT_TTL


def make_cache_key(endpoint, params=None):
    """缓存键 = 端点 + 归一化参数（键排序）的 SHA-256。"""
    if params:
        normalized = json.dumps(params, sort_keys=True, ensure_ascii=False)
    else:
        normalized = ""
    return hashlib.sha256((endpoint + "|" + normalized).encode("utf-8")).hexdigest()


class LocalStore:
    """本地数据层门面：get/set 读穿缓存 + 事实表写入。"""

    def __init__(self):
        self.conn = connect()

    def get(self, endpoint, params=None):
        """TTL 内命中返回 payload（dict），未命中或过期返回 None。"""
        key = make_cache_key(endpoint, params)
        row = self.conn.execute(
            "SELECT payload, expires_at FROM cache WHERE cache_key = ?", (key,)
        ).fetchone()
        if not row:
            return None
        if row["expires_at"] is not None and row["expires_at"] < time.time():
            return None
        try:
            return json.loads(row["payload"])
        except (ValueError, TypeError):
            return None

    def set(self, endpoint, payload, params=None, ttl="auto"):
        """写入缓存。ttl='auto' 按端点规则；传秒数显式覆盖；传 None 永久。"""
        key = make_cache_key(endpoint, params)
        effective = ttl_for(endpoint) if ttl == "auto" else ttl
        expires_at = (time.time() + effective) if effective else None
        self.conn.execute(
            "INSERT OR REPLACE INTO cache (cache_key, endpoint, params, payload, fetched_at, expires_at)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (
                key,
                endpoint,
                json.dumps(params or {}, sort_keys=True, ensure_ascii=False),
                json.dumps(payload, ensure_ascii=False),
                time.time(),
                expires_at,
            ),
        )
        self.conn.commit()

    def save_fixtures(self, rows, source_endpoint=""):
        """赛果事实表入库（INSERT OR REPLACE，后到的数据覆盖同 id 旧值）。"""
        for f in rows or []:
            if not isinstance(f, dict) or not f.get("fixture_id"):
                continue
            self.conn.execute(
                """INSERT OR REPLACE INTO fixtures
                (fixture_id, date, timestamp, season, round, league_id, league_name,
                 home_team_id, home_team, away_team_id, away_team,
                 home_goals, away_goals, ht_home, ht_away, status,
                 lottery_code, lottery_code_beidan, source_endpoint, fetched_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    f.get("fixture_id"),
                    f.get("date"),
                    f.get("timestamp"),
                    f.get("season"),
                    f.get("round"),
                    f.get("league_id"),
                    f.get("league_name"),
                    f.get("home_team_id"),
                    f.get("home_team_name") or f.get("home_team"),
                    f.get("away_team_id"),
                    f.get("away_team_name") or f.get("away_team"),
                    f.get("home_goals"),
                    f.get("away_goals"),
                    f.get("ht_home"),
                    f.get("ht_away"),
                    f.get("status"),
                    f.get("lottery_code"),
                    f.get("lottery_code_beidan"),
                    source_endpoint,
                    time.time(),
                ),
            )
        self.conn.commit()

    def save_reports(self, rows):
        """研报事实表入库（摘要与全文分步填充，全文后写覆盖摘要）。"""
        for r in rows or []:
            if not isinstance(r, dict) or not r.get("id"):
                continue
            match = r.get("match") or {}
            existing = self.conn.execute(
                "SELECT content_text FROM reports WHERE post_id = ?", (int(r["id"]),)
            ).fetchone()
            content_text = r.get("content_text")
            if content_text is None and existing:
                content_text = existing["content_text"]
            ai_prediction = r.get("ai_prediction")
            self.conn.execute(
                """INSERT OR REPLACE INTO reports
                (post_id, title, date, lottery_id, lottery_type, home_team, away_team,
                 kickoff, actual_score, is_correct, hit_items, recommendation,
                 content_text, ai_prediction, fetched_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    int(r["id"]),
                    r.get("title"),
                    r.get("date"),
                    r.get("lottery_id"),
                    r.get("lottery_type"),
                    match.get("home_team"),
                    match.get("away_team"),
                    match.get("kickoff"),
                    match.get("actual_score"),
                    match.get("is_correct"),
                    json.dumps(match.get("hit_items") or [], ensure_ascii=False),
                    r.get("recommendation"),
                    content_text,
                    json.dumps(ai_prediction, ensure_ascii=False) if ai_prediction else None,
                    time.time(),
                ),
            )
        self.conn.commit()

    def query(self, sql):
        """只读 SQL 查询（仅允许 SELECT），返回行列表。"""
        text = (sql or "").strip().rstrip(";")
        if not text[:6].upper() == "SELECT":
            raise ValueError("仅允许 SELECT 查询")
        lowered = text.lower()
        for banned in ("insert", "update", "delete", "drop", "alter", "attach", "pragma"):
            if " " + banned in " " + lowered or lowered.startswith(banned):
                raise ValueError("仅允许只读查询")
        cursor = self.conn.execute(text)
        return [dict(row) for row in cursor.fetchall()]

    def stats(self):
        """库概况：各表行数与缓存命中结构。"""
        out = {}
        for table in ("cache", "fixtures", "reports"):
            out[table] = self.conn.execute(f"SELECT COUNT(*) AS c FROM {table}").fetchone()["c"]
        out["cache_fresh"] = self.conn.execute(
            "SELECT COUNT(*) AS c FROM cache WHERE expires_at IS NULL OR expires_at > ?",
            (time.time(),),
        ).fetchone()["c"]
        out["db_path"] = db_path()
        return out

    def purge(self, all_entries=False):
        """清理缓存。默认只清过期项；all_entries=True 清空缓存表（不动事实表）。"""
        if all_entries:
            self.conn.execute("DELETE FROM cache")
        else:
            self.conn.execute(
                "DELETE FROM cache WHERE expires_at IS NOT NULL AND expires_at < ?",
                (time.time(),),
            )
        self.conn.commit()

    def export(self, table, out_path=None):
        """导出事实表为 CSV（默认输出到 stdout）。"""
        if table not in ("fixtures", "reports"):
            raise ValueError("仅支持导出 fixtures / reports 事实表")
        rows = self.conn.execute(f"SELECT * FROM {table}").fetchall()
        if not rows:
            return ""
        import io

        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(rows[0].keys())
        for row in rows:
            writer.writerow([row[k] for k in row.keys()])
        text = buf.getvalue()
        if out_path:
            with open(out_path, "w", encoding="utf-8-sig", newline="") as fp:
                fp.write(text)
        return text


def main():
    """命令行入口：供 LLM 直接操作本地库。"""
    parser = argparse.ArgumentParser(description="球小策 Skill 本地数据层（SQLite）")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init", help="初始化本地库（首次运行任意命令也会自动建库）")

    p_get = sub.add_parser("get", help="读取缓存；未命中或过期时退出码为 1")
    p_get.add_argument("--endpoint", required=True)
    p_get.add_argument("--params", default="", help="JSON 字符串，与写入时一致")

    p_set = sub.add_parser("set", help="写入缓存")
    p_set.add_argument("--endpoint", required=True)
    p_set.add_argument("--params", default="")
    p_set.add_argument("--payload", required=True, help="JSON 字符串")
    p_set.add_argument("--ttl", default="auto", help="秒数 / auto / forever")

    p_query = sub.add_parser("query", help="只读 SQL 查询本地库（fixtures / reports / cache）")
    p_query.add_argument("--sql", required=True)

    sub.add_parser("stats", help="库概况")

    p_export = sub.add_parser("export", help="导出事实表为 CSV")
    p_export.add_argument("--table", choices=["fixtures", "reports"], required=True)
    p_export.add_argument("--out", default="", help="输出文件路径，缺省打印到标准输出")

    p_purge = sub.add_parser("purge", help="清理过期缓存")
    p_purge.add_argument("--all", action="store_true", help="清空全部缓存（不动事实表）")

    args = parser.parse_args()
    store = LocalStore()

    if args.command == "init":
        print(json.dumps({"success": True, "db_path": db_path()}, ensure_ascii=False))
        return 0

    if args.command == "get":
        params = json.loads(args.params) if args.params else None
        payload = store.get(args.endpoint, params)
        if payload is None:
            print(json.dumps({"hit": False}, ensure_ascii=False))
            return 1
        print(json.dumps({"hit": True, "payload": payload}, ensure_ascii=False))
        return 0

    if args.command == "set":
        params = json.loads(args.params) if args.params else None
        payload = json.loads(args.payload)
        ttl = args.ttl
        if ttl == "auto":
            ttl_value = "auto"
        elif ttl == "forever":
            ttl_value = None
        else:
            ttl_value = float(ttl)
        store.set(args.endpoint, payload, params, ttl=ttl_value)
        print(json.dumps({"success": True}, ensure_ascii=False))
        return 0

    if args.command == "query":
        try:
            rows = store.query(args.sql)
        except (ValueError, sqlite3.Error) as error:
            print(json.dumps({"error": True, "message": str(error)}, ensure_ascii=False))
            return 1
        print(json.dumps({"rows": rows, "count": len(rows)}, ensure_ascii=False))
        return 0

    if args.command == "stats":
        print(json.dumps(store.stats(), ensure_ascii=False))
        return 0

    if args.command == "export":
        text = store.export(args.table, args.out or None)
        if not args.out:
            print(text)
        else:
            print(json.dumps({"success": True, "out": args.out}, ensure_ascii=False))
        return 0

    if args.command == "purge":
        store.purge(all_entries=args.all)
        print(json.dumps({"success": True}, ensure_ascii=False))
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
