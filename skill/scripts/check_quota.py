#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""查询当前 API Key 的点数余额、有效期与调用限制。"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

BASE_URL = "https://www.qiuxiaoce.com/wp-json/abv2-creator/v1"
USER_AGENT = "QiuXiaoCe-Skill-Agent/2.4.3"


def get_api_key(cli_key=None):
    """按命令参数、环境变量顺序读取 API Key。"""
    if cli_key:
        return cli_key.strip()
    return os.environ.get("QIUXIAOCE_API_KEY", "").strip() or None


def main():
    """执行余额自查并输出结构化 JSON。"""
    parser = argparse.ArgumentParser(description="球小策 API Key 余额与调用限制查询工具")
    parser.add_argument("--key", help="临时 API Key；优先推荐使用 QIUXIAOCE_API_KEY 环境变量")
    args = parser.parse_args()

    key = get_api_key(args.key)
    if not key:
        print(json.dumps({
            "error": True,
            "message": "未检测到 API Key。请在本机安全设置 QIUXIAOCE_API_KEY 环境变量。",
        }, ensure_ascii=False))
        return 1

    request = urllib.request.Request(BASE_URL + "/quota", headers={
        "User-Agent": USER_AGENT,
        "X-API-Key": key,
        "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            print(json.dumps(json.loads(response.read().decode("utf-8")), ensure_ascii=False, indent=2))
            return 0
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="ignore")
        try:
            payload = json.loads(body)
            message = payload.get("message", body)
        except (ValueError, TypeError):
            message = body
        print(json.dumps({"error": True, "status": error.code, "message": message}, ensure_ascii=False, indent=2))
        return 1
    except (urllib.error.URLError, TimeoutError, ValueError) as error:
        print(json.dumps({"error": True, "message": str(error)}, ensure_ascii=False, indent=2))
        return 1


if __name__ == "__main__":
    sys.exit(main())
