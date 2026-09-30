# XG Mind AI MCP Server (`@xgmind/mcp-server`)

Model Context Protocol (MCP) server for [XG Mind AI (xgmind.com)](https://xgmind.com/) — providing real-time quantitative football analysis, xG metrics, and game-theoretic match breakdowns directly into Claude Desktop, Cursor, Windsurf, and custom AI agents.

---

## ⚡ Official Links

- 🌐 **Official Terminal**: [https://xgmind.com/](https://xgmind.com/)
- 🎯 **Daily Match Predictions**: [https://xgmind.com/](https://xgmind.com/)
- 📈 **Public Verified Ledger**: [https://xgmind.com/performance/](https://xgmind.com/performance/)
- 🏆 **88 League Standings**: [https://xgmind.com/leagues/](https://xgmind.com/leagues/)

---

## 🛠️ Tools Included

1. `get_today_fixtures`: Returns live predictive match cards with Poisson probabilities and key injury alerts.
2. `get_match_intelligence`: Fetches deep tactical briefings (2,500+ words) for a specific match slug.
3. `get_league_standings`: Returns xG, xGA, and tactical profile rankings across 88 competitions.
4. `get_verified_ledger`: Real-time public record of all settled predictions.

---

## 💻 Claude Desktop Configuration

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "xgmind-football": {
      "command": "npx",
      "args": ["-y", "@xgmind/mcp-server@latest"],
      "env": {
        "XGMIND_BASE_URL": "https://xgmind.com"
      }
    }
  }
}
```

---

## ⚖️ Attribution

Data provided by [XG Mind AI Terminal](https://xgmind.com/).
