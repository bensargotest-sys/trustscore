# CrewAI Integration Spec

**Goal:** Automatic trust-based tool selection and outcome reporting for CrewAI agents

---

## Overview

CrewAI agents use tools to accomplish tasks. This integration adds automatic TrustScore checking before tool execution and automatic outcome reporting after.

**Value Proposition:**
- Minimal config (`trust_selection=True`)
- Automatic trust filtering
- Automatic data contribution
- Works with existing CrewAI setups

---

## Architecture

```python
from crewai import Agent, Task, Crew
from trustscore_crewai import TrustScoredToolkit

# Standard CrewAI agent
agent = Agent(
    role="Researcher",
    goal="Find information",
    tools=[tool1, tool2, tool3]
)

# With TrustScore
agent = Agent(
    role="Researcher",
    goal="Find information",
    tools=TrustScoredToolkit(
        [tool1, tool2, tool3],
        min_trust=0.5
    )
)
```

---

## Implementation

### 1. TrustScored Tool Wrapper

```python
# trustscore_crewai/wrapper.py

from crewai_tools import BaseTool
from trustscore import TrustScoreClient
import time

class TrustScoredTool(BaseTool):
    """Wraps a CrewAI tool with TrustScore integration."""
    
    base_tool: BaseTool
    trustscore_client: TrustScoreClient
    min_trust: float = 0.0
    task_type: str = None
    
    def __init__(self, base_tool, client, min_trust=0.0):
        super().__init__()
        self.base_tool = base_tool
        self.trustscore_client = client
        self.min_trust = min_trust
        self.task_type = base_tool.name
        
        # Inherit properties
        self.name = base_tool.name
        self.description = base_tool.description
        self.args_schema = base_tool.args_schema
    
    def _run(self, *args, **kwargs):
        """Execute with trust checking."""
        # 1. Check trust
        provider_id = self.base_tool.name
        score = self.trustscore_client.check_sync(
            provider_id,
            self.task_type
        )
        
        if score and score['trust_score'] < self.min_trust:
            return f"Error: {provider_id} has low trust score ({score['trust_score']:.3f}). Skipping."
        
        # 2. Execute
        start = time.time()
        try:
            result = self.base_tool._run(*args, **kwargs)
            outcome = "success"
            error = None
        except Exception as e:
            result = str(e)
            outcome = "error"
            error = str(e)
        finally:
            latency_ms = int((time.time() - start) * 1000)
        
        # 3. Report
        self.trustscore_client.report_sync(
            provider_id=provider_id,
            outcome=outcome,
            task_type=self.task_type,
            latency_ms=latency_ms,
            details=error
        )
        
        return result


class TrustScoredToolkit:
    """Collection of trust-scored tools for CrewAI."""
    
    def __init__(
        self,
        tools,
        min_trust=0.5,
        trustscore_db_path=None
    ):
        self.client = TrustScoreClient(db_path=trustscore_db_path)
        self.wrapped = [
            TrustScoredTool(tool, self.client, min_trust)
            for tool in tools
        ]
    
    def __iter__(self):
        return iter(self.wrapped)
    
    def __len__(self):
        return len(self.wrapped)
```

### 2. Sync Client

```python
# trustscore_crewai/client.py

import asyncio
from typing import Optional, Dict

class TrustScoreClient:
    """Sync-friendly TrustScore client for CrewAI."""
    
    def __init__(self, db_path=None):
        self.db_path = db_path or "trustscore.db"
        self._loop = None
    
    def _get_loop(self):
        if self._loop is None:
            try:
                self._loop = asyncio.get_event_loop()
            except RuntimeError:
                self._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._loop)
        return self._loop
    
    def check_sync(self, provider_id, task_type=None):
        """Sync wrapper for trust check."""
        from src.database import get_provider_score, init_db
        
        async def _check():
            await init_db(self.db_path)
            return await get_provider_score(
                provider_id,
                task_type=task_type,
                db_path=self.db_path
            )
        
        loop = self._get_loop()
        return loop.run_until_complete(_check())
    
    def report_sync(
        self,
        provider_id,
        outcome,
        task_type=None,
        latency_ms=None,
        details=None
    ):
        """Sync wrapper for outcome reporting."""
        from src.database import record_interaction, init_db
        
        async def _report():
            await init_db(self.db_path)
            await record_interaction(
                provider_id=provider_id,
                outcome=outcome,
                task_type=task_type,
                latency_ms=latency_ms,
                reporter_id="crewai_agent",
                details=details,
                db_path=self.db_path
            )
        
        loop = self._get_loop()
        loop.run_until_complete(_report())
```

---

## Installation

```bash
pip install trustscore-crewai
```

---

## Usage Examples

### Basic Usage

```python
from crewai import Agent, Task, Crew
from crewai_tools import tool
from trustscore_crewai import TrustScoredToolkit

# Define tools
@tool
def search_web(query: str) -> str:
    """Search the web."""
    # Implementation
    pass

@tool
def scrape_website(url: str) -> str:
    """Scrape a website."""
    # Implementation
    pass

# Create agent with TrustScore
researcher = Agent(
    role="Researcher",
    goal="Find accurate information",
    backstory="Expert at web research",
    tools=TrustScoredToolkit(
        [search_web, scrape_website],
        min_trust=0.5
    )
)

# Create task and crew
task = Task(
    description="Research AI trends in 2026",
    agent=researcher
)

crew = Crew(
    agents=[researcher],
    tasks=[task]
)

# Run - trust checking happens automatically
result = crew.kickoff()
```

### Multiple Agents

```python
from trustscore_crewai import TrustScoredToolkit

# Different trust thresholds per agent
researcher_tools = TrustScoredToolkit(
    [search_tool, scrape_tool],
    min_trust=0.5  # Moderate threshold
)

analyst_tools = TrustScoredToolkit(
    [data_tool, chart_tool],
    min_trust=0.7  # High threshold (critical work)
)

researcher = Agent(
    role="Researcher",
    tools=researcher_tools
)

analyst = Agent(
    role="Analyst",
    tools=analyst_tools
)

crew = Crew(agents=[researcher, analyst], tasks=[...])
```

---

## Configuration

```python
# config.py

TRUSTSCORE_CREWAI_CONFIG = {
    "min_trust": 0.5,
    "db_path": "./trustscore.db",
    "reporter_id": "crewai_agent",
    "auto_report": True
}
```

---

## Testing

```python
# tests/test_crewai_integration.py

from crewai_tools import tool
from trustscore_crewai import TrustScoredToolkit

@tool
def mock_tool(input: str) -> str:
    """Mock tool."""
    return f"Result: {input}"

def test_tool_wrapping():
    """Test that tools are wrapped correctly."""
    toolkit = TrustScoredToolkit([mock_tool], min_trust=0.5)
    
    assert len(toolkit) == 1
    assert toolkit.wrapped[0].name == "mock_tool"

def test_trust_filtering():
    """Test low-trust tools are handled."""
    toolkit = TrustScoredToolkit([mock_tool], min_trust=0.9)
    
    # Should return error message if trust <0.9
    result = toolkit.wrapped[0]._run("test")
    assert "low trust score" in result.lower() or "Result" in result
```

---

## Integration with Existing CrewAI Projects

### Option 1: Drop-in Replacement

```python
# Before
agent = Agent(tools=[tool1, tool2])

# After
from trustscore_crewai import TrustScoredToolkit
agent = Agent(tools=TrustScoredToolkit([tool1, tool2]))
```

### Option 2: Selective Wrapping

```python
from trustscore_crewai import TrustScoredTool, TrustScoreClient

client = TrustScoreClient()

# Wrap only high-risk tools
safe_tool = SafeAPITool()
risky_tool = TrustScoredTool(RiskyAPITool(), client, min_trust=0.7)

agent = Agent(tools=[safe_tool, risky_tool])
```

---

## Roadmap

**v0.1 (Week 1):**
- [x] Basic wrapper
- [x] Sync client
- [x] Trust filtering
- [x] Auto-reporting

**v0.2 (Week 2):**
- [ ] Crew-level trust policies
- [ ] Dashboard integration
- [ ] Better error messages
- [ ] Caching

**v0.3 (Week 3):**
- [ ] Tool discovery by trust
- [ ] Fallback mechanisms
- [ ] Agent-specific trust profiles
- [ ] Metrics export

---

## Success Metrics

**Week 1:** Package published  
**Week 4:** 50+ crews using it  
**Week 8:** 1000+ tool calls tracked

---

**Last Updated:** 2026-02-11 18:08 UTC
