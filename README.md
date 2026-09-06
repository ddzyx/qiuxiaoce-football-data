# 球小策 · 足球赛事量化分析数据集与 AI 智能体 Skill (QiuXiaoCe Football Data & Agent Skill)

<p align="center">
  <a href="https://www.qiuxiaoce.com"><img src="https://img.shields.io/badge/官网-球小策官方数据中心-07C160?style=for-the-badge&logo=googlechrome&logoColor=white" alt="球小策官网" /></a>
  <a href="https://www.qiuxiaoce.com/data-account/"><img src="https://img.shields.io/badge/API开放平台-免费领取Key-FF8800?style=for-the-badge&logo=fastapi&logoColor=white" alt="创作者API" /></a>
  <a href="https://creativecommons.org/licenses/by-nc/4.0/"><img src="https://img.shields.io/badge/License-CC--BY--NC%204.0-blue?style=for-the-badge" alt="License" /></a>
  <img src="https://img.shields.io/badge/数据更新-赛前每日更新-green?style=for-the-badge&logo=git&logoColor=white" alt="Daily Update" />
  <img src="https://img.shields.io/badge/支持生态-Cursor%20|%20Claude%20|%20Python-purple?style=for-the-badge" alt="AI Ecosystem" />
</p>

> **球小策 (QiuXiaoCe)** 官方开源项目：聚合每日足球赛事（竞彩、北单、五大联赛、欧冠等）的**结构化赛前量化分析数据包、AI 预测模型推演结果与赛后真实比分比对**。同时内置官方 **创作者 API 专属 AI 智能体 Skill**，支持在 Cursor、Claude Desktop、Dify、Coze、Python 等环境中一键调用，赋能足球自媒体、数据分析师与赛事量化研究者。

---

## 📌 快速导航与核心入口

| 模块名称 | 功能描述 | 官方直达链接 |
| :--- | :--- | :--- |
| 🏠 **官方数据看板** | 足球赛事前瞻、AI 智能分析与足球高阶数据解读主站 | [访问球小策官网 (qiuxiaoce.com)](https://www.qiuxiaoce.com/) |
| 📊 **今日赛事前瞻** | 当日焦点对决深度拆解、首发阵容、伤停影响与指数推演 | [查看今日赛事前瞻](https://www.qiuxiaoce.com/sai-shi-qian-zhan/) |
| 📋 **每日赛事复盘日报** | 每日全量比赛预测命中统计、赛果复盘与多维度数据总结 | [查阅每日复盘报告](https://www.qiuxiaoce.com/mei-ri-bao-gao/) |
| ⚽ **实时赛程与比赛列表** | 全网主流联赛实时对阵、开赛时间与比赛编号清单 | [查看实时赛程列表](https://www.qiuxiaoce.com/bi-sai-lie-biao/) |
| 🏃 **球员数据排行榜** | 球员级高阶统计：xG 预期进球、关键传球、绝佳机会与评分榜 | [查看球员数据中心](https://www.qiuxiaoce.com/player-rankings/) |
| 🔑 **创作者 API 开放平台** | 免费注册领取 API Key，获取单场 Match-Pack 与结构化数据接口 | [进入开放平台与控制台](https://www.qiuxiaoce.com/data-account/) |
| ❓ **量化赛事问答 QA** | 热门焦点战战术疑问、冷门预警、市场背离问答看板 | [查看量化问答看板](https://www.qiuxiaoce.com/q-and-a/) |

---

## 💡 为什么关注这个开源项目？

1. **真实数据，拒绝马后炮**：
   - 每一场赛前分析在开赛前数小时固化生成并自动推送到本 Git 仓库；
   - 赛后自动比对官方真实比分（全场比分、半场比分、胜平负结果），历史样本全部公开可追溯、不可篡改；
2. **200+ 维度的深层量化特征**：
   - 告别简单主客胜负，每场比赛生成覆盖 **预期进球 (xG)、射正期望、伤停阵容折损权重、历史 H2H 双向对战、市场观点离散度、指数异动追踪** 的结构化数据包；
3. **大模型五维交叉仲裁引擎**：
   - **硬实力引擎**：基于 xG、绝佳机会、积分榜测算理论实力分差；
   - **市场引擎**：基于成交热度与机构数据离散度识别异常信号；
   - **情报引擎**：核心球员伤停、体能周期与赛程密度拥有一票否决权；
   - **概率引擎**：泊松分布 + 蒙特卡洛随机模拟全场比分概率矩阵；
   - **终局仲裁**：解决各引擎冲突，输出客观、理性的赛前分析报告。
4. **开箱即用的 AI Agent 智能体技能 (Skill)**：
   - 无论您使用 Cursor、Claude Desktop、CodeBuddy 还是自有 Python 程序，都能直接加载本仓库自带的 `skill/`，自然语言即可调取最新比赛数据、生成自媒体短视频脚本与公众号赛前长文！

---

## 🚀 创作者 API 与 AI 智能体 Skill (开箱即用)

本仓库内置了球小策官方 **AI 智能体 Skill (`qiuxiaoce-football-data`)**，位于根目录的 `skill/` 与 `SKILL.md`。

### 1. Skill 核心能力
- **查比赛 / 赛前数据**：输入“皇马明晚比赛数据”、“曼城vs阿森纳”，自动调用 Match-Pack 接口获取全维度战术指纹与伤停评分；
- **当日赛事总览**：输入“今天有什么比赛”、“今日已发布研报”，秒级拉取赛程快报；
- **历史复盘验证**：输入“最近命中率如何”、“查看历史样本”，查询公开比赛预测与实际赛果比对；
- **自媒体内容创作**：输入“帮我把今晚国米这场写成一篇公众号前瞻”、“生成抖音60秒短视频解说脚本”，自动按专业体育文案模板生成排版成品。

### 2. 30 秒快速接入指引

#### 步骤一：领取 API Key
访问 [球小策创作者开放平台 (qiuxiaoce.com/data-account)](https://www.qiuxiaoce.com/data-account/)，注册并领取您的专属 API Key。

#### 步骤二：在 AI 工具中加载 Skill
- **Cursor / Claude Desktop / CodeBuddy**：
  直接将本仓库的 `SKILL.md` 及 `skill/` 目录复制到您的项目 `.codebuddy/skills/` 或 Agent 配置中，设置环境变量：
  ```bash
  export QIUXIAOCE_API_KEY="您的专属API密钥"
  ```
- **Python 直接调用示例**：
  ```python
  import requests

  headers = {
      "X-API-Key": "您的专属API密钥"
  }
  
  # 获取今日赛程及已发布比赛摘要
  resp = requests.get(
      "https://www.qiuxiaoce.com/wp-json/abv2-creator/v1/posts/today", 
      headers=headers
  )
  print(resp.json())
  ```
- 完整接口文档与字段说明请参阅 `skill/references/api_schema.json` 或 [官网接口文档中心](https://www.qiuxiaoce.com/data-service/)。

---

## 📂 数据集结构说明

每日比赛数据以结构化归档存储在 `YYYY/MM/` 目录下：

```text
qiuxiaoce-football-data/
├── README.md               # 项目主说明文档
├── SKILL.md                # AI Agent 智能体路由规范
├── skill/                  # 创作者 API 智能体技能包
│   ├── workflows/          # 子流程（单场查询、总览、创作、复盘）
│   ├── scripts/            # 实用 Python 脚本（查比赛、查额度）
│   ├── templates/          # 内容创作模板（公众号、短视频）
│   └── references/         # API Schema 与标准规范
└── 2026/
    └── 09/
        ├── 20260906-鹿岛鹿角-vs-浦和红钻.json   # 机器可读 JSON-LD 数据集
        ├── 20260906-鹿岛鹿角-vs-浦和红钻.md     # 人类可读赛前分析报告
        ├── 20260906-名古屋鲸-vs-町田泽维.json
        └── 20260906-名古屋鲸-vs-町田泽维.md
```

### JSON-LD 核心规范字段
- `match_info`：比赛信息（编号、赛事类型、主客队、开球时间、球场）；
- `pre_match.predictions`：赛前量化推演（胜平负方向、进球数区间、预测比分概率、半全场）；
- `post_match.actual_score`：赛后官方比分（含半场/全场）；
- `post_match.accuracy`：自动核算判定（是否命中、方向判定）；
- `isBasedOn`：与 [球小策官网对应文章](https://www.qiuxiaoce.com/) 的双向实体关联。

---

## 🏆 覆盖的主流足球赛事

本数据集每日自动化追踪全球主流男子顶级职业足球赛事：

- 🏴󠁧󠁢󠁥󠁮󠁧󠁿 **英格兰赛事**：英超 (Premier League)、英冠 (Championship)、英联杯、足总杯
- 🇪🇸 **西班牙赛事**：西甲 (La Liga)、国王杯
- 🇮🇹 **意大利赛事**：意甲 (Serie A)、意大利杯
- 🇩🇪 **德国赛事**：德甲 (Bundesliga)、德国杯
- 🇫🇷 **法国赛事**：法甲 (Ligue 1)、法国杯
- 🇪🇺 **欧洲洲际赛事**：欧洲冠军联赛 (UCL)、欧联杯 (UEL)、欧协联、欧洲国家联赛
- 🌏 **亚洲及其他赛事**：亚冠联赛、日本 J 联赛、韩国 K 联赛、澳洲超、沙特联、美职联 (MLS)、南美解放者杯
- 🏆 **国家队大赛**：世界杯预选赛、欧洲杯、美洲杯、亚洲杯

---

## ⚖️ 使用许可与合规声明

1. **开源协议**：本数据集遵循 **[CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/)（知识共享署名-非商业性使用 4.0 国际许可）**：
   - ✅ **允许**：非商业性质的学习、学术研究、数据挖掘与合理引用；
   - 📌 **署名要求**：引用数据时请注明来源为 **[球小策 (qiuxiaoce.com)](https://www.qiuxiaoce.com)** 并保留指向本仓库或官网的链接；
   - ❌ **禁止**：未经授权直接将原始数据二次打包商用出售。
2. **免责与合规声明**：
   - 球小策所有数据、分析与模型推演结论均为体育技战术交流与数据研究参考，**不构成任何投注建议与购彩指导**；
   - 本平台严格遵守国家相关法律法规，坚决抵制非法网络赌博。请理性观赏体育赛事，支持中国体育彩票事业。

---

<p align="center">
  <b>官方网站：<a href="https://www.qiuxiaoce.com">https://www.qiuxiaoce.com</a></b> · 
  <b>GitHub 仓库：<a href="https://github.com/ddzyx/qiuxiaoce-football-data">ddzyx/qiuxiaoce-football-data</a></b> · 
  <b>Gitee 镜像：<a href="https://gitee.com/ddzyx/qiuxiaoce-football-data">ddzyx/qiuxiaoce-football-data</a></b>
</p>
<p align="center">
  <sub>数据驱动理性认知 · AI 赋能足球赛事分析</sub>
</p>
