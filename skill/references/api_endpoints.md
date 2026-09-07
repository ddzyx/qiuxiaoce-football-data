# 球小策数据接口决策手册（api_endpoints）

本文件是 Skill 调用数据接口的**唯一完整清单**，按「用户意图 → 调用链」组织。使用时按标题检索定位到需要的场景或端点，不要把整份文件载入上下文。

> 版本：v2.6.0 ｜ 点数：1 元 = 100 点（后台可调，以 `/quota` 实测为准）｜ Base URL：`https://www.qiuxiaoce.com/wp-json/abv2-creator/v1`

---

## 第 0 章 通用规则（每次调用前必读）

- 认证：请求头 `X-API-Key: <密钥>`，密钥从环境变量 `QIUXIAOCE_API_KEY` 读取，禁止回显。
- **本地优先**：调接口前先查本地库 `scripts/local_store.py`；TTL 内命中直接用，不扣点。接口拿到的重要数据必须落库（落库清单见各端点「落库」栏）。
- 去重：60 秒内相同请求服务端不重复扣点（响应头 `X-Dedup-Hit: 1`）。
- 限流：默认 30 次/分钟。
- ID 驱动：球队/联赛/球员/比赛一律用数字 ID；用户给名字先搜索解析（见第 1 章），禁止凭名称猜 ID。
- 成功响应含 `success/data/note`；`note` 非空时如实转告用户，不得补造缺失字段。
- **赛季口径**：跨年联赛存起始年（2026/27 → `2026`）；联赛类接口（fixtures/topscorers/topassists/standings/league detail 附积分榜）均支持 `season` 参数，缺省自动取库内最新赛季。多赛季数据需求务必显式传 season。
- 合规：对用户只说「市场参考值 / 胜平负参考 / 让球参考 / 进球数参考」，禁用赔率、盘口、盯盘、庄家、资金流、诱导、投注、稳胆。
- 不开放：第三方投注预测（/predictions）、奖杯、场馆。

---

## 第 1 章 实体解析（所有场景的前置）

用户输入是乱七八糟的中文：绰号、简称、英文名、错别字、彩票编号。解析规则：

| 用户给了 | 解析方式 | 点数 |
|:---|:---|:---:|
| 球队名/绰号/简称 | `GET /teams?q=名称` | 2 |
| 球员名 | `GET /players?q=名称`（至少 2 字） | 2 |
| 联赛名 | `GET /leagues?q=名称` | 2 |
| 裁判英文名 | `GET /referees?q=Taylor` | 2 |
| 彩票编号（如「周四001」） | `GET /today/digest` 在返回场次里匹配 `lottery_id`；历史日期用 `GET /fixtures?date=YYYY-MM-DD` 匹配 `lottery_code` | 5 / 2 |
| 「今晚那场」「明天曼联」 | 先归一化日期与队名，再按上表解析 | — |

- 搜索返回多候选时，**列出候选让用户选**，不要替用户猜。
- 解析不到中文名时用英文名继续，并标注「该名称暂无中文译名」。
- 解析结果（ID 与名称对应关系）可记入本地库备注，后续复用。

---

## 第 2 章 意图场景速查表

| 用户意图 | 调用链 | 总点数参考 |
|:---|:---|:---:|
| 今天/明天有什么比赛 | `/fixtures?date=` 或 `/today/digest` | 2 / 5 |
| 这场怎么看（单场前瞻） | 解析 → `/match-pack/{id}`（50）→ 可选 `/fixtures/{id}/quotes`（5） | 50-55 |
| 某队最近战绩/状态 | 解析 → `/teams/{id}/form` | 7 |
| 某队整个赛季赛果 | 解析 → `/teams/{id}/fixtures?season=` | 5 |
| 两队交锋 | 解析 → `/h2h?home_id=&away_id=` | 9 |
| 积分榜/射手榜/助攻榜（任意赛季） | 解析联赛 → `/standings` 或 `/leagues/{id}/topscorers|topassists?season=` | 5-7 |
| 伤停 | 解析 → `/teams/{id}/injuries` | 7 |
| 完赛那场的技术统计/事件/阵容/球员评分 | `/fixtures/{id}/stats|events|lineups|players` | 5 |
| 市场参考值/怎么变 | `/fixtures/{id}/quotes`（快照）`/quotes/history`（走势）`/market`（异动） | 5 |
| 某队/某球员转会 | 解析 → `/transfers?team=` 或 `?player=` | 7 |
| 教练是谁/履历 | `/teams/{id}/coach`（现任）→ `/coaches/{id}`（完整履历） | 6 |
| 这场谁执法/裁判风格 | `/fixtures/{id}` 取 referee 名 → `/referees?q=` → `/referees/{id}` | 7 |
| 今天官方研报 | `/posts/today`，点名某篇再 `/posts/{id}` | 1000/批发、25-100/篇 |
| 最近准不准 | `/review`（10）或 `/stats/overall`（5） | 5-10 |
| 我买过/查过的数据分析 | 本地库：`local_store.py query --sql ...` | 0 |
| 还剩多少点 | `scripts/check_quota.py` | 0 |

---

## 第 3 章 端点详情（含返回字段清单）

> 字段清单供「组合多个接口数据 / 只取某字段」场景使用。所有端点外层都有 `success`；空数据时 `note` 给中文提示。球队/联赛/球员名统一「中文别名兜底英文」。

### 3.1 赛程

**GET /fixtures（2 点）** — 比赛日程。至少给一种定位，全空默认北京时间当天。落库：`fixtures` 事实表（fetch_match.py 已自动落库）。
- 参数：`id` 单场直达 / `date` 单日 / `from`+`to` 区间（≤31 天）/ `league` / `season` / `team`（主客皆可）/ `round`（如 `Regular Season - 12`）/ `status`（NS/FT/LIVE/FINISHED…）/ `last`（最近完赛 N 场）/ `next`（未来 N 场）/ `lottery_type`（all/zucai/beidan）/ `limit`（≤50）/ `offset`（≤2000）。
- 返回：`total/count/filters` + `data[]`：
  - `fixture_id`：比赛 ID，贯穿所有 /fixtures/{id} 子端点
  - `timestamp`/`date`：开球时间（Unix / ISO）
  - `season`/`round`/`status`/`status_zh`：赛季、轮次、状态码与中文
  - `home_team_id`/`home_team_name`/`home_team_en`/`home_team_logo`（客队同组 `away_*`）
  - `home_goals`/`away_goals`：全场比分；`ht_home`/`ht_away`：半场
  - `league_id`/`league_name`/`league_type`/`league_logo`
  - `lottery_code`：竞彩编号；`lottery_code_beidan`：北单编号
  - `lottery_total_goals_odds`：竞彩官方总进球玩法参考值图（8 档，可能为 null）

**GET /fixtures/{id}（2 点）** — 单场详情。
- 返回 `data`：`fixture_id/timestamp/date/season/round/status`；`venue_name` 球场；`referee` 主裁判名（查裁判数据的第一步）；`league_id/league_name/league_logo`；主客队 `home_team_id/home_team/home_team_logo`（客队同组）；`goals` 四段比分 `{halftime, fulltime, extratime, penalty}` 各 `{home, away}`。

**GET /fixtures/{id}/stats（5 点）** — 单场技术统计。
- 返回：外层 `fixture`（基础信息块，所有 /fixtures/{id}/* 子端点同结构：`fixture_id/timestamp/date/status/league_id/league_name/venue_name/referee/双方 team_id+team_name/home_goals/away_goals`）；`data[]` 按队分组 `{team_id, stats}`，`stats` 为 `{统计项名: 值}` 键值对（控球率/射门/射正/角球/xG 等，键名随数据源）。

**GET /fixtures/{id}/events（5 点）** — 事件流（时间升序）。
- `data[]`：`minute`/`extra`（补时）、`team_id`、`player_id`/`assist_id`、`type`（Goal/Card/subst/Var）、`detail`（子类型如 Normal Goal/Yellow Card）、`comments`。

**GET /fixtures/{id}/lineups（5 点）** — 官方阵容。
- `data[]` 按队：`team_id`、`formation`（如 4-3-3）、`coach_name`、`starters[]`/`bench[]`（每名 `{player_id, player_name, number, position, grid(站位坐标)}`）。

**GET /fixtures/{id}/players（5 点）** — 球员逐场统计。
- `data[]` 按队 `{team_id, players[]}`；每名：`player_id`/`player_name`（中文化时附 `player_name_en`）/`position`/`number`、`minutes`/`rating`/`captain`/`substitute`、`goals`/`assists`、`shots{total,on}`、`passes{total,accuracy}`、`cards{yellow,red}`。

**GET /today/digest（5 点）** — 当天竞彩/北单总览（北京时间 11 点日界线，11 点前归前一天；可用 `date` 覆盖）。
- 返回：`date`/`total`；`summary{published, generatable, pack_ready}`；`matches[]`（开球升序，≤200 场）：
  - `fixture_id`/`kickoff`/`status`/`status_zh`、`league_id`/`league_name`、双方队名+logo
  - `lottery_code`/`lottery_code_beidan`：竞彩/北单编号；`lottery_id`：展示编号（如「周四001」，**定位编号场次唯一入口**）
  - `pack_ready`/`pack_source`（pipeline/realtime）：match-pack 是否就绪
  - `report_status`（published/generatable/unavailable）、`post_id`（已发布文章 ID）
  - `is_paid`/`locked`：付费场次与当前 Key 权限标记
  - `score{home, away}`：已完赛比分

### 3.2 单场全景（旗舰）

**GET /match-pack/{fixture_id}（50 点）** — 一次覆盖赛前分析全部维度。用户说「这场怎么看」就用它，不要拆 8 次零散请求。**不含市场参考值**，需要时另调 quotes。落库：pack 进缓存（TTL 2h）。
- 外层：`fixture_id`、`meta{source(pipeline 完整/realtime 实时组装), generated_at, lottery_type, lottery_id}`、`pack`。
- `pack` 顶层键：`league_id/league_name/kickoff/venue_name/referee`、双方 `home_team_id/home_name`（客队同组）、`home_form/away_form`（同 3.3 form 结构）、`home_stats/away_stats`（同 statistics 单行）、`home_advanced/away_advanced`（同 advanced）、`h2h`（同 /h2h data）、`home_injuries/away_injuries`、`home_coach/away_coach`、`calculated_metrics{home_xg_per_game, home_xga_per_game, away_xg_per_game, away_xga_per_game, xg_diff_avg}`；pipeline 包另有预测首发/加权状态/战术指纹等独家字段。

### 3.3 球队

| 端点 | 点数 | 说明 |
|:---|:---:|:---|
| GET /teams?q= | 2 | 搜索，返回 `team_id/name_en/name_zh/logo_url/country/national` |
| GET /teams/{id} | 2 | 详情：`code`(三字码)/`country`/`founded`/`national`/`venue_name`/`venue_city`/`venue_capacity` |
| GET /teams/{id}/form?last=10 | 5 | 近 N 场（1-20）：`summary{W,D,L}` + `matches[]{fixture_id,date,league_name,is_home,opponent,goals_for,goals_against,result}` |
| GET /teams/{id}/fixtures | 3 | 逐场赛程历史：season/status(finished/upcoming/all)/league_id/limit≤50/offset≤1000；行含 `is_home/halftime/result` |
| GET /teams/{id}/statistics?season= | 5 | 赛季统计按联赛行：`matches/wins/losses/goals_for/goals_against`（各 `{total,home,away}`）、场均进失球、`clean_sheets`/`failed_to_score`、最长连胜平负、最大比分胜负 |
| GET /teams/{id}/advanced?season= | 10 | 高阶画像：`expected_goals{xg,xg_conceded,xg_difference}`、`attack{goals_per_match,shots_on_target_per_match,big_chances,big_chances_missed,touches_in_opposition_box,corners,set_piece_goals,penalties_awarded}`、`defense{...}`、`possession{average_possession,accurate_passes_per_match,...}`、`discipline{fouls_per_match,yellow_cards,red_cards}`、`formation`/`recent_form`/`fotmob_rating`/`market_value`/`league_position` |
| GET /teams/{id}/injuries | 5 | 当前伤停（TTL 6h）：`sync_date` + `injuries[]{player_name, injury_type, expected_return, is_doubtful}` |
| GET /teams/{id}/squad | 3 | 阵容大名单（数据源原结构，球员名已中文化） |
| GET /teams/{id}/coach | 3 | 现任教练：`coach_id`（查 /coaches/{id} 的钥匙）/`name`/`nationality`/`age`/`preferred_formation`/`start_date` |
| GET /teams/{id}/players-advanced?limit=&season= | 10 | 队内球员高阶 TOP（OTI 降序）：`advanced{npxg,xa,xg_chain,xg_buildup,sca90}`、`ratings{oti,dii,gim}`、`form{form_rating,form_trend,form_matches}`、`consistency_score`、`fatigue{fatigue_load,fatigue_risk,minutes_21d}`、`is_estimated` |
| GET /h2h?home_id=&away_id=&limit= | 5 | 交锋：`summary{games,home_wins,draws,away_wins,goals_home,goals_away,avg_goals,btts_count,over25_count,under25_count,metrics_games}` + `matches[]` 逐场 |

### 3.4 联赛（均支持 season 参数，缺省取库内最新赛季）

| 端点 | 点数 | 说明 |
|:---|:---:|:---|
| GET /leagues?q=/country=/type= | 2 | 列表/搜索：`league_id/name_en/name_zh/type/country/logo_url` |
| GET /leagues/{id}?with_standings=&season= | 3 | 详情；`with_standings=1` 附 standings（同 /standings data） |
| GET /leagues/{id}/teams?season= | 2 | 参赛球队：`team_id/name_en/name_zh/country/national/venue_*/logo_url` |
| GET /leagues/{id}/seasons | 1 | 赛季列表：`season/start/end/is_current`（不确定赛季口径时先查） |
| GET /leagues/{id}/fixtures?season=&round=&limit=&offset= | 5 | 赛季逐场（升序）：`fixture_id/date/round/双方队名/home_goals/away_goals/status`，外层回显 `season/total` |
| GET /leagues/{id}/topscorers?season=&limit= | 5 | 射手榜：`rank/player_id/player_name/team_id/team_name/appearances/minutes/rating/goals/assists/penalties` |
| GET /leagues/{id}/topassists?season=&limit= | 5 | 助攻榜：字段同射手榜，按 assists 排序 |
| GET /standings?league=&season= | 3 | 积分榜：`rank/team_id/team_name/team_logo/points/matches_played/wins/draws/losses/goals_for/goals_against/goals_diff`，外层回显实际 `season` |

### 3.5 球员

| 端点 | 点数 | 说明 |
|:---|:---:|:---|
| GET /players?q= | 2 | 搜索（≥2 字）：`player_id/name/name_zh/nationality/age/photo` |
| GET /players/{id} | 2 | 详情：`firstname/lastname/nationality/birth_date/age/height_cm/weight_kg/photo` + `current_team{team_id,team_name,season,shirt_number}` |
| GET /players/{id}/stats?season= | 3 | 赛季统计按 球队×联赛 行：`appearances/minutes/rating/goals/assists/shots{total,on_target}/passes{total,accuracy_pct}/dribbles{attempts,success}/duels{total,won}/tackles/interceptions/cards{yellow,red}/penalties{scored,missed,saved}` |
| GET /players/{id}/advanced?season= | 10 | 高阶指标：结构同 players-advanced 单人（npxG/xA/OTI/疲劳等 8 维） |

### 3.6 转会（v2.6.0 新增）

**GET /transfers（5 点）** — `team` / `player` 二选一必填；limit≤100、offset≤500。
- 返回：外层 `team/player/total/count`；`data[]`（日期倒序）：
  - `player_id`/`player_name`（中文兜底）、`date`、`type`（费用原值，如 `€90M`/`Free`/`Loan`/`Free agent`）、`season`（欧洲赛季口径）
  - `direction`（仅 team 模式）：`in`=转入该队 / `out`=从该队转出
  - `team_in{team_id, team_name, team_logo}`、`team_out{...}`（转入/转出方）
- 覆盖范围：在库白名单赛事相关球队；数据源仅覆盖职业队主流转会，远古/低级别记录可能缺失。

### 3.7 人物（教练 / 裁判，v2.6.0 新增）

**GET /coaches/{id}（3 点）** — 教练详情 + 执教履历。coach_id 来自 `/teams/{id}/coach`。
- 返回 `data`：`coach_id/name/firstname/lastname/nationality/birth_date/age/photo/preferred_formation` + `career[]`（上任日期倒序，≤50 条）：`team_id/team_name/team_logo/league_id/league_name/season/start_date/end_date/is_current`（现任 `end_date=null`）。

**GET /referees?q=（2 点）** — 裁判搜索（英文姓名，≥2 字）。返回 `referee_id/name/nationality/age/photo`。

**GET /referees/{id}（3 点）** — 裁判详情 + 执法数据。
- 返回 `data`：档案字段同搜索 + `career{matches, yellow_cards, red_cards, second_yellow, avg_yellow, avg_red}`（在库赛事实时聚合）+ `recent_matches[]`（最近 10 场：`fixture_id/date/league_name/home_team/away_team/home_goals/away_goals/status`）+ `stats`（预聚合指标，未生成时为 null）。
- 用法：从 `/fixtures/{id}` 的 `referee` 拿到姓名 → `/referees?q=` 解析 ID → 本端点。注意 fixtures 中裁判是姓名字符串，同名裁判理论上有歧义。

### 3.8 市场参考值（合规口径）

| 端点 | 点数 | 说明 |
|:---|:---:|:---|
| GET /fixtures/{id}/quotes?group= | 5 | 当前快照。group：result 胜平负参考 / spread 让球参考 / totals 进球数参考 / both_teams / score / halftime / all（默认主流六类） |
| GET /fixtures/{id}/quotes/history?group=&limit= | 5 | 时间序列（新→旧，≤200），含 `is_open`/`is_close` 开收盘标记 |
| GET /fixtures/{id}/market?limit= | 5 | 已识别的异动事件流：`market_type/event_type/old_value/new_value/velocity/change_time/description` |

- quotes 返回两块：`quotes{bookmaker, count, items[]{group, label, option, value, updated}}`（外部数据公司快照，option 已合规化：「主队/客队/平局」「高于/低于 2.5」）；`official`（竞彩官方公开参考值，按玩法中文标签分组，每项 `{option, value}`，可能为空）。TTL 30 分钟。

### 3.9 研报（已发布内容）

> **高成本确认（强制）**：本组接口单次 25-1000 点，调用前必须先向用户说明扣点金额并得到确认，未确认不得调用。

| 端点 | 点数 | 说明 |
|:---|:---:|:---|
| GET /posts?date=&search=&lottery_type=&with_settlement=1&per_page=&page= | 1000/次 | 按天批发摘要；with_settlement 附带回测字段 |
| GET /posts/today?date=&lottery_type= | 1000/次 | 当天研报（销售日口径），字段同 /posts |
| GET /posts/{id} | 历史 25 / 当天 100 | 全文 + `ai_prediction`（清洗后） |

- 摘要行字段：`id/title/date/modified/author/thumbnail/url/excerpt` + `match{home_team, away_team, 双方 id+logo+英文名, league_type, match_number, kickoff, actual_score, half_score, is_correct, result_text, is_perfect, hit_score, hit_goals, hit_htft, hit_direction, hit_items, manual_wrong}` + `recommendation/recommendation_text` + `highlight` + `is_paid/locked`；`with_settlement=1` 加 `backtest{actual_score, is_correct, is_correct_text, hit_items, predicted_direction, predicted_scores}`。
- `/posts/{id}` 另含：`content_html/content_text/categories[]/tags[]/lottery_id/lottery_type` + `ai_prediction`（剥离市场参考值类键后的预测 JSON；常见键 `predictions.spf.direction`、`predictions.rqspf`、`predictions.totalGoals`、`predictions.scores`、`predictions.htft`）。
- 研报是公开来源之一，不得表述为官方推荐或确定结果。落库：`reports` 事实表（query_backtest.py 自动落摘要）。

### 3.10 复盘与统计

| 端点 | 点数 | 说明 |
|:---|:---:|:---|
| GET /stats/overall | 5 | 整体命中率快照（官网历史样本，不代表用户调用结果）：`stats{total,correct,wrong,accuracy,details{score,goals,htft,direction,perfect}}`、`high_rec`（高推荐度子集）、`chart{labels,data}`（近 10 天走势）、`rankings.leagues[]/teams[]` |
| GET /stats/team?name= | 5 | 某队历史研报命中情况：`found/stats{同 overall 结构}/history[]`（最近 5 场明细） |
| GET /review?days=7 | 10 | 近 N 天聚合（1-30）：`overall` + `daily[]{date,total,correct,accuracy,details}`，替代逐日拉取 |

### 3.11 账户与工具

| 端点 | 点数 | 说明 |
|:---|:---:|:---|
| GET /quota | 0 | `credits{remaining, expires_at, days_left, today_used}`、`limits{rate_per_minute, dedup_window_seconds}`、`recharge_url`（不缓存） |
| GET /skill/version · /skill/download | 免 Key | Skill 更新（走 update_skill.py，勿直接调） |

---

## 第 4 章 本地数据层（SQLite）

库文件：`data/qiuxiaoce_local.db`（首次运行自动创建；Skill 更新不覆盖）。

**哪些数据必须落库**：

| 数据 | 表 | 保留策略 |
|:---|:---|:---|
| 赛程与赛果（/fixtures、match-pack 基础信息） | `fixtures` 事实表 | 永久 |
| 研报摘要与已购全文 | `reports` 事实表 | 永久 |
| match-pack / 伤停 / quotes / 赛程列表等响应 | `cache` 表 | TTL：pack 2h、伤停 6h、quotes 30min、其余 12-24h |

**LLM 直接用本地库做分析**（0 点）：

```bash
python scripts/local_store.py query --sql "SELECT date, home_team, away_team, home_goals, away_goals FROM fixtures WHERE status='FT' ORDER BY date DESC LIMIT 20"
python scripts/local_store.py stats
python scripts/local_store.py export --table fixtures --out fixtures.csv
```

- 用户问「我之前查过的」「我买过的研报」一律先查本地库，不调接口。
- query 仅允许 SELECT。
- 库内不存 API Key。

---

## 第 5 章 维护规则（改接口必同步）

1. 新增数据端点：本文件加条目（场景表 + 详情 + 落库规则）；`class-key-manager.php` 的 `default_endpoint_config()` 登记权重；`api_schema.json` 加 path。三处同步。
2. 改参数/返回字段：只改对应小节。
3. 改价：只改点数数字。
4. 投注建议类接口即使库内有数据也不写进本文件。
5. SKILL.md 只保留路由与原则，端点细节以本文件为准。
