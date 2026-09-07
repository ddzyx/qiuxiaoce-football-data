# 内容创作（content_creation）

## 1. 适用意图与反例

适用：基于数据产出可发布内容——文章、短视频脚本、社群简报、复盘报告、定制提示词。"写一篇公众号"、"做个短视频脚本"、"给我今天的赛事简报"。

不适用：只要数据事实（直接答，不套模板）；极简赛前分析报告（走 match_query + simple_match_brief.md）。

## 2. 参数识别

确认两件事（缺则一次问全）：
1. **成品类型**：文章 / 视频脚本 / 简报 / 复盘报告 / 提示词；
2. **内容范围**：具体某场 / 当日综述 / 某主题复盘。

## 3. 取数步骤（本地优先）

| 内容范围 | 取数路径 |
|:---|:---|
| 具体某场 | match_query.md 取 Match-Pack（50 点） |
| 当日综述 | today_content.md 取 digest（5 点） |
| 复盘类 | backtest.md 取历史样本 |

数据先于模板：先拿到数据，确认数据量够支撑成品类型，再加载模板。

## 4. 模板路由（按需加载一个）

| 成品 | 加载文件 |
|:---|:---|
| 公众号/专栏文章 | `templates/template_article.md` |
| 短视频脚本 | `templates/template_video.md` |
| 社群简报 | `templates/template_bulletin.md` |
| 战术资料整理 | `templates/template_tactical.md` |
| 复盘报告 | `templates/template_backtest.md` |
| 定制分析提示词 | `prompts/prompt_optimizer.md` |

模板是结构框架不是填空模具，按数据丰俭调整篇幅。

## 5. 合规红线

见 SKILL.md 第 6 节。额外：无煽动性话术、无红黑榜、无结果承诺；文末附来源声明。

## 6. 完成自检

- [ ] 只使用了接口实际返回的数据？
- [ ] 事实 / 预测字段 / 衍生评分已区分？
- [ ] 来源声明已附？
- [ ] 数据日期与缺失字段已向用户说明？
