#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检索历史已发布研报及赛后结果，用于历史样本评估。"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE_URL = "https://www.qiuxiaoce.com/wp-json/abv2-creator/v1"
USER_AGENT = "QiuXiaoCe-Skill-Agent/2.4.3"


def get_api_key(cli_key=None):
    """按命令参数、环境变量顺序读取 API Key。"""
    if cli_key:
        return cli_key.strip()
    return os.environ.get("QIUXIAOCE_API_KEY", "").strip() or None


def http_get(endpoint, key, params):
    """发送 GET 请求并返回解析后的 JSON。"""
    url = BASE_URL + endpoint + "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "X-API-Key": key,
        "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="ignore")
        try:
            payload = json.loads(body)
            message = payload.get("message", body)
        except (ValueError, TypeError):
            message = body
        return {"error": True, "status": error.code, "message": message}
    except (urllib.error.URLError, TimeoutError, ValueError) as error:
        return {"error": True, "message": str(error)}


def main():
    """解析参数并执行历史公开记录检索。"""
    parser = argparse.ArgumentParser(description="球小策历史公开研报与赛后结果检索工具")
    parser.add_argument("--key", help="临时 API Key；优先推荐使用 QIUXIAOCE_API_KEY 环境变量")
    parser.add_argument("--search", help="搜索关键词：球队、联赛或标题关键词")
    parser.add_argument("--date", help="日期筛选，格式 YYYY-MM-DD")
    parser.add_argument("--lottery-type", choices=["all", "zucai", "beidan"], default="all", help="研报类型筛选参数")
    parser.add_argument("--page", type=int, default=1, help="页码，默认 1")
    parser.add_argument("--per-page", type=int, default=10, help="每页数量，1-50，默认 10")
    parser.add_argument("--without-settlement", action="store_true", help="不附带赛后结果与结算比对字段")
    args = parser.parse_args()

    key = get_api_key(args.key)
    if not key:
        print(json.dumps({
            "error": True,
            "message": "未检测到 API Key。请在本机安全设置 QIUXIAOCE_API_KEY 环境变量。",
        }, ensure_ascii=False))
        return 1

    params = {
        "page": max(args.page, 1),
        "per_page": min(max(args.per_page, 1), 50),
        "lottery_type": args.lottery_type,
        "with_settlement": 0 if args.without_settlement else 1,
    }
    if args.search:
        params["search"] = args.search.strip()
    if args.date:
        params["date"] = args.date.strip()

    response = http_get("/posts", key, params)
    print(json.dumps(response, ensure_ascii=False, indent=2))
    return 1 if isinstance(response, dict) and response.get("error") else 0


if __name__ == "__main__":
    sys.exit(main())
