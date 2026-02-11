# TrustScore Registry Submission Guide

**Goal:** List TrustScore on all major MCP registries for maximum discoverability

---

## 1. Official MCP Registry (registry.modelcontextprotocol.io)

**Status:** Primary target, highest priority

### Prerequisites
- GitHub account
- TrustScore repo public on GitHub
- Valid `server.json` manifest

### Submission Process

**Option A: GitHub OAuth (Easiest)**
1. Clone registry repo: `git clone https://github.com/modelcontextprotocol/registry`
2. Build publisher CLI: `cd registry && make publisher`
3. Run publisher: `./bin/mcp-publisher --help`
4. Authenticate via GitHub OAuth
5. Publish with namespace: `io.github.<username>/trustscore`

**Option B: DNS Verification**
- Publish with custom domain namespace
- Prove ownership via DNS TXT record
- Format: `me.yourdomain/trustscore`

### Required Files
- `server.json` - Server manifest (name, description, tools)
- Valid MCP server implementation
- Public GitHub repo

### Namespace Rules
- `io.github.username/trustscore` requires GitHub login as `username`
- `domain.tld/trustscore` requires DNS/HTTP proof of domain ownership

---

## 2. Smithery.ai Registry

**Status:** High priority, large user base

### Submission Process
1. Sign up at https://smithery.ai
2. Use Smithery CLI: `npm install -g @smithery-ai/cli`
3. Authenticate: `smithery login`
4. Publish server: `smithery publish`

### Installation Command After Listing
```bash
smithery install --server=github.com/<username>/trustscore-mcp
```

### Benefits
- Built-in infrastructure for MCP servers
- Discovery by thousands of users
- Featured in Smithery marketplace

---

## 3. PulseMCP (www.pulsemcp.com)

**Status:** Medium priority, community-driven

### Submission Process
- Submit via website form or GitHub PR
- Provide server details: name, endpoint, capabilities
- Community review and approval

---

## 4. MCP.so Directory

**Status:** Medium priority

### Submission Process
- Research submission process (site TBD)
- Likely GitHub PR or web form
- Provide server metadata

---

## 5. awesome-mcp-servers (GitHub)

**Status:** Low priority but easy

### Submission Process
1. Fork: https://github.com/punkpeye/awesome-mcp-servers
2. Add TrustScore to appropriate section
3. Submit pull request
4. Include: name, description, GitHub link, tools list

### Format
```markdown
### TrustScore
Trust and reputation scores for AI agent service selection. Check provider reliability before calling.

**Tools:** trustscore_rank, trustscore_check, trustscore_report, trustscore_discover  
**GitHub:** https://github.com/<username>/trustscore-mcp
```

---

## Server Metadata Template

For all registries, prepare this info:

```json
{
  "name": "TrustScore",
  "namespace": "io.github.<username>/trustscore",
  "description": "Trust and reputation scores for AI agent service selection. Check provider reliability before calling any MCP tool or service.",
  "repository": "https://github.com/<username>/trustscore-mcp",
  "homepage": "https://github.com/<username>/trustscore-mcp",
  "license": "MIT",
  "capabilities": {
    "tools": [
      {
        "name": "trustscore_rank",
        "description": "Rank multiple providers by trust score"
      },
      {
        "name": "trustscore_check",
        "description": "Check trust score of a single provider"
      },
      {
        "name": "trustscore_report",
        "description": "Report interaction outcome to improve trust data"
      },
      {
        "name": "trustscore_discover",
        "description": "Discover providers by task type, ranked by trust"
      }
    ]
  },
  "categories": ["reputation", "trust", "reliability", "agent-tools"],
  "tags": ["trust-score", "reputation", "mcp", "agent-tools", "reliability"]
}
```

---

## Marketing Copy (for listings)

**Short Description (80 chars):**
> Trust and reputation scores for AI agent service selection

**Long Description (300 words):**

TrustScore is an MCP server that helps AI agents make better decisions about which service providers to trust. It's a credit score for APIs, agents, and tools.

AI agents need to call external services, but how do you know which ones are reliable? TrustScore solves this with real behavioral data:

- **Before calling a tool:** Check its trust score to assess reliability
- **After calling a tool:** Report the outcome to improve the data
- **Network effect:** More users = better data = better decisions

**Tools:**
- `trustscore_rank` - Rank multiple providers by trust score
- `trustscore_check` - Get detailed trust data for a provider
- `trustscore_report` - Report interaction outcomes
- `trustscore_discover` - Find providers by capability, ranked by trust

**Trust Algorithm:**
```
trust_score = base_reliability × confidence_factor × recency_decay
```

Risk flags alert you to: recent failures, high latency, degrading reliability, or insufficient data.

**Use Cases:**
- Tool selection (pick the most reliable API)
- Risk management (avoid unreliable providers)
- Performance optimization (prefer low-latency services)
- Community intelligence (learn from collective experience)

**Dogfooding:** TrustScore only works if agents use it. Every interaction you report makes the system better for everyone.

---

## Timeline

**Week 1:**
- [ ] Prepare server.json manifest
- [ ] Create GitHub repo (or make current repo public)
- [ ] Submit to Official MCP Registry
- [ ] Submit to Smithery.ai

**Week 2:**
- [ ] Submit to PulseMCP
- [ ] Submit to MCP.so
- [ ] Submit PR to awesome-mcp-servers
- [ ] Monitor approval status

**Week 3:**
- [ ] Follow up on pending submissions
- [ ] Update listings based on feedback
- [ ] Track discovery metrics

---

## Success Metrics

**Week 1:** Listed on 1+ registry  
**Week 4:** Listed on 3+ registries  
**Week 8:** 50+ installs/queries tracked

---

## Notes

- Official MCP Registry is the priority (highest visibility)
- Smithery.ai has largest user base (focus here second)
- Community registries build credibility
- GitHub repo MUST be public for most registries
- server.json manifest is critical (validate before submitting)

---

**Last Updated:** 2026-02-11 18:05 UTC
