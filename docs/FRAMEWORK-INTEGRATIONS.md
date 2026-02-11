# Framework Integrations

## Overview
TrustScore MCP Server can be integrated into any MCP-compatible AI agent framework. This guide covers the two most popular frameworks: **LangGraph** and **CrewAI**.

## LangGraph Integration

### Installation
```bash
pip install langchain-mcp-adapters
```

### Quick Start
```python
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent

async def main():
    # Connect to TrustScore MCP server
    client = MultiServerMCPClient({
        "trustscore": {
            "transport": "stdio",
            "command": "node",
            "args": ["/path/to/trustscore/dist/index.js"]
        }
    })
    
    # Get TrustScore tools
    tools = await client.get_tools()
    
    # Create agent with TrustScore tools
    agent = create_agent("claude-sonnet-4-5-20250929", tools)
    
    # Use TrustScore in agent workflow
    response = await agent.ainvoke({
        "messages": [{
            "role": "user", 
            "content": "Check trust score for github_api before fetching data"
        }]
    })
    
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

### Advanced: Tool Interceptors for Auto-Scoring

Use interceptors to automatically check trust scores before external calls:

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.interceptors import MCPToolCallRequest
from langchain.messages import ToolMessage

async def auto_trust_check(
    request: MCPToolCallRequest,
    handler,
):
    """Automatically check trust score before external tool calls."""
    
    # List of external tools that need trust checking
    external_tools = ["github_api", "stripe_api", "openai_api"]
    
    if request.name in external_tools:
        # Get trust score from TrustScore server
        # (assumes client has trustscore server configured)
        trust_result = await request.runtime.invoke_tool(
            "trustscore_check",
            {"provider_id": request.name}
        )
        
        # Parse trust score
        trust_score = float(trust_result.content.split("score: ")[1].split(",")[0])
        
        # Block if trust score too low
        if trust_score < 0.5:
            return ToolMessage(
                content=f"Blocked: {request.name} trust score ({trust_score}) below threshold (0.5)",
                tool_call_id=request.runtime.tool_call_id,
            )
        
        # Log trust check
        print(f"✓ {request.name} trust score: {trust_score}")
    
    # Continue with tool execution
    result = await handler(request)
    
    # Report outcome to TrustScore
    success = "error" not in result.content.lower()
    await request.runtime.invoke_tool(
        "trustscore_report",
        {
            "provider_id": request.name,
            "success": success,
            "latency_ms": 100,  # Measure actual latency
            "error_message": None if success else result.content
        }
    )
    
    return result

# Use interceptor
client = MultiServerMCPClient(
    {
        "trustscore": {...},
        "external_tools": {...}
    },
    tool_interceptors=[auto_trust_check],
)
```

### HTTP Transport (Remote TrustScore Server)

```python
client = MultiServerMCPClient({
    "trustscore": {
        "transport": "http",
        "url": "http://localhost:3000/mcp",
        "headers": {
            "Authorization": "Bearer your_token"
        }
    }
})
```

### Stateful Sessions

For persistent scoring context:

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain.agents import create_agent

client = MultiServerMCPClient({...})

async with client.session("trustscore") as session:
    tools = await load_mcp_tools(session)
    agent = create_agent("claude-sonnet-4-5-20250929", tools)
    
    # All tool calls in this session share trust score state
    result = await agent.ainvoke({"messages": [...]})
```

### Resources: Trust Score History

Access trust score data as resources:

```python
# Load trust score history as Blob objects
blobs = await client.get_resources(
    "trustscore",
    uris=["trustscore://history/github_api"]
)

for blob in blobs:
    print(f"Provider: {blob.metadata['uri']}")
    print(blob.as_string())  # JSON history data
```

---

## CrewAI Integration

### Installation
```bash
pip install 'crewai-tools[mcp]'
# or
uv add mcp
```

### Quick Start (Recommended: DSL)

```python
from crewai import Agent, Task, Crew
from crewai.mcp import MCPServerStdio

# Create agent with TrustScore tools
trust_aware_agent = Agent(
    role="API Integration Specialist",
    goal="Safely integrate with external APIs using trust scores",
    backstory="Expert at evaluating API reliability before integration",
    mcps=[
        MCPServerStdio(
            command="node",
            args=["/path/to/trustscore/dist/index.js"],
        )
    ]
)

# Create task
integration_task = Task(
    description="Check trust score for stripe_api and integrate if reliable",
    expected_output="Integration status and trust assessment",
    agent=trust_aware_agent
)

# Run crew
crew = Crew(agents=[trust_aware_agent], tasks=[integration_task])
result = crew.kickoff()
```

### Multiple Servers (TrustScore + External APIs)

```python
from crewai import Agent
from crewai.mcp import MCPServerStdio, MCPServerHTTP

agent = Agent(
    role="Full-Stack Integrator",
    goal="Integrate APIs with trust scoring",
    backstory="Expert at safe API integration",
    mcps=[
        # TrustScore for scoring
        MCPServerStdio(
            command="node",
            args=["/path/to/trustscore/dist/index.js"],
        ),
        # External APIs to score
        MCPServerHTTP(
            url="https://api.github.com/mcp",
            headers={"Authorization": "Bearer github_token"},
        ),
        MCPServerHTTP(
            url="https://api.stripe.com/mcp",
            headers={"Authorization": "Bearer stripe_token"},
        ),
    ]
)
```

### Tool Filtering (Security Best Practice)

Allow only specific TrustScore tools:

```python
from crewai.mcp import MCPServerStdio
from crewai.mcp.filters import create_static_tool_filter

agent = Agent(
    role="Read-Only Analyst",
    goal="Analyze trust scores without modifying data",
    backstory="Security-conscious analyst",
    mcps=[
        MCPServerStdio(
            command="node",
            args=["/path/to/trustscore/dist/index.js"],
            tool_filter=create_static_tool_filter(
                allowed_tool_names=[
                    "trustscore_check",
                    "trustscore_rank",
                    "trustscore_discover"
                ],
                blocked_tool_names=["trustscore_report"]  # Read-only
            ),
        )
    ]
)
```

### Dynamic Filtering (Context-Aware)

```python
from crewai.mcp import MCPServerStdio
from crewai.mcp.filters import create_dynamic_tool_filter, ToolFilterContext

def role_based_filter(context: ToolFilterContext, tool: dict) -> bool:
    """Block trust reporting for junior analysts."""
    if context.agent.role == "Junior Analyst":
        if "report" in tool.get("name", "").lower():
            return False  # Block reporting tools
    return True

agent = Agent(
    role="Junior Analyst",
    goal="View trust scores safely",
    backstory="Learning to work with trust data",
    mcps=[
        MCPServerStdio(
            command="node",
            args=["/path/to/trustscore/dist/index.js"],
            tool_filter=role_based_filter,
        )
    ]
)
```

### Advanced: MCPServerAdapter

For manual connection management:

```python
from crewai import Agent
from crewai_tools import MCPServerAdapter

server_params = {
    "url": "http://localhost:3000/mcp",
    "transport": "streamable-http"
}

with MCPServerAdapter(server_params, connect_timeout=60) as trustscore_tools:
    print(f"Available tools: {[tool.name for tool in trustscore_tools]}")
    
    agent = Agent(
        role="Trust Scorer",
        goal="Use TrustScore tools",
        backstory="Expert trust evaluator",
        tools=trustscore_tools,
        verbose=True
    )
    
    # Use in crew...
```

### Using with CrewBase

```python
from crewai import CrewBase, agent, task
from mcp import StdioServerParameters
import os

@CrewBase
class TrustScoringCrew:
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"
    
    mcp_server_params = [
        # TrustScore Server
        StdioServerParameters(
            command="node",
            args=["/path/to/trustscore/dist/index.js"],
            env={"NODE_ENV": "production", **os.environ}
        ),
        # External API servers...
    ]
    
    mcp_connect_timeout = 60  # 60 seconds
    
    @agent
    def trust_analyst(self):
        return Agent(
            config=self.agents_config["trust_analyst"],
            tools=self.get_mcp_tools()  # All tools
        )
    
    @agent
    def integration_engineer(self):
        return Agent(
            config=self.agents_config["integration_engineer"],
            tools=self.get_mcp_tools(
                "trustscore_check",
                "trustscore_report"
            )  # Filtered tools
        )
    
    @task
    def score_providers(self):
        return Task(
            config=self.tasks_config["score_providers"],
            agent=self.trust_analyst()
        )
```

---

## Common Patterns

### Pattern 1: Pre-Flight Trust Check

Before calling an external API, check its trust score:

```python
# 1. Check trust score
trust_response = await agent.ainvoke({
    "messages": [{
        "role": "user",
        "content": "Check trust score for stripe_api"
    }]
})

# 2. Parse score (example: "score: 0.85")
trust_score = extract_score(trust_response)

# 3. Decide whether to proceed
if trust_score >= 0.7:
    # Proceed with Stripe API call
    api_response = await agent.ainvoke({
        "messages": [{
            "role": "user",
            "content": "Create Stripe payment for $100"
        }]
    })
else:
    # Fallback or alert
    print(f"Warning: stripe_api trust score too low ({trust_score})")
```

### Pattern 2: Post-Call Outcome Reporting

After calling an external API, report the outcome:

```python
# 1. Call external API
api_response = await call_external_api()

# 2. Report outcome to TrustScore
await agent.ainvoke({
    "messages": [{
        "role": "user",
        "content": f"Report trustscore for github_api: success={api_response.ok}, latency={api_response.latency_ms}ms"
    }]
})
```

### Pattern 3: Provider Discovery

Find trusted providers by category:

```python
# Discover file storage providers
discovery_response = await agent.ainvoke({
    "messages": [{
        "role": "user",
        "content": "Discover MCP servers in category: file-storage"
    }]
})

# Returns ranked list of providers with trust scores
```

### Pattern 4: Trust-Based Routing

Route requests to the most trusted provider:

```python
# Get ranked providers for a task
ranked_response = await agent.ainvoke({
    "messages": [{
        "role": "user",
        "content": "Rank providers by trust score, limit 5"
    }]
})

# Use top-ranked provider
top_provider = parse_top_provider(ranked_response)
result = await call_provider(top_provider)
```

---

## Configuration Examples

### Development (Local)

```python
# LangGraph
client = MultiServerMCPClient({
    "trustscore": {
        "transport": "stdio",
        "command": "npm",
        "args": ["run", "dev"],
        "env": {"NODE_ENV": "development"}
    }
})

# CrewAI
mcps=[
    MCPServerStdio(
        command="npm",
        args=["run", "dev"],
        env={"NODE_ENV": "development"}
    )
]
```

### Production (Remote)

```python
# LangGraph
client = MultiServerMCPClient({
    "trustscore": {
        "transport": "http",
        "url": "https://trustscore.example.com/mcp",
        "headers": {
            "Authorization": "Bearer prod_token_xyz"
        }
    }
})

# CrewAI
mcps=[
    MCPServerHTTP(
        url="https://trustscore.example.com/mcp",
        headers={"Authorization": "Bearer prod_token_xyz"},
        streamable=True,
    )
]
```

---

## Testing

### Unit Testing with Mock Server

```python
import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_trust_check():
    # Mock TrustScore server
    mock_client = AsyncMock()
    mock_client.get_tools.return_value = [
        MockTool("trustscore_check", returns={"score": 0.85})
    ]
    
    # Test agent behavior
    agent = create_agent("gpt-4", await mock_client.get_tools())
    result = await agent.ainvoke({
        "messages": [{"role": "user", "content": "Check trust for github_api"}]
    })
    
    assert "0.85" in result["messages"][-1]["content"]
```

### Integration Testing

```python
@pytest.mark.integration
async def test_full_workflow():
    # Start real TrustScore server
    server = start_trustscore_server()
    
    try:
        # Connect agent
        client = MultiServerMCPClient({
            "trustscore": {
                "transport": "http",
                "url": f"http://localhost:{server.port}/mcp"
            }
        })
        
        # Test workflow
        tools = await client.get_tools()
        assert len(tools) == 4  # 4 TrustScore tools
        
        # Test each tool
        # ...
    finally:
        server.stop()
```

---

## Best Practices

### 1. **Use Tool Filtering**
Only expose necessary TrustScore tools to each agent (principle of least privilege).

### 2. **Cache Tool Lists**
Enable `cache_tools_list=True` for faster subsequent connections:
```python
mcps=[
    MCPServerStdio(
        command="node",
        args=["/path/to/trustscore/dist/index.js"],
        cache_tools_list=True,  # ← Enable caching
    )
]
```

### 3. **Handle Timeouts**
Configure appropriate timeouts for remote servers:
```python
client = MultiServerMCPClient({...}, connect_timeout=60)
```

### 4. **Secure Remote Connections**
Always use HTTPS and authentication for production:
```python
MCPServerHTTP(
    url="https://trustscore.example.com/mcp",
    headers={"Authorization": "Bearer secure_token"},
)
```

### 5. **Monitor Trust Scores**
Log trust scores to detect provider degradation:
```python
async def log_trust_score(provider_id: str, score: float):
    logger.info(f"Trust score for {provider_id}: {score}")
    if score < 0.5:
        logger.warning(f"LOW TRUST: {provider_id} score below threshold")
```

---

## Troubleshooting

### Connection Refused

**Error:** `Connection refused to localhost:3000`

**Solution:**
- Ensure TrustScore server is running: `npm start`
- Check port matches configuration
- For HTTP transport, verify server is listening on correct interface

### Tool Not Found

**Error:** `Tool 'trustscore_check' not found`

**Solution:**
- Verify TrustScore server is running
- Check tool names match exactly (case-sensitive)
- Enable verbose logging: `verbose=True` (CrewAI) or set `LANGCHAIN_VERBOSE=true` (LangGraph)

### Timeout Errors

**Error:** `Connection timeout after 30 seconds`

**Solution:**
- Increase timeout: `connect_timeout=60`
- Check server performance (slow startup?)
- Verify network connectivity (remote servers)

### Authentication Failed

**Error:** `401 Unauthorized`

**Solution:**
- Verify API token is valid
- Check headers match server expectations
- Ensure token has required permissions

---

## Resources

- **LangChain MCP Adapters**: https://github.com/langchain-ai/langchain-mcp-adapters
- **LangChain Docs**: https://docs.langchain.com/oss/python/langchain/mcp
- **CrewAI MCP Docs**: https://docs.crewai.com/en/mcp/overview
- **CrewAI MCP Demo**: https://github.com/tonykipkemboi/crewai-mcp-demo
- **MCP Specification**: https://modelcontextprotocol.io/
- **TrustScore GitHub**: https://github.com/bensargotest-sys/trustscore

---

## Next Steps

1. **Try the examples** in `examples/` directory
2. **Read the MCP Spec** to understand primitives (tools, resources, prompts)
3. **Join the community** on Discord/GitHub for support
4. **Build your integration** using these patterns

Questions? Open an issue on GitHub or join our Discord!
