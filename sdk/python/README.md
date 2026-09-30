# XG Mind AI — Predictive Football Terminal Python SDK

[![PyPI](https://img.shields.io/pypi/v/xgmind.svg)](https://pypi.org/project/xgmind/)
[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC--BY--NC%204.0-blue.svg)](https://creativecommons.org/licenses/by-nc/4.0/)
[![Terminal](https://img.shields.io/badge/Official-XG_Mind_AI-2563EB?logo=cloudflare&logoColor=white)](https://xgmind.com/)

Lightweight Python client and command-line toolkit for [XG Mind AI (xgmind.com)](https://xgmind.com/), the premier global predictive football intelligence terminal covering 88 elite leagues worldwide.

---

## ⚡ Key Portals & Documentation

- 🌐 **Official Global Terminal**: [https://xgmind.com/](https://xgmind.com/)
- 📊 **Verified Performance Ledger**: [https://xgmind.com/performance/](https://xgmind.com/performance/)
- 🏆 **88 League Standings & xG Metrics**: [https://xgmind.com/leagues/](https://xgmind.com/leagues/)
- 🏃 **Player Quant Power Rankings**: [https://xgmind.com/players/](https://xgmind.com/players/)
- 📑 **Data Methodology & Poisson Synthesis**: [https://xgmind.com/methodology/](https://xgmind.com/methodology/)

---

## 📦 Installation

```bash
pip install xgmind
```

---

## 🚀 Quickstart

```python
from xgmind import XGMindClient

client = XGMindClient()

# 1. Fetch live predictive match intelligence for today
matches = client.get_today_matches()
for m in matches:
    print(f"{m.home_team} vs {m.away_team} | 1X2 Prob: {m.prob_1x2}")

# 2. Query public verified ledger & performance metrics
ledger = client.get_settled_ledger(limit=10)
print(f"Overall Settled Hit Rate: {ledger.hit_rate}%")
```

---

## ⚖️ License & Attribution

Distributed under CC BY-NC 4.0. Quantitative football data powered by [XG Mind AI Terminal](https://xgmind.com/).
