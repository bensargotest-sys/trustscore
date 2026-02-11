# MCP Registry Submission Guide

## Overview
The official MCP Registry (https://registry.modelcontextprotocol.io/) is like an app store for MCP servers. It's community-driven and maintained by Anthropic, PulseMCP, GitHub, and Stacklok.

**Status:** API freeze (v0.1) - stable for integrations, no breaking changes expected

## Prerequisites
✅ **We have:**
- Functional MCP server (TrustScore)
- GitHub account (bensargotest-sys)
- All tests passing
- MIT LICENSE
- Comprehensive README

❌ **We need:**
- `server.json` manifest file (create this)
- GitHub repo published (blocked, working on it)
- MCP Publisher CLI tool (install this)

## Authentication Methods
Choose one:

### Option 1: GitHub OAuth (Easiest for us)
- Login via GitHub
- Publish under `io.github.bensargotest-sys/trustscore`
- No DNS verification required
- **RECOMMENDED** - We already have GitHub account

### Option 2: DNS Verification
- Prove ownership of domain
- Publish under custom namespace (e.g., `com.trustscore/trustscore`)
- Requires DNS TXT record

### Option 3: HTTP Verification
- Prove ownership via HTTP endpoint
- Similar to DNS but uses HTTP challenge

## Step-by-Step Submission Process

### Step 1: Create `server.json` Manifest
Create file at repo root:
```json
{
  "name": "trustscore",
  "description": "Trust and reputation scores for AI agent service selection. Track reliability, uptime, quality metrics, and build algorithmic trust for MCP servers.",
  "version": "0.1.0",
  "author": {
    "name": "bensargotest-sys",
    "url": "https://github.com/bensargotest-sys"
  },
  "license": "MIT",
  "homepage": "https://github.com/bensargotest-sys/trustscore",
  "repository": {
    "type": "git",
    "url": "https://github.com/bensargotest-sys/trustscore.git"
  },
  "capabilities": {
    "tools": true,
    "resources": false,
    "prompts": false
  },
  "tools": [
    {
      "name": "trustscore_check",
      "description": "Check trust score for a provider before making external calls"
    },
    {
      "name": "trustscore_report",
      "description": "Report outcome of external call (success/failure/latency)"
    },
    {
      "name": "trustscore_rank",
      "description": "Get ranked list of providers by trust score"
    },
    {
      "name": "trustscore_discover",
      "description": "Discover new MCP servers by category"
    }
  ],
  "categories": ["monitoring", "analytics", "trust", "reliability"],
  "transport": {
    "type": "stdio"
  },
  "installation": {
    "type": "git",
    "url": "https://github.com/bensargotest-sys/trustscore.git",
    "setupCommand": "npm install && npm run build"
  }
}
```

### Step 2: Update README
Ensure README includes:
- ✅ Clear description (we have this)
- ✅ Installation instructions (we have this)
- ✅ Usage examples (we have this in `examples/`)
- ✅ License info (MIT, we have this)
- ✅ Quick start section (we have this)

### Step 3: Install MCP Publisher CLI
```bash
# Clone registry repo
git clone https://github.com/modelcontextprotocol/registry.git
cd registry

# Build publisher CLI
make publisher

# Or use pre-built binary (if available)
# Download from GitHub releases
```

### Step 4: Validate Locally
```bash
# Run publisher in dry-run mode
./bin/mcp-publisher publish \
  --manifest /path/to/trustscore/server.json \
  --dry-run

# Check for validation errors
```

### Step 5: Authenticate with GitHub
```bash
# Publisher will prompt for GitHub OAuth
./bin/mcp-publisher login
# Opens browser, authorize with GitHub account
```

### Step 6: Publish to Registry
```bash
# Publish for real
./bin/mcp-publisher publish \
  --manifest /path/to/trustscore/server.json \
  --namespace io.github.bensargotest-sys

# Namespace format: io.github.<username>/<server-name>
```

### Step 7: Verify Publication
- Check https://registry.modelcontextprotocol.io/
- Search for "trustscore"
- Verify metadata, description, tools list
- Test discovery in MCP clients (Claude Desktop, Cursor)

## Post-Publication

### Update Badge in README
```markdown
[![MCP Registry](https://img.shields.io/badge/MCP-Registry-blue)](https://registry.modelcontextprotocol.io/servers/io.github.bensargotest-sys.trustscore)
```

### Monitor Adoption
- Track GitHub stars/forks
- Monitor registry downloads (if available)
- Watch for issues/PRs from users

### Update Process
When pushing updates:
1. Update `version` in `server.json` (semantic versioning)
2. Push to GitHub
3. Re-run `mcp-publisher publish`
4. Registry will validate and update listing

## Expected Timeline
- **Manual time:** 30 minutes (create manifest, test, publish)
- **Automated validation:** ~5 minutes
- **Registry indexing:** ~1 hour for public discovery

## Blockers (Current)
1. ❌ GitHub repo not created yet (token issue)
2. ❌ MCP Publisher CLI not installed
3. ✅ All other requirements met (tests, LICENSE, README, examples)

## Next Steps (Once Unblocked)
1. Create GitHub repo: `bensargotest-sys/trustscore`
2. Push all commits (6 commits ready)
3. Create `server.json` manifest
4. Install MCP Publisher CLI
5. Publish to registry
6. Announce on Discord/X/Moltbook

## Resources
- Official registry: https://registry.modelcontextprotocol.io/
- GitHub repo: https://github.com/modelcontextprotocol/registry
- API docs: https://registry.modelcontextprotocol.io/docs
- Discord: #registry-dev channel
- Documentation: https://github.com/modelcontextprotocol/registry/blob/main/docs/
