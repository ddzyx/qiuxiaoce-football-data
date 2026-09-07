# 单场比赛（match_query）

## 1. 适用意图与反例

适用：用户点名某场比赛，要看数据、前瞻、或生成分析报告。"皇马这场怎么看"、"帮我分析明晚曼城"、"给我一份曼联那场的赛前报告"。

不适用：积分榜/射手榜/赛季统计（直接调 standings、topscorers 等，见 `references/api_endpoints.md`）；"今天有什么比赛"（走 today_content）。

## 2. 参数识别

需要两个参数：**日期**（默认北京时间今天）和**球队**（双方或至少一方）。

- 用户同时给了双方队名 + 日期 → 直接定位，不追问；
- 只给一方 → 用「同队同日最多一场」原则定位，不追问；
- 只给彩票编号（"周四001"）→ 走 today_content 的 digest 匹配 `lottery_id`；
- 完全无定位线索（"今晚那场德比"且当夜确有多场）→ 追问，一次问全。

## 3. 取数步骤（本地优先）

1. 定位比赛：`python scripts/fetch_match.py --date <YYYY-MM-DD>`（可加 `--team 名称` 预筛），从返回中取 `fixture_id`。脚本自动走本地缓存，命中不扣点。
2. 取全景数据：`python scripts/fetch_match.py --pack <fixture_id>`（50 点；TTL 2h 内重取命中本地）。这是主力数据源，覆盖近期战绩/赛季统计/高阶/H2H/伤停/教练。
3. 检查 `meta.source`：`pipeline` 字段完整；`realtime` 是实时组装，回复时说明覆盖较少。
4. 按需补充（不要默认全调）：
   - 用户提到市场变化 → `GET /fixtures/{id}/quotes`（5 点）；
   - 要阵容细节 → `GET /fixtures/{id}/lineups`（5 点）；
   - 已完赛要技术统计/事件 → `GET /fixtures/{id}/stats|events|players`（各 5 点）。
5. 落库清单：赛程与 pack 基础信息已由脚本自动落 `fixtures` 事实表；直接 HTTP 拿到的完赛数据（stats/events/players）手动落库：`python scripts/local_store.py set --endpoint "/fixtures/{id}/stats" --payload '...' --ttl forever`。

## 4. 输出规则

- 用户只要数据 → 直接给结构化数据（表格优先）；
- 用户要分析/预测报告 → 加载 `prompts/simple_match_brief.md`，把取到的数据作为输入，按其骨架生成；
- 用户要成稿 → 转 `content_creation.md`；
- 事实（赛程/伤停/战绩）与模型判断（倾向/评估）分层表述。

## 5. 合规红线

见 SKILL.md 第 6 节。市场参考值只用合规词；不输出投注建议。

## 6. 完成自检

- [ ] fixture_id 来自接口而非猜测？
- [ ] pack 数据命中本地时向用户说明数据时点？
- [ ] 缺失维度已注明？
