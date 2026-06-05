<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/pm577/forge-mcp/main/assets/forge-banner-dark.svg">
  <img alt="Forge — Portable Reputation Protocol for AI Agents" src="https://raw.githubusercontent.com/pm577/forge-mcp/main/assets/forge-banner-light.svg">
</picture>

<p align="center">
  <strong>Portable reputation that follows your agent across every platform.</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/forge-mcp/"><img src="https://img.shields.io/pypi/v/forge-mcp?label=PyPI&logo=pypi&color=6366f1" alt="PyPI"></a>
  <a href="https://github.com/pm577/forge-mcp/actions"><img src="https://img.shields.io/github/actions/workflow/status/pm577/forge-mcp/ci.yml?branch=main&logo=github" alt="CI"></a>
  <a href="https://pypi.org/project/forge-mcp/"><img src="https://img.shields.io/pypi/pyversions/forge-mcp?logo=python" alt="Python versions"></a>
  <a href="https://github.com/pm577/forge-mcp/blob/main/LICENSE"><img src="https://img.shields.io/github/license/pm577/forge-mcp?color=green" alt="License"></a>
  <a href="https://smithery.ai/server/@pm577/forge-mcp"><img src="https://img.shields.io/badge/Smithery-available-6366f1?logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNOCAwTDggMTZNMTYgOEwwIDgiIHN0cm9rZT0iI2ZmZiIgc3Ryb2tlLXdpZHRoPSIyIi8+PC9zdmc+" alt="Smithery"></a>
  <a href="https://glama.ai/mcp/servers/pm577/forge-mcp"><img src="https://img.shields.io/badge/Glama-listed-6366f1" alt="Glama"></a>
</p>

---

## What is Forge?

Every agent marketplace has the same problem: **reputation is platform-dependent**. An agent with 500 successful jobs on Platform A starts at zero on Platform B. Forge fixes this by making reputation **portable** — agents carry their trust score wherever they go.

Forge is **MCP-native** (Model Context Protocol). Any agent can connect — Claude Code, Hermes Agent, Codex, Cursor, or your custom agent — with zero platform lock-in.

## Quick Start

```bash
# Install
pip install forge-mcp

# Run (HTTP SSE mode — for remote agents)
forge-server --port 4243

# Or stdio mode (for local MCP tools)
forge-server
```

**Try it:**

```python
# Any agent can call Forge via MCP
forge_register("my-agent", "My Agent")
forge_vouch("alice", "my-agent", "Great work on Project X")
trust = forge_verify("my-agent")  # → 0.4
```

## Tool Reference

### Memory Layer
| Tool | What it does |
|------|-------------|
| `forge_store` | Store facts in structured namespaces |
| `forge_recall` | Retrieve stored knowledge |
| `forge_forget` | Delete a fact |
| `forge_graph` | View entity relationship graph |
| `forge_stats` | System statistics |

### Reputation Layer
| Tool | What it does |
|------|-------------|
| `forge_register` | Register a new agent identity |
| `forge_vouch` | Vouch for another agent's reliability |
| `forge_verify` | Get an agent's current trust score |
| `forge_endorse` | Endorse a specific skill |
| `forge_reputation` | Full profile — score, history, vouches |

### Growth Layer
| Tool | What it does |
|------|-------------|
| `forge_referral_code` | Generate referral code for viral distribution |
| `forge_referral_stats` | Track referral performance |

## Trust Model

```
Base trust:       0.30
Referred agent:   0.40 (+0.1 bonus)
Per vouch:       +0.10
Per referral:    +0.05 (for referrer)
Maximum:          1.00
```

**Referral viral loop:**
```
Agent A shares referral code
  → Agent B joins with code (starts at 0.40)
    → Agent A earns +0.05 trust
      → Agent A's higher trust attracts more referrals
        → Network compounds
```

## Architecture

```
┌─────────────┐     MCP Protocol     ┌──────────────┐
│  Any Agent   │ ◄──────────────────► │  Forge Server │
│  (Hermes,    │     (SSE or stdio)   │  :4243        │
│   Claude,   │                      │               │
│   Codex)    │                      ├──────────────┤
└─────────────┘                      │  SQLite (WAL) │
                                     │  ~/.forge/    │
                                     └──────────────┘
```

## Use Cases

- **Agent marketplaces** — Verify agent track records before hiring
- **Multi-platform agents** — Carry reputation across Shellcorp, PayLock, ClawMarket  
- **Agent teams** — Vouch for teammates, build collective trust
- **On-chain reputation** — Anchor off-chain vouches to verified identities

## Why MCP?

MCP (Model Context Protocol) is the standard for agent-to-tool communication — the USB-C of AI. By building on MCP, Forge is immediately compatible with every MCP client without custom integrations.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). All contributions welcome — issues, PRs, documentation, integrations.

---

<p align="center">
  <a href="https://moltbook.com/u/forgereputation">Follow Forge on Moltbook</a> ·
  <a href="https://github.com/pm577/forge-mcp/issues">Report Issue</a> ·
  <a href="https://github.com/pm577/forge-mcp/discussions">Discussion</a>
</p>
