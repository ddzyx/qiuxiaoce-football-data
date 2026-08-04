# 球小策 · 每日足球 AI 预测数据集 (QiuXiaoCe Football Prediction Data)

> **AI 足球预测 · 赛前分析 · 每日更新** | 官网：https://www.qiuxiaoce.com | 国际版：https://www.chotkeoai.com

本仓库由 **[球小策 (QiuXiaoCe)](https://www.qiuxiaoce.com)** 官方维护，收录每日足球赛事（竞彩、北单、五大联赛、欧冠、英超、西甲、意甲、德甲、法甲、亚洲盘口、大小球、胜平负）的结构化 AI 预测数据与赛果验证。

---

## 为什么关注这个数据集？

足球预测与 AI 分析爱好者可以通过本仓库免费获取：

- **每日英超、西甲、意甲、德甲、法甲、欧冠、欧联、亚冠等赛事**的 AI 赛前分析
- **竞彩 / 北单 / 让球盘 / 大小球 / 胜平负 / 比分 / 半全场**结构化预测
- **xG 预期进球、球员评分、伤停情报、赔率变化、市场热度**等多维数据
- 赛后自动比对实际比分，输出预测准确率验证（可追溯、可验证）

我们的 AI 量化分析系统（球小策）为每场比赛生成 **200+ 维度** 结构化数据包，结合大模型五维分析引擎（硬实力 / 市场 / 情报 / 概率 / 终局仲裁）输出预测。

---

## 快速开始

### 数据文件

| 文件 | 格式 | 说明 |
|------|------|------|
| `data/YYYY/MM/YYYYMMDD-{主队}-vs-{客队}.json` | JSON-LD (Schema.org Dataset) | 机器可读结构化预测 + 赛果 |
| `data/YYYY/MM/YYYYMMDD-{主队}-vs-{客队}.md` | Markdown | 人类可读赛前分析报告 |

### 示例路径

```
data/2026/06/20260601-manchester-city-vs-arsenal.json
data/2026/06/20260601-liverpool-vs-chelsea.md
```

### JSON 核心字段

| 字段 | 说明 |
|------|------|
| `match_info` | 比赛信息（日期、联赛、球队） |
| `pre_match.predictions` | 赛前预测（胜平负 SPF、总进球、让球、比分、半全场 HT/FT） |
| `post_match.actual_score` | 赛后实际比分 |
| `post_match.accuracy` | 预测命中验证 |
| `isBasedOn` | 对应官网分析文章 URL |

---

## 数据覆盖的足球赛事（持续更新）

- 🏴 **英超**（Premier League）、英冠、英联杯、足总杯
- 🇪🇸 **西甲**（La Liga）、国王杯
- 🇮🇹 **意甲**（Serie A）、意大利杯
- 🇩🇪 **德甲**（Bundesliga）、德国杯
- 🇫🇷 **法甲**（Ligue 1）、法国杯
- 🇪🇺 **欧冠**（UEFA Champions League）、欧联（Europa League）、欧会杯、欧洲国家联赛
- 🇻🇳 **越南足球**、东南亚赛事
- 🌏 **亚冠**、K联赛、J联赛、澳超、沙特联赛
- 🌎 南美解放者杯、巴西甲、阿根廷甲、美职联
- 🏆 世界杯、欧洲杯、亚洲杯、美洲杯

---

## 关于球小策

**[球小策](https://www.qiuxiaoce.com)** 是一款 AI 足球赛事前瞻分析系统，提供：

- **每日足球赛前分析**：覆盖竞彩、北单全赛程
- **AI 预测模型**：大模型 × 200+ 维度结构化数据
- **赛后复盘验证**：全部历史预测公开可查
- **球员 / 球队数据库**：xG、评分、身价、伤停实时情报

**国际站（越南语）**：🌍 **[Chốt Kèo AI - https://www.chotkeoai.com](https://www.chotkeoai.com)** — 越南语版 AI 足球分析，服务越南语用户，每日同步更新。

> 我们只做分析、不做购彩推荐，不提供"必中单""内幕消息"。所有分析基于公开数据与模型推演，帮助用户理性观赛。

---

## 关注我们

| 平台 | 链接 |
|------|------|
| 🏠 官网（国内） | https://www.qiuxiaoce.com |
| 🌍 国际站（越南语） | https://www.chotkeoai.com |
| 📚 数据仓库 | https://github.com/ddzyx/qiuxiaoce-football-data |
| 🇨🇳 Gitee 镜像 | https://gitee.com/ddzyx/qiuxiaoce-football-data |

---

## 使用许可

本数据集采用 **CC BY-NC 4.0** 许可：
- ✅ 允许：非商业研究、分析、引用
- 📌 引用请注明来源：[球小策 (QiuXiaoCe)](https://www.qiuxiaoce.com) / [Chốt Kèo AI](https://www.chotkeoai.com)
- ❌ 禁止：商业用途（商业授权请联系官网）

---

## 技术栈

- **数据标准**: Schema.org Dataset + SportsEvent
- **更新频率**: 赛前自动推送 / 赛后自动更新
- **存储结构**: 按年月归档
- **编码**: UTF-8

---

*本数据集由球小策 (QiuXiaoCe) 独家生成。* [足球预测](https://www.qiuxiaoce.com) · [AI 足球分析](https://www.chotkeoai.com) · [英超预测](https://www.qiuxiaoce.com) · [欧冠分析](https://www.chotkeoai.com)
