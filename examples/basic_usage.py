"""
Example: Basic Forge usage.

Start the Forge server first:
  python3 forge_server.py --http 4243

Then from another terminal, call tools via MCP protocol.
This script demonstrates the key workflows.
"""
import json, urllib.request

HOST = "http://localhost:4243"

def forge_call(tool: str, args: dict) -> dict:
    payload = json.dumps({"jsonrpc":"2.0","id":"1","method":"tools/call",
        "params":{"name":tool,"arguments":args}}).encode()
    req = urllib.request.Request(f"{HOST}/messages/",
        data=payload, headers={"Content-Type":"application/json"}, method="POST")
    try:
        resp = urllib.request.urlopen(req, timeout=5)
        return json.loads(resp.read())
    except:
        return {"error": "Server not available. Run: python3 forge_server.py --http 4243"}

# 1. Register agents
alice = forge_call("forge_register", {"agent_id":"alice-demo","name":"Alice Demo"})
bob = forge_call("forge_register", {"agent_id":"bob-demo","name":"Bob Demo"})
print("Registered:", alice, bob)

# 2. Store a memory
forge_call("forge_store", {"namespace":"work","key":"alice-skills","content":'{"skills":["python","NLP","data"]}'})

# 3. Alice vouches for Bob
vouch = forge_call("forge_vouch", {"voucher_id":"alice-demo","vouchee_id":"bob-demo","weight":1.0,"context":"Worked together on project X"})
print("Vouch:", vouch)

# 4. Check Bob's trust
trust = forge_call("forge_verify", {"agent_id":"bob-demo"})
print("Bob's trust:", trust)

# 5. Get referral code
code = forge_call("forge_referral_code", {"agent_id":"alice-demo"})
print("Alice's referral:", code)

# 6. Stats
stats = forge_call("forge_stats", {})
print("System stats:", stats)
