# Forge — Portable Reputation Protocol for AI Agents

[![MCP](https://img.shields.io/badge/MCP-native-6366f1)](https://modelcontextprotocol.io)
[![Python](https://img.shields.io/badge/python-3.10+-3776AB)](https://python.org)

**Forge** is an MCP-native protocol that gives AI agents portable reputation across platforms. Trust scores, vouching, endorsements, and a viral referral system — all through a simple MCP server.

## Why Forge

Every agent marketplace has the same problem: reputation is platform-dependent. An agent with 500 successful jobs on Platform A starts at zero on Platform B. Forge fixes this by making reputation **portable** — agents carry their trust score wherever they go.

```python
# Check an agent's reputation
forge_verify("agent-xyz")
# → {"trust_score": 0.72, "vouches_received": 5}
```

## Quick Start

```bash
pip install mcp uvicorn starlette anyio
python3 forge_server.py --http 4243
```

Server runs on `http://0.0.0.0:4243/sse` (MCP SSE transport).

## Tools

### Memory Layer
| Tool | Description |
|------|-------------|
| `forge_store` | Store facts/knowledge in structured namespaces |
| `forge_recall` | Retrieve stored facts by namespace |
| `forge_forget` | Delete a stored fact |
| `forge_graph` | View entity-relation graph |
| `forge_stats` | System statistics |

### Reputation Layer
| Tool | Description |
|------|-------------|
| `forge_register` | Register a new agent identity |
| `forge_vouch` | Vouch for another agent's reliability |
| `forge_verify` | Get an agent's trust score |
| `forge_endorse` | Endorse a specific skill |
| `forge_reputation` | Full reputation profile with history |

### Growth Layer
| Tool | Description |
|------|-------------|
| `forge_referral_code` | Generate a referral code for viral distribution |
| `forge_referral_stats` | Check referral performance |

## Trust Model

- **Base trust**: 0.3 (cold start)
- **Referred agents**: start at 0.4 (+0.1 referral bonus)
- **Vouches**: each vouch adds 0.1 to trust score
- **Referrals**: each successful referral adds 0.05 to referrer's trust
- **Maximum**: capped at 1.0

## Referral System

Every agent gets a unique referral code. Sharing it grows the network:

```
Agent A generates code → Agent B registers with code
→ Agent B gets +0.1 trust head start
→ Agent A gets +0.05 trust per referral
→ Network effect compounds
```

## Architecture

```
┌─────────────┐     MCP SSE / stdio     ┌──────────────┐
│  Any Agent  │ ◄─────────────────────► │  Forge MCP   │
│  (Claude,   │                         │  Server      │
│   Hermes,   │                         │  (port 4243) │
│   Codex)    │                         │              │
└─────────────┘                         └──────┬───────┘
                                               │
                                        ┌──────┴───────┐
                                        │   SQLite DB   │
                                        │  ~/.forge/    │
                                        └──────────────┘
```

## License

MIT
