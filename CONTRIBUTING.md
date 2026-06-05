# Contributing to Forge

Thanks for your interest! Here's how to contribute.

## Getting Started

1. Fork the repo
2. Clone: `git clone https://github.com/YOUR_USER/forge-mcp`
3. Install: `pip install -r requirements.txt`
4. Test: `python3 forge_server.py --http 4243`

## How to Contribute

### Report a Bug
Open an issue with:
- Your environment (OS, Python version)
- Steps to reproduce
- Expected vs actual behavior

### Suggest a Feature
Open an issue describing:
- The problem you're solving
- How Forge should work after
- Any alternatives considered

### Submit Code
1. Create a branch: `git checkout -b feature/your-feature`
2. Make changes
3. Test: server starts and tools respond
4. Commit with clear message
5. Push and open PR

## Code Style

- Python 3.10+ compatible
- Follow existing patterns in forge_server.py
- No external dependencies beyond mcp + starlette

## Project Structure

```
forge_server.py    — Main MCP server (all tools in one file)
examples/          — Usage examples
.github/workflows/ — CI/CD
```

## Getting Help

- Open a [Discussion](https://github.com/pm577/forge-mcp/discussions)
- DM on Moltbook: [forgereputation](https://moltbook.com/u/forgereputation)
