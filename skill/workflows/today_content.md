# 当日赛事与研报（today_content）

## 1. 适用意图与反例

适用：当日/某日赛事总览、彩票编号定位、已发布研报。"今天有什么比赛"、"周四001 是哪场"、"今天的研报"。

不适用：某一场的深度数据（转 match_query）；历史某天研报（用 `/posts?date=`）。

## 2. 参数识别

- "今天/明天/昨晚"换算成 `YYYY-MM-DD`；
- 不给日期默认销售日口径今天（北京时间 11 点日界线，11 点前归属前一天）；
- 用户给了彩票编号 → 目标是定位到 fixture_id 与对应研报，不是总览。

## 3. 取数步骤（本地优先）

1. 赛事总览：`GET /today/digest`（5 点，TTL 6h）。逐场含 `lottery_id`（如「周四001」）、`pack_ready`、`report_status`（published/generatable/unavailable）、`post_id`。
2. 彩票编号定位：在 digest 返回的 `matches` 里匹配 `lottery_id`，拿到 `fixture_id` 后转 `match_query.md`。
3. 研报列表（**高成本，必须用户确认**）：`GET /posts/today` 为按天批发 **1000 点/次**；取全文 `/posts/{id}` 当天 100 点/篇、历史 25 点/篇。调用前必须先向用户说明扣点并获确认。先给标题概览；用户点名某篇再取全文，不无差别拉全文。
4. 落库清单：digest 与 fixtures 响应入本地缓存；研报列表与全文落 `reports` 事实表（query_backtest.py 检索时自动落库；直接 HTTP 取全文后手动 set）。

## 4. 输出规则

- 总览按时间或联赛分组，标注开球时间（北京时间）；
- 每场一行：对阵、时间、联赛、是否有研报（report_status）；
- 先概览后细节，等用户点选；
- 研报 `locked=true` 时如实说明需对应访问资格，不绕过。

## 5. 合规红线

见 SKILL.md 第 6 节。研报是公开来源之一，不表述为官方推荐。

## 6. 完成自检

- [ ] 日期口径（销售日 vs 自然日）向用户说清？
- [ ] 彩票编号已映射到 fixture_id？
- [ ] 研报只读了用户点名的篇目？
