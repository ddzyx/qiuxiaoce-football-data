# 当日赛事与已发布研报（today_content）

## 适用意图

用户想知道当日赛事全貌或已发布的公开研报：

- "今天有什么比赛" / "今日赛程" / "今天竞彩有哪些场次" → 赛事摘要；
- "今天的研报" / "已发布的分析" / "看看你们发的文章" → 已发布内容。

## 参数识别（LLM 执行）

- "今天 / 明天 / 昨晚"等相对日期换算成具体日期；
- 用户提到具体球队时，记录球队名（归一化规则见 `match_query.md`），用于从结果中筛选重点场次。

## 执行步骤

### A. 当日赛事摘要

无专用脚本，使用直接 HTTP：

```bash
curl -s -H "X-API-Key: $QIUXIAOCE_API_KEY" \
  "https://www.qiuxiaoce.com/wp-json/abv2-creator/v1/today/digest"
```

- 该接口为销售日口径（竞彩跨零点），直接按返回结构整理即可；
- 用户想深入某一场时，转 `match_query.md` 流程。

### B. 已发布研报

```bash
curl -s -H "X-API-Key: $QIUXIAOCE_API_KEY" \
  "https://www.qiuxiaoce.com/wp-json/abv2-creator/v1/posts/today"
```

1. 先拉列表，向用户概括标题与对应比赛；
2. 用户点名某篇时再调用 `GET /posts/{post_id}` 取全文，不无差别拉取全部文章；
3. 受会员权限保护的内容可能返回 `403 subscription_required`，如实说明所需访问资格，不绕过权限；
4. 引用研报时做摘要和归纳，不整篇搬运原文。

## 输出要求

- 按时间或联赛分组呈现，标注比赛时间（默认北京时间）；
- 区分事实信息与研报中的预测字段；
- 列表类输出控制长度，先给概览，等用户点选再给细节。
