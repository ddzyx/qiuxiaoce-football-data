# 内容创作（content_creation）

## 适用意图

用户要基于球小策数据产出内容：文章、短视频脚本、简报、提示词等。

## 模板路由

根据用户要的成品类型加载对应模板，不要一次加载全部：

| 用户要的东西 | 加载文件 |
|:---|:---|
| 战术与赛前资料整理 | `templates/template_tactical.md` |
| 短视频信息脚本 | `templates/template_video.md` |
| 公众号或专栏文章 | `templates/template_article.md` |
| 社群赛事简报 | `templates/template_bulletin.md` |
| 历史样本评估报告 | `templates/template_backtest.md` |
| 定制专属分析提示词 | `prompts/prompt_optimizer.md` |

## 执行步骤

1. 识别成品类型，加载对应模板；
2. 识别内容涉及的比赛或主题：
   - 具体某场 → 按 `match_query.md` 获取 Match-Pack；
   - 当日综述类 → 按 `today_content.md` 获取摘要与研报；
   - 复盘类 → 按 `backtest.md` 获取历史样本；
3. 按模板结构组织内容，只使用接口实际返回的数据；
4. 完稿检查：
   - 区分事实、预测字段、衍生评分；
   - 无博彩黑话、无煽动性话术、无结果承诺；
   - 文末附来源声明（见 SKILL.md 公共约定）；
5. 输出前向用户说明数据日期与缺失字段。

## 注意

- 模板是结构框架，不是填空模具；根据实际数据丰俭调整篇幅；
- 用户要自己风格的提示词时，走 `prompts/prompt_optimizer.md`，不直接替用户发明规则。
