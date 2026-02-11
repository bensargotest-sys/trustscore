"""TrustScore MCP Server — Trust and reputation scores for AI agent service selection."""

import asyncio
import json
import time
from datetime import datetime, timezone

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from . import database as db

server = Server("trustscore")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """Register the 4 TrustScore tools."""
    return [
        Tool(
            name="trustscore_rank",
            description=(
                "Rank multiple providers by trust score. Use this when your agent has "
                "discovered several providers and needs to pick the best one. Returns "
                "providers sorted by trust score with reliability data and risk flags."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "providers": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of provider IDs to rank",
                    },
                    "task_type": {
                        "type": "string",
                        "description": "Optional task domain (e.g., 'defi_swap', 'web_search')",
                    },
                    "min_score": {
                        "type": "number",
                        "description": "Minimum trust score threshold (0-1). Default 0.",
                        "default": 0,
                    },
                },
                "required": ["providers"],
            },
        ),
        Tool(
            name="trustscore_check",
            description=(
                "Check the trust score of a single provider. Returns detailed reliability "
                "data including 7d/30d/90d history, latency, success rates, and risk flags."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "provider_id": {
                        "type": "string",
                        "description": "The provider ID to check",
                    },
                    "task_type": {
                        "type": "string",
                        "description": "Optional task domain for context-specific scoring",
                    },
                },
                "required": ["provider_id"],
            },
        ),
        Tool(
            name="trustscore_report",
            description=(
                "Report the outcome of an interaction with a provider. This contributes "
                "data to improve trust scores for everyone. Contributors get richer data "
                "in return."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "provider_id": {
                        "type": "string",
                        "description": "The provider that was used",
                    },
                    "outcome": {
                        "type": "string",
                        "enum": ["success", "failure", "timeout", "error"],
                        "description": "What happened",
                    },
                    "task_type": {
                        "type": "string",
                        "description": "What type of task was attempted",
                    },
                    "latency_ms": {
                        "type": "integer",
                        "description": "How long the interaction took in milliseconds",
                    },
                    "reporter_id": {
                        "type": "string",
                        "description": "Your agent's ID (for contributor tracking)",
                    },
                    "details": {
                        "type": "string",
                        "description": "Optional details about what happened",
                    },
                },
                "required": ["provider_id", "outcome"],
            },
        ),
        Tool(
            name="trustscore_discover",
            description=(
                "Discover trusted providers for a specific task type. Returns top providers "
                "ranked by trust score. Use when you need to find a reliable provider "
                "for a task but don't have candidates yet."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "task_type": {
                        "type": "string",
                        "description": "What type of task you need (e.g., 'defi_swap', 'web_search')",
                    },
                    "min_score": {
                        "type": "number",
                        "description": "Minimum trust score (0-1). Default 0.5.",
                        "default": 0.5,
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max providers to return. Default 5.",
                        "default": 5,
                    },
                },
                "required": [],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""

    if name == "trustscore_rank":
        providers = arguments.get("providers", [])
        task_type = arguments.get("task_type")
        min_score = arguments.get("min_score", 0)

        if not providers:
            return [TextContent(type="text", text=json.dumps({"error": "No providers specified"}))]

        ranked = await db.get_ranked_providers(providers, task_type, min_score)

        # Build clean response
        result = {
            "ranked": [
                {
                    "provider_id": p["provider_id"],
                    "trust_score": p["trust_score"],
                    "reliability": p["reliability"],
                    "avg_latency_ms": p.get("avg_latency_ms"),
                    "success_rate_30d": p.get("success_rate_30d"),
                    "sample_size": p["sample_size"],
                    "flags": p.get("flags", []),
                    "confidence": p["confidence"],
                }
                for p in ranked
            ],
            "recommendation": ranked[0]["provider_id"] if ranked else None,
            "data_freshness": datetime.now(timezone.utc).isoformat(),
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "trustscore_check":
        provider_id = arguments.get("provider_id")
        task_type = arguments.get("task_type")

        if not provider_id:
            return [TextContent(type="text", text=json.dumps({"error": "No provider_id specified"}))]

        score = await db.get_provider_score(provider_id, task_type)

        if not score:
            result = {
                "provider_id": provider_id,
                "trust_score": 0.5,
                "reliability": 0.5,
                "confidence": "none",
                "sample_size": 0,
                "flags": ["unknown_provider"],
                "message": "No data available for this provider. Consider reporting your interactions to build trust data.",
            }
        else:
            result = {
                "provider_id": score["provider_id"],
                "trust_score": score["trust_score"],
                "reliability": score["reliability"],
                "avg_latency_ms": score.get("avg_latency_ms"),
                "success_rate_30d": score.get("success_rate_30d"),
                "sample_size": score["sample_size"],
                "flags": score.get("flags", []),
                "confidence": score["confidence"],
                "history": score.get("history", {}),
            }

        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "trustscore_report":
        provider_id = arguments.get("provider_id")
        outcome = arguments.get("outcome")

        if not provider_id or not outcome:
            return [TextContent(type="text", text=json.dumps({"error": "provider_id and outcome required"}))]

        if outcome not in ("success", "failure", "timeout", "error"):
            return [TextContent(type="text", text=json.dumps({"error": "outcome must be: success, failure, timeout, or error"}))]

        await db.record_interaction(
            provider_id=provider_id,
            outcome=outcome,
            task_type=arguments.get("task_type"),
            latency_ms=arguments.get("latency_ms"),
            reporter_id=arguments.get("reporter_id", "anonymous"),
            details=arguments.get("details"),
        )

        reporter_id = arguments.get("reporter_id", "anonymous")
        stats = await db.get_contributor_stats(reporter_id)

        result = {
            "accepted": True,
            "contributor_status": stats["contributor_status"],
            "total_contributions": stats["total_contributions"],
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "trustscore_discover":
        task_type = arguments.get("task_type")
        min_score = arguments.get("min_score", 0.5)
        limit = arguments.get("limit", 5)

        providers = await db.discover_providers(task_type, min_score, limit)

        result = {
            "providers": [
                {
                    "provider_id": p["provider_id"],
                    "trust_score": p["trust_score"],
                    "task_types": p.get("task_types"),
                    "description": p.get("description"),
                    "sample_size": p["sample_size"],
                    "confidence": p["confidence"],
                }
                for p in providers
            ],
            "total_matching": len(providers),
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    else:
        return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]


async def run():
    """Start the MCP server."""
    await db.init_db()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main():
    """Entry point."""
    asyncio.run(run())


if __name__ == "__main__":
    main()
