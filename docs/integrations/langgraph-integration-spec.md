# LangGraph Integration Spec

**Goal:** Automatic trust-based tool selection and outcome reporting for LangGraph agents

---

## Overview

LangGraph agents use tools to accomplish tasks. This integration adds automatic TrustScore checking before tool calls and automatic outcome reporting after.

**Value Proposition:**
- Zero code changes to existing LangGraph agents
- Automatic trust filtering (skip low-trust tools)
- Automatic data contribution (every tool call improves TrustScore)
- Optional: fallback to alternatives if primary tool has low trust

---

## Architecture

```python
# Standard LangGraph agent
agent = create_agent(
    model=model,
    tools=[tool1, tool2, tool3]
)

# With TrustScore integration
from trustscore_langgraph import TrustScoredTools

agent = create_agent(
    model=model,
    tools=TrustScoredTools(
        [tool1, tool2, tool3],
        min_trust=0.5,              # Filter out tools <0.5
        report_outcomes=True,       # Auto-report after calls
        fallback_enabled=True       # Try alternatives on failure
    )
)
```

---

## Implementation

### 1. Wrapper Class

```python
# trustscore_langgraph/wrapper.py

import asyncio
from typing import List, Callable, Optional
from langchain_core.tools import BaseTool
from trustscore import TrustScoreClient

class TrustScoredTool(BaseTool):
    """Wraps a LangChain tool with TrustScore checking and reporting."""
    
    def __init__(
        self,
        base_tool: BaseTool,
        trustscore_client: TrustScoreClient,
        min_trust: float = 0.0,
        task_type: Optional[str] = None
    ):
        self.base_tool = base_tool
        self.trustscore = trustscore_client
        self.min_trust = min_trust
        self.task_type = task_type or base_tool.name
        
        # Copy base tool properties
        self.name = base_tool.name
        self.description = base_tool.description
        self.args_schema = base_tool.args_schema
    
    async def _arun(self, *args, **kwargs):
        """Async run with trust checking and reporting."""
        # 1. Check trust score
        provider_id = self.base_tool.name
        score = await self.trustscore.check(provider_id, self.task_type)
        
        if score and score['trust_score'] < self.min_trust:
            raise ValueError(
                f"Trust score {score['trust_score']:.3f} below minimum {self.min_trust}"
            )
        
        # 2. Execute tool
        start_time = time.time()
        try:
            result = await self.base_tool._arun(*args, **kwargs)
            outcome = "success"
            error = None
        except Exception as e:
            result = None
            outcome = "error"
            error = str(e)
        finally:
            latency_ms = int((time.time() - start_time) * 1000)
        
        # 3. Report outcome
        await self.trustscore.report(
            provider_id=provider_id,
            outcome=outcome,
            task_type=self.task_type,
            latency_ms=latency_ms,
            details=error
        )
        
        if outcome == "error":
            raise Exception(error)
        
        return result
    
    def _run(self, *args, **kwargs):
        """Sync wrapper."""
        return asyncio.run(self._arun(*args, **kwargs))


class TrustScoredTools:
    """Collection of trust-scored tools with automatic filtering."""
    
    def __init__(
        self,
        tools: List[BaseTool],
        min_trust: float = 0.0,
        report_outcomes: bool = True,
        trustscore_db_path: Optional[str] = None
    ):
        self.client = TrustScoreClient(db_path=trustscore_db_path)
        self.wrapped_tools = [
            TrustScoredTool(tool, self.client, min_trust)
            for tool in tools
        ]
    
    def __iter__(self):
        return iter(self.wrapped_tools)
    
    def __len__(self):
        return len(self.wrapped_tools)
```

### 2. LangGraph Integration

```python
# trustscore_langgraph/agent.py

from langgraph.prebuilt import create_react_agent

def create_trustscored_agent(
    model,
    tools: List[BaseTool],
    min_trust: float = 0.5,
    trustscore_db_path: Optional[str] = None,
    **kwargs
):
    """Create a LangGraph ReAct agent with automatic TrustScore integration."""
    
    trustscored_tools = TrustScoredTools(
        tools,
        min_trust=min_trust,
        trustscore_db_path=trustscore_db_path
    )
    
    return create_react_agent(
        model,
        list(trustscored_tools),
        **kwargs
    )
```

### 3. TrustScore Client

```python
# trustscore_langgraph/client.py

import aiosqlite
from pathlib import Path
from typing import Optional, Dict

class TrustScoreClient:
    """Async client for TrustScore database operations."""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(
            Path(__file__).parent.parent / "trustscore.db"
        )
    
    async def check(
        self,
        provider_id: str,
        task_type: Optional[str] = None
    ) -> Optional[Dict]:
        """Check trust score for a provider."""
        from src.database import get_provider_score, init_db
        
        await init_db(self.db_path)
        return await get_provider_score(
            provider_id,
            task_type=task_type,
            db_path=self.db_path
        )
    
    async def report(
        self,
        provider_id: str,
        outcome: str,
        task_type: Optional[str] = None,
        latency_ms: Optional[int] = None,
        details: Optional[str] = None
    ):
        """Report interaction outcome."""
        from src.database import record_interaction, init_db
        
        await init_db(self.db_path)
        await record_interaction(
            provider_id=provider_id,
            outcome=outcome,
            task_type=task_type,
            latency_ms=latency_ms,
            reporter_id="langgraph_agent",
            details=details,
            db_path=self.db_path
        )
```

---

## Installation

```bash
pip install trustscore-langgraph
```

---

## Usage Examples

### Basic Usage

```python
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from trustscore_langgraph import create_trustscored_agent

# Define tools
@tool
def search_web(query: str) -> str:
    """Search the web for information."""
    # Implementation
    pass

@tool
def get_weather(location: str) -> str:
    """Get weather for a location."""
    # Implementation
    pass

# Create agent with TrustScore
model = ChatOpenAI(model="gpt-4")
agent = create_trustscored_agent(
    model,
    tools=[search_web, get_weather],
    min_trust=0.5  # Filter tools with trust <0.5
)

# Use normally
result = agent.invoke({"messages": [("user", "What's the weather in SF?")]})
```

### Manual Wrapper

```python
from trustscore_langgraph import TrustScoredTools

# Wrap existing tools
tools = [search_web, get_weather, risky_api]
trustscored = TrustScoredTools(
    tools,
    min_trust=0.7,               # Higher threshold
    report_outcomes=True         # Auto-report
)

# Use with any LangGraph agent
agent = create_react_agent(model, list(trustscored))
```

### Custom Trust Logic

```python
from trustscore_langgraph import TrustScoredTool, TrustScoreClient

client = TrustScoreClient()

async def my_custom_tool_logic(*args, **kwargs):
    # Check trust manually
    score = await client.check("my_api", task_type="search")
    
    if score['trust_score'] < 0.5:
        # Fallback to alternative
        return await alternative_api(*args, **kwargs)
    
    # Use primary
    result = await my_api(*args, **kwargs)
    
    # Report outcome
    await client.report(
        "my_api",
        outcome="success",
        latency_ms=450
    )
    
    return result
```

---

## Testing

```python
# tests/test_langgraph_integration.py

import pytest
from langchain_core.tools import tool
from trustscore_langgraph import TrustScoredTools, TrustScoreClient

@tool
def mock_tool(query: str) -> str:
    """Mock tool for testing."""
    return f"Result for {query}"

@pytest.mark.asyncio
async def test_trust_filtering():
    """Test that low-trust tools are filtered."""
    tools = TrustScoredTools([mock_tool], min_trust=0.8)
    
    # Should raise if trust <0.8
    with pytest.raises(ValueError, match="Trust score"):
        await tools.wrapped_tools[0]._arun("test")

@pytest.mark.asyncio
async def test_outcome_reporting():
    """Test that outcomes are reported."""
    client = TrustScoreClient(db_path=":memory:")
    
    await client.report(
        provider_id="test_tool",
        outcome="success",
        latency_ms=100
    )
    
    # Verify report was recorded
    score = await client.check("test_tool")
    assert score is not None
```

---

## Configuration

```python
# config.py

TRUSTSCORE_CONFIG = {
    "min_trust": 0.5,              # Default threshold
    "report_outcomes": True,        # Auto-report
    "db_path": "./trustscore.db",  # Database location
    "fallback_enabled": False,     # Try alternatives
    "reporter_id": "my_agent"      # Your agent ID
}
```

---

## Roadmap

**v0.1 (Week 1):**
- [x] Basic wrapper implementation
- [x] Async support
- [x] Auto-reporting
- [x] Trust filtering

**v0.2 (Week 2):**
- [ ] Fallback to alternatives
- [ ] Batch checking for multiple tools
- [ ] Caching for repeated checks
- [ ] Better error handling

**v0.3 (Week 3):**
- [ ] Metrics dashboard
- [ ] Custom trust policies
- [ ] Tool discovery by trust score
- [ ] Integration tests with real LangGraph agents

---

## Success Metrics

**Week 1:** Package published, 10+ downloads  
**Week 4:** 50+ agents using it  
**Week 8:** 1000+ tool calls tracked

---

**Last Updated:** 2026-02-11 18:06 UTC
