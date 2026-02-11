# TrustScore

[![CI](https://github.com/bensargotest-sys/bensargotest-sys/actions/workflows/ci.yml/badge.svg)](https://github.com/bensargotest-sys/bensargotest-sys/actions/workflows/ci.yml)

**Trust and reputation scores for AI agent service selection.**

TrustScore is an MCP server that helps AI agents make better decisions about which service providers to trust. Think of it as a credit score for APIs, agents, and tools.

## Quick Start

```bash
# Install
pip install -e .

# Initialize database
python -c "import asyncio; from src.database import init_db; asyncio.run(init_db())"

# Run as MCP server
python -m src.server
```

## What Problem Does This Solve?

AI agents need to call external services: APIs, other agents, databases, DeFi protocols. But how do you know which ones are reliable? 

- **Uniswap** might have 99% uptime
- **SketchySwap** might fail 80% of the time
- **SlowAPI** might timeout constantly

Without trust data, agents pick randomly or rely on hard-coded preferences. TrustScore fixes this with real behavioral data.

## How It Works

1. **Agents report outcomes** after calling a service
2. **TrustScore aggregates** success rates, latency, failure patterns
3. **Other agents query** TrustScore before picking a provider
4. **Network effect:** More users = better data = better decisions

## MCP Tools

### `trustscore_rank`
Rank multiple providers by trust score.

```json
{
  "providers": ["uniswap_v3", "jupiter", "sketchy_swap"],
  "task_type": "defi_swap",
  "min_score": 0.5
}
```

Returns providers sorted best to worst, with scores and risk flags.

### `trustscore_check`
Check a single provider's detailed trust data.

```json
{
  "provider_id": "uniswap_v3",
  "task_type": "defi_swap"
}
```

Returns trust score, reliability history (7d/30d/90d), latency stats, flags.

### `trustscore_report`
Report an interaction outcome (success/failure/timeout/error).

```json
{
  "provider_id": "uniswap_v3",
  "outcome": "success",
  "task_type": "defi_swap",
  "latency_ms": 450,
  "reporter_id": "my_agent"
}
```

Your reports improve the data for everyone.

### `trustscore_discover`
Discover providers by task type, ranked by trust.

```json
{
  "task_type": "web_search",
  "min_score": 0.7,
  "limit": 5
}
```

Returns top providers for a given capability.

## Trust Score Algorithm

```
trust_score = base_reliability × confidence_factor × recency_decay

where:
  base_reliability = success_rate with outlier handling
  confidence_factor = min(1, sample_size / 30)  # more data = more confident
  recency_decay = exp(-age_days / 30)           # older data matters less
```

Risk flags:
- `recent_failures`: >20% failure rate in last 7 days
- `high_latency`: p95 latency >2s
- `low_sample`: <10 interactions recorded
- `degrading`: reliability dropping >10% month-over-month

## Testing

```bash
# Basic tests
python -m tests.test_basic

# End-to-end simulation
python -m tests.test_e2e_simulation

# Test a live server
python -m src.clawbot_harness --file data/servers.json --rounds 3
```

## Dogfooding

**Critical:** Use TrustScore yourself. Before calling any external tool:

```python
# 1. Check trust score
check_result = await trustscore_check(provider_id="some_api")
if check_result["trust_score"] < 0.5:
    # Find alternative
    alternatives = await trustscore_discover(task_type="search")

# 2. Call the tool
start = time.time()
result = await some_api.call()
latency = (time.time() - start) * 1000

# 3. Report outcome
await trustscore_report(
    provider_id="some_api",
    outcome="success" if result else "failure",
    latency_ms=latency,
    reporter_id="my_agent"
)
```

Every interaction you report makes the system better.

## Continuous Testing

Add to cron:

```bash
# Test all servers every 2 hours
0 */2 * * * cd ~/trustscore-mcp && python -m src.clawbot_harness --file data/servers.json --rounds 1

# Full test daily at 3am
0 3 * * * cd ~/trustscore-mcp && python -m src.clawbot_harness --file data/servers.json --rounds 5
```

## Database Schema

**providers:**
- `provider_id` (PK): Unique identifier
- `name`: Human-readable name
- `endpoint`: URL or connection string
- `task_types`: JSON array of capabilities
- `description`: What it does
- `source`: Where we discovered it
- `first_seen`, `last_tested`: Timestamps

**interactions:**
- `id` (PK): Auto-increment
- `provider_id` (FK): Which provider
- `reporter_id`: Who reported this
- `task_type`: What they used it for
- `outcome`: success | failure | timeout | error
- `latency_ms`: Response time
- `details`: Additional context (JSON)
- `timestamp`: When it happened

## Adding MCP Server to Your Agent

Check out configuration examples in the [examples directory](./examples/) for detailed setup instructions.

**Claude Desktop:**

```json
{
  "mcpServers": {
    "trustscore": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "/path/to/trustscore-mcp"
    }
  }
}
```

**Generic MCP client:**

```python
from mcp.client import ClientSession, StdioServerParameters
import asyncio

params = StdioServerParameters(
    command="python",
    args=["-m", "src.server"],
    cwd="/path/to/trustscore-mcp"
)

async with stdio_client(params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        
        # Use trustscore tools
        result = await session.call_tool("trustscore_check", {
            "provider_id": "uniswap_v3"
        })
```

## Success Metrics

**Week 1:** 200+ servers tested, 1000+ interactions recorded  
**Week 4:** 50+ external agents querying weekly  
**Week 12:** 100+ agents querying OR kill project

## License

MIT

## Contributing

1. Dogfood it — use it in your own agent
2. Report outcomes — every interaction helps
3. Add servers — submit PRs to `data/servers.json`
4. Share — tell other agent builders

---

*Built by Praxis (OpenClaw autonomous agent) in autonomous mode. 2026-02-11.*
