# TrustScore MCP Server

The credit score for AI agents. One API call to know which providers to trust.

## What It Does

Agents discover providers via A2A or MCP Registry. TrustScore tells them which ones are actually good.

```
Agent discovers 15 providers → calls trustscore_rank → gets ranked list → picks the best one
```

## Quick Start

### Install

```bash
pip install -e .
```

### Run the MCP Server

```bash
python -m src.server
```

### Add to your MCP config (Claude, Cursor, etc.)

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

## Tools

### trustscore_rank
Rank multiple providers. Give it a list, get back a ranked list with scores.

### trustscore_check
Check a single provider. Get trust score, reliability history, risk flags.

### trustscore_report
Report an interaction outcome. Contribute data, get better scores for everyone.

### trustscore_discover
Find trusted providers for a task type. Don't have candidates? We'll suggest them.

## Seed Data

Run ClawBot to test MCP servers and populate the database:

```bash
# Test curated seed servers
python -m src.clawbot_harness --seed-only

# Test servers from the registry
python -m src.clawbot_harness

# Test a specific server
python -m src.clawbot_harness --url https://server.example.com --name my_server

# Multiple rounds for more data
python -m src.clawbot_harness --rounds 10
```

## How Scoring Works

- **Beta Distribution**: Each provider has success/failure counts. Score = Bayesian posterior mean.
- **Confidence**: Higher sample size = higher confidence. Scores stabilize over time.
- **Recency**: Recent interactions weighted more heavily (30-day half-life).
- **Flags**: Automatic risk flags for low samples, recent failures, high latency, degradation.

## Run Tests

```bash
python -m tests.test_basic
python -m tests.test_e2e_simulation
```

## Project Structure

```
trustscore-mcp/
├── src/
│   ├── server.py          # MCP server (4 tools)
│   ├── database.py         # SQLite + scoring logic
│   └── clawbot_harness.py  # Data collection harness
├── tests/
│   ├── test_basic.py       # Unit tests
│   └── test_e2e_simulation.py  # Full simulation
├── pyproject.toml
└── README.md
```

## License

MIT
