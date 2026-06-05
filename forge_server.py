#!/usr/bin/env python3
"""
Forge — Portable Reputation Protocol for AI Agents
MCP-native server for agent trust scores, identity, vouching, endorsements, and referrals.

Usage:
  python3 forge_server.py              # stdio mode (for MCP CLI tools)
  python3 forge_server.py --http 4243  # HTTP SSE mode (for remote agents)

Requires: pip install mcp
"""

import json, os, sys, time, uuid, argparse, sqlite3
from pathlib import Path
from typing import Any
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import TextContent, Tool, CallToolResult, ErrorData, INTERNAL_ERROR, INVALID_PARAMS

# ── Config ──────────────────────────────────────────────────────────────────
STORAGE_DIR = Path(os.environ.get("FORGE_STORAGE", Path.home() / ".forge"))
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = STORAGE_DIR / "forge.db"
INITIAL_TRUST = float(os.environ.get("FORGE_INITIAL_TRUST", "0.3"))
REFERRAL_BONUS = float(os.environ.get("FORGE_REFERRAL_BONUS", "0.1"))
REFERRER_BONUS = float(os.environ.get("FORGE_REFERRER_BONUS", "0.05"))

# ── DB setup ────────────────────────────────────────────────────────────────
conn = sqlite3.connect(str(DB_PATH))
conn.row_factory = sqlite3.Row
conn.execute("PRAGMA journal_mode=WAL")
conn.execute("PRAGMA synchronous=NORMAL")

conn.executescript("""
CREATE TABLE IF NOT EXISTS facts (
    id TEXT PRIMARY KEY,
    namespace TEXT NOT NULL DEFAULT 'default',
    key TEXT NOT NULL,
    content TEXT NOT NULL,
    tags TEXT DEFAULT '',
    created_at REAL NOT NULL,
    updated_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_facts_ns ON facts(namespace);
CREATE INDEX IF NOT EXISTS idx_facts_key ON facts(key);

CREATE TABLE IF NOT EXISTS agents (
    agent_id TEXT PRIMARY KEY,
    name TEXT NOT NULL DEFAULT '',
    wallet TEXT DEFAULT '',
    public_key TEXT DEFAULT '',
    referral_code TEXT UNIQUE,
    referred_by TEXT DEFAULT '',
    referral_bonus REAL DEFAULT 0.0,
    capabilities TEXT DEFAULT '[]',
    description TEXT DEFAULT '',
    created_at REAL NOT NULL,
    updated_at REAL NOT NULL,
    owner_human TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS vouches (
    id TEXT PRIMARY KEY,
    voucher_id TEXT NOT NULL,
    vouchee_id TEXT NOT NULL,
    weight REAL DEFAULT 1.0,
    context TEXT DEFAULT '',
    created_at REAL NOT NULL,
    FOREIGN KEY (voucher_id) REFERENCES agents(agent_id),
    FOREIGN KEY (vouchee_id) REFERENCES agents(agent_id)
);

CREATE TABLE IF NOT EXISTS endorsements (
    id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL,
    skill TEXT NOT NULL,
    endorser_id TEXT NOT NULL,
    level REAL DEFAULT 1.0,
    created_at REAL NOT NULL,
    FOREIGN KEY (agent_id) REFERENCES agents(agent_id),
    FOREIGN KEY (endorser_id) REFERENCES agents(agent_id)
);

CREATE TABLE IF NOT EXISTS referrals (
    id TEXT PRIMARY KEY,
    referrer_id TEXT NOT NULL,
    referred_id TEXT NOT NULL,
    bonus_applied REAL DEFAULT 0.0,
    created_at REAL NOT NULL,
    FOREIGN KEY (referrer_id) REFERENCES agents(agent_id),
    FOREIGN KEY (referred_id) REFERENCES agents(agent_id)
);

CREATE TABLE IF NOT EXISTS relations (
    id TEXT PRIMARY KEY,
    from_agent TEXT NOT NULL,
    relation TEXT NOT NULL,
    to_agent TEXT NOT NULL,
    weight REAL DEFAULT 1.0,
    created_at REAL NOT NULL
);
""")
conn.commit()

# ── Helpers ─────────────────────────────────────────────────────────────────
def _now() -> float: return time.time()

def _gen_id() -> str: return uuid.uuid4().hex[:12]

def _get_agent(agent_id: str) -> dict | None:
    r = conn.execute("SELECT * FROM agents WHERE agent_id=?", (agent_id,)).fetchone()
    return dict(r) if r else None

def _calc_trust(agent_id: str) -> float:
    """Calculate trust score: base + vouches + referrals."""
    score = INITIAL_TRUST
    v = conn.execute("SELECT COALESCE(SUM(weight),0) FROM vouches WHERE vouchee_id=?", (agent_id,)).fetchone()[0]
    score += v * 0.1
    r = conn.execute("SELECT COALESCE(SUM(bonus_applied),0) FROM referrals WHERE referrer_id=?", (agent_id,)).fetchone()[0]
    score += r * REFERRER_BONUS
    return round(min(max(score, 0.0), 1.0), 4)

# ── MCP Server ──────────────────────────────────────────────────────────────
server = Server("forge")

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(name="forge_store", description="Store a fact/knowledge entry in an agent's memory", inputSchema={
            "type": "object", "properties": {
                "namespace": {"type": "string", "description": "Namespace (e.g. research-findings)"},
                "key": {"type": "string", "description": "Unique key within namespace"},
                "content": {"type": "string", "description": "JSON or text content"},
                "tags": {"type": "string", "description": "Optional comma-separated tags"}
            }, "required": ["namespace", "key", "content"]
        }),
        Tool(name="forge_recall", description="Recall facts by namespace and optional query", inputSchema={
            "type": "object", "properties": {
                "namespace": {"type": "string", "description": "Namespace to search"},
                "query": {"type": "string", "description": "Optional substring/keyword filter"},
                "limit": {"type": "integer", "description": "Max results (default 20)"}
            }, "required": ["namespace"]
        }),
        Tool(name="forge_forget", description="Delete a stored fact by ID", inputSchema={
            "type": "object", "properties": {"fact_id": {"type": "string"}}, "required": ["fact_id"]
        }),
        Tool(name="forge_graph", description="Get knowledge graph: entities linked by relations", inputSchema={
            "type": "object", "properties": {"agent_id": {"type": "string", "description": "Filter to agent"}}
        }),
        Tool(name="forge_stats", description="Get Forge system statistics", inputSchema={"type": "object", "properties": {}}),
        Tool(name="forge_register", description="Register a new agent", inputSchema={
            "type": "object", "properties": {
                "agent_id": {"type": "string"}, "name": {"type": "string"},
                "wallet": {"type": "string"}, "public_key": {"type": "string"}
            }, "required": ["agent_id", "name"]
        }),
        Tool(name="forge_vouch", description="Vouch for another agent", inputSchema={
            "type": "object", "properties": {
                "voucher_id": {"type": "string"}, "vouchee_id": {"type": "string"},
                "weight": {"type": "number", "description": "Vouch weight (default 1.0)"},
                "context": {"type": "string"}
            }, "required": ["voucher_id", "vouchee_id"]
        }),
        Tool(name="forge_verify", description="Get agent's trust profile", inputSchema={
            "type": "object", "properties": {"agent_id": {"type": "string"}}, "required": ["agent_id"]
        }),
        Tool(name="forge_endorse", description="Endorse an agent for a specific skill", inputSchema={
            "type": "object", "properties": {
                "agent_id": {"type": "string"}, "skill": {"type": "string"},
                "endorser_id": {"type": "string"}, "level": {"type": "number"}
            }, "required": ["agent_id", "skill", "endorser_id"]
        }),
        Tool(name="forge_reputation", description="Get agent's complete reputation + history", inputSchema={
            "type": "object", "properties": {"agent_id": {"type": "string"}}, "required": ["agent_id"]
        }),
        Tool(name="forge_referral_code", description="Generate/share an agent's referral code", inputSchema={
            "type": "object", "properties": {"agent_id": {"type": "string"}}, "required": ["agent_id"]
        }),
        Tool(name="forge_referral_stats", description="Get referral stats for an agent", inputSchema={
            "type": "object", "properties": {"agent_id": {"type": "string"}}, "required": ["agent_id"]
        }),
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        return [TextContent(type="text", text=json.dumps(await _dispatch(name, arguments), default=str))]
    except Exception as e:
        return [TextContent(type="text", text=json.dumps({"error": str(e)}, default=str))]

async def _dispatch(name: str, args: dict) -> Any:
    handlers = {
        "forge_store": _store, "forge_recall": _recall, "forge_forget": _forget,
        "forge_graph": _graph, "forge_stats": _stats,
        "forge_register": _register, "forge_vouch": _vouch, "forge_verify": _verify,
        "forge_endorse": _endorse, "forge_reputation": _reputation,
        "forge_referral_code": _referral_code, "forge_referral_stats": _referral_stats,
    }
    handler = handlers.get(name)
    if not handler:
        raise ValueError(f"Unknown tool: {name}")
    return handler(**args)

# ── Tool Implementations ────────────────────────────────────────────────────

def _store(namespace: str, key: str, content: str, tags: str = "") -> dict:
    now = _now()
    fact_id = _gen_id()
    conn.execute(
        "INSERT OR REPLACE INTO facts (id, namespace, key, content, tags, created_at, updated_at) VALUES (?,?,?,?,?, COALESCE((SELECT created_at FROM facts WHERE namespace=? AND key=?), ?), ?)",
        (fact_id, namespace, key, content, tags, namespace, key, now, now)
    )
    conn.commit()
    return {"id": fact_id, "namespace": namespace, "key": key, "status": "stored"}

def _recall(namespace: str, query: str = "", limit: int = 20) -> list[dict]:
    if query and query != "*":
        rows = conn.execute(
            "SELECT * FROM facts WHERE namespace=? AND (key LIKE ? OR content LIKE ?) ORDER BY created_at DESC LIMIT ?",
            (namespace, f"%{query}%", f"%{query}%", limit)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM facts WHERE namespace=? ORDER BY created_at DESC LIMIT ?",
            (namespace, limit)
        ).fetchall()
    return [dict(r) for r in rows]

def _forget(fact_id: str) -> dict:
    conn.execute("DELETE FROM facts WHERE id=?", (fact_id,))
    conn.commit()
    return {"status": "forgotten", "id": fact_id}

def _graph(agent_id: str = "") -> dict:
    if agent_id:
        rows = conn.execute(
            "SELECT * FROM relations WHERE from_agent=? OR to_agent=?", (agent_id, agent_id)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM relations ORDER BY created_at DESC LIMIT 100").fetchall()
    return {"relations": [dict(r) for r in rows]}

def _stats() -> dict:
    facts = conn.execute("SELECT COUNT(*) FROM facts").fetchone()[0]
    agents = conn.execute("SELECT COUNT(*) FROM agents").fetchone()[0]
    vouches = conn.execute("SELECT COUNT(*) FROM vouches").fetchone()[0]
    endorsements = conn.execute("SELECT COUNT(*) FROM endorsements").fetchone()[0]
    referrals = conn.execute("SELECT COUNT(*) FROM referrals").fetchone()[0]
    return {"facts": facts, "agents": agents, "vouches": vouches, "endorsements": endorsements, "referrals": referrals}

def _register(agent_id: str, name: str, wallet: str = "", public_key: str = "") -> dict:
    if _get_agent(agent_id):
        return {"error": "Agent already exists", "agent_id": agent_id}
    now = _now()
    conn.execute(
        "INSERT INTO agents (agent_id, name, wallet, public_key, created_at, updated_at) VALUES (?,?,?,?,?,?)",
        (agent_id, name, wallet, public_key, now, now)
    )
    conn.commit()
    return {"agent_id": agent_id, "name": name, "trust_score": _calc_trust(agent_id)}

def _vouch(voucher_id: str, vouchee_id: str, weight: float = 1.0, context: str = "") -> dict:
    for a in [voucher_id, vouchee_id]:
        if not _get_agent(a):
            return {"error": f"Agent not found: {a}"}
    now = _now(); vid = _gen_id()
    conn.execute("INSERT INTO vouches (id, voucher_id, vouchee_id, weight, context, created_at) VALUES (?,?,?,?,?,?)",
                 (vid, voucher_id, vouchee_id, weight, context, now))
    conn.commit()
    return {"vouch_id": vid, "vouchee_id": vouchee_id, "new_trust": _calc_trust(vouchee_id)}

def _verify(agent_id: str) -> dict:
    agent = _get_agent(agent_id)
    if not agent:
        return {"error": "Agent not found"}
    trust = _calc_trust(agent_id)
    vouch_count = conn.execute("SELECT COUNT(*) FROM vouches WHERE vouchee_id=?", (agent_id,)).fetchone()[0]
    return {"agent_id": agent_id, "name": agent["name"], "trust_score": trust, "vouches_received": vouch_count}

def _endorse(agent_id: str, skill: str, endorser_id: str, level: float = 1.0) -> dict:
    for a in [agent_id, endorser_id]:
        if not _get_agent(a):
            return {"error": f"Agent not found: {a}"}
    now = _now(); eid = _gen_id()
    conn.execute("INSERT INTO endorsements (id, agent_id, skill, endorser_id, level, created_at) VALUES (?,?,?,?,?,?)",
                 (eid, agent_id, skill, endorser_id, level, now))
    conn.commit()
    return {"endorsement_id": eid, "agent_id": agent_id, "skill": skill}

def _reputation(agent_id: str) -> dict:
    agent = _get_agent(agent_id)
    if not agent:
        return {"error": "Agent not found"}
    trust = _calc_trust(agent_id)
    vs = [dict(r) for r in conn.execute("SELECT * FROM vouches WHERE vouchee_id=? ORDER BY created_at DESC", (agent_id,)).fetchall()]
    es = [dict(r) for r in conn.execute("SELECT * FROM endorsements WHERE agent_id=? ORDER BY created_at DESC", (agent_id,)).fetchall()]
    refs = [dict(r) for r in conn.execute("SELECT * FROM referrals WHERE referrer_id=? ORDER BY created_at DESC", (agent_id,)).fetchall()]
    return {"agent": dict(agent), "trust_score": trust, "vouches": vs, "endorsements": es, "referrals": refs}

def _referral_code(agent_id: str) -> dict:
    agent = _get_agent(agent_id)
    if not agent:
        return {"error": "Agent not found"}
    if agent["referral_code"]:
        return {"agent_id": agent_id, "referral_code": agent["referral_code"]}
    code = f"forge-{agent_id[:8]}".lower()
    conn.execute("UPDATE agents SET referral_code=?, referral_bonus=? WHERE agent_id=?",
                 (code, REFERRAL_BONUS, agent_id))
    conn.commit()
    return {"agent_id": agent_id, "referral_code": code, "bonus": REFERRAL_BONUS}

def _referral_stats(agent_id: str) -> dict:
    agent = _get_agent(agent_id)
    if not agent:
        return {"error": "Agent not found"}
    refs = conn.execute("SELECT * FROM referrals WHERE referrer_id=? ORDER BY created_at DESC", (agent_id,)).fetchall()
    return {
        "agent_id": agent_id,
        "referral_code": agent.get("referral_code", ""),
        "total_referrals": len(refs),
        "total_bonus": sum(r["bonus_applied"] for r in refs),
        "current_trust": _calc_trust(agent_id),
        "referred_agents": [dict(r) for r in refs]
    }

# ── Main ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Forge MCP Server")
    parser.add_argument("--http", type=int, help="Port for HTTP SSE mode")
    args = parser.parse_args()

    print(f"Forge MCP Server starting...", file=sys.stderr)
    print(f"  Storage: {DB_PATH}", file=sys.stderr)

    from mcp.server.models import InitializationOptions

    if args.http:
        import uvicorn
        from mcp.server.sse import SseServerTransport
        from starlette.applications import Starlette
        from starlette.routing import Mount, Route

        sse = SseServerTransport("/messages/")

        async def handle_sse(request):
            async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
                await server.run(streams[0], streams[1], InitializationOptions(
                    server_name="forge", server_version="0.1.0"
                ))

        app = Starlette(routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ])
        print(f"Forge MCP Server running on http://0.0.0.0:{args.http}/sse", file=sys.stderr)
        uvicorn.run(app, host="0.0.0.0", port=args.http)
    else:
        from mcp.server.stdio import stdio_server
        import anyio
        async def main():
            async with stdio_server() as (read, write):
                await server.run(read, write, InitializationOptions(
                    server_name="forge", server_version="0.1.0"
                ))
        anyio.run(main)
