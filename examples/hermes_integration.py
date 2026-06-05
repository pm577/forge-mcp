"""
Integrate Forge with Hermes Agent.
Save this as a Hermes skill to give agents portable reputation.
"""

FORGE_SERVER = "http://localhost:4243"

TOOLS = """
You have access to Forge reputation tools via MCP.
Call them like any other tool:

- forge_register(agent_id="my-agent", name="My Agent")
    → Register yourself for reputation tracking

- forge_vouch(voucher_id="alice", vouchee_id="bob", weight=1.0, context="Completed task")
    → Vouch for another agent

- forge_verify(agent_id="bob")
    → Get trust score

- forge_endorse(agent_id="bob", skill="python", endorser_id="alice", level=0.9)
    → Endorse a skill

- forge_reputation(agent_id="bob")
    → Full profile
"""

QUICK_START = """
# In your Hermes agent session:
# After starting forge_server.py --http 4243, just call:
forge_register(agent_id="hermes-agent", name="Hermes Agent")
my_trust = forge_verify(agent_id="hermes-agent")
print(f"My trust score: {my_trust}")
"""
