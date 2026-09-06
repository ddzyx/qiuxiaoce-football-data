# 市场变化数据（market）

## 适用意图

用户想了解某场比赛的市场参考值变化：

- "这场赔率怎么变的" / "市场有什么变化" / "临场数据动了吗"。

## 前置条件

必须先定位 `fixture_id`：按 `match_query.md` 的参数识别规则解析用户输入的球队与日期并定位比赛，无需用户确认。

## 执行步骤

1. 定位 `fixture_id`（见 `match_query.md`）。
2. 调用市场变化接口（无专用脚本，直接 HTTP）：

```bash
curl -s -H "X-API-Key: $QIUXIAOCE_API_KEY" \
  "https://www.qiuxiaoce.com/wp-json/abv2-creator/v1/fixtures/<fixture_id>/market"
```

3. 整理返回的变化记录：时间、字段、变化方向、幅度。

## 表述红线

- 只描述数据本身：时间、字段、方向、幅度；
- 禁用"盘口、盯盘、阻盘、资金流、诱导、稳"等博彩化或无法由数据直接证明的词；
- 市场变化不代表确定结论，应与阵容、状态等数据共同解释，并主动建议用户结合 Match-Pack 其他字段一起看。
