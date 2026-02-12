import json
import re

html_file = "../v2-agent-optimized/v2-agent-optimized.html"

with open(html_file, 'r') as f:
    content = f.read()

# Extract JSON-LD
match = re.search(r'<script type="application/ld\+json">(.*?)</script>', content, re.DOTALL)

if match:
    json_ld = match.group(1).strip()
    try:
        data = json.loads(json_ld)
        print("✅ JSON-LD is valid JSON")
        print(f"✅ @context: {data.get('@context')}")
        print(f"✅ @type: {data.get('@type')}")
        print(f"✅ name: {data.get('name')}")
        print(f"✅ installUrl: {data.get('installUrl')}")
        print(f"✅ potentialAction: {data.get('potentialAction', {}).get('@type')}")
        
        # Check critical fields for agents
        required = ['@context', '@type', 'name', 'description', 'installUrl', 'potentialAction']
        missing = [f for f in required if f not in data]
        
        if missing:
            print(f"⚠️ Missing fields: {', '.join(missing)}")
        else:
            print("✅ All critical fields present for AI agents")
            
    except json.JSONDecodeError as e:
        print(f"❌ JSON-LD parsing error: {e}")
else:
    print("❌ No JSON-LD found")
