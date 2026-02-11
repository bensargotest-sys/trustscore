"""
ClawBot Testing Harness — Probes MCP servers and seeds the TrustScore database.

Usage:
    python -m src.clawbot_harness                    # Test servers from registry
    python -m src.clawbot_harness --file servers.json # Test servers from file
    python -m src.clawbot_harness --url https://...   # Test a single server
"""

import argparse
import asyncio
import json
import time
import aiohttp
import aiosqlite
from pathlib import Path
from typing import Optional

from . import database as db

# Known MCP servers to seed with (curated starter list)
SEED_SERVERS = [
    {
        "provider_id": "smithery_web_search",
        "name": "Smithery Web Search",
        "endpoint": "https://server.smithery.ai/@anthropic/web-search",
        "task_types": '["web_search"]',
        "description": "Web search via Smithery",
        "source": "curated",
    },
    {
        "provider_id": "smithery_brave_search",
        "name": "Brave Search MCP",
        "endpoint": "https://server.smithery.ai/@anthropic/brave-search",
        "task_types": '["web_search"]',
        "description": "Brave search engine via Smithery",
        "source": "curated",
    },
    {
        "provider_id": "smithery_github",
        "name": "GitHub MCP Server",
        "endpoint": "https://server.smithery.ai/@anthropic/github",
        "task_types": '["code_search", "repo_management"]',
        "description": "GitHub API via MCP",
        "source": "curated",
    },
    {
        "provider_id": "smithery_filesystem",
        "name": "Filesystem MCP Server",
        "endpoint": "https://server.smithery.ai/@anthropic/filesystem",
        "task_types": '["file_operations"]',
        "description": "Local filesystem access via MCP",
        "source": "curated",
    },
    {
        "provider_id": "smithery_postgres",
        "name": "PostgreSQL MCP Server",
        "endpoint": "https://server.smithery.ai/@anthropic/postgres",
        "task_types": '["database_query"]',
        "description": "PostgreSQL database access via MCP",
        "source": "curated",
    },
    {
        "provider_id": "smithery_slack",
        "name": "Slack MCP Server",
        "endpoint": "https://server.smithery.ai/@anthropic/slack",
        "task_types": '["messaging", "team_communication"]',
        "description": "Slack API via MCP",
        "source": "curated",
    },
    {
        "provider_id": "smithery_fetch",
        "name": "Fetch MCP Server",
        "endpoint": "https://server.smithery.ai/@anthropic/fetch",
        "task_types": '["web_fetch", "http_request"]',
        "description": "HTTP fetch via MCP",
        "source": "curated",
    },
    {
        "provider_id": "smithery_memory",
        "name": "Memory MCP Server",
        "endpoint": "https://server.smithery.ai/@anthropic/memory",
        "task_types": '["memory", "knowledge_graph"]',
        "description": "Persistent memory/knowledge graph via MCP",
        "source": "curated",
    },
]


class ServerProbe:
    """Probes an MCP server endpoint to measure reliability."""

    def __init__(self, timeout_seconds: int = 10):
        self.timeout = aiohttp.ClientTimeout(total=timeout_seconds)

    async def probe_endpoint(self, endpoint: str) -> dict:
        """
        Probe an MCP server endpoint.
        Tests: reachability, response time, basic protocol compliance.
        Returns a result dict with outcome and metrics.
        """
        start = time.time()
        result = {
            "reachable": False,
            "latency_ms": None,
            "status_code": None,
            "outcome": "error",
            "details": "",
        }

        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                # Test 1: Basic HTTP reachability (GET or OPTIONS)
                async with session.get(endpoint) as resp:
                    latency = int((time.time() - start) * 1000)
                    result["latency_ms"] = latency
                    result["status_code"] = resp.status
                    result["reachable"] = True

                    if resp.status == 200:
                        result["outcome"] = "success"
                        result["details"] = f"HTTP 200 in {latency}ms"
                    elif resp.status in (301, 302, 307, 308):
                        result["outcome"] = "success"
                        result["details"] = f"Redirect ({resp.status}) in {latency}ms"
                    elif resp.status == 404:
                        result["outcome"] = "failure"
                        result["details"] = f"Not found (404) in {latency}ms"
                    elif resp.status == 405:
                        # Method not allowed — server exists but doesn't accept GET
                        # This is actually expected for many MCP servers (they want POST)
                        result["outcome"] = "success"
                        result["details"] = f"Server exists (405 Method Not Allowed) in {latency}ms"
                    elif resp.status >= 500:
                        result["outcome"] = "failure"
                        result["details"] = f"Server error ({resp.status}) in {latency}ms"
                    else:
                        result["outcome"] = "success"
                        result["details"] = f"HTTP {resp.status} in {latency}ms"

        except asyncio.TimeoutError:
            result["outcome"] = "timeout"
            result["latency_ms"] = int(self.timeout.total * 1000)
            result["details"] = f"Timed out after {self.timeout.total}s"
        except aiohttp.ClientConnectorError as e:
            result["outcome"] = "error"
            result["details"] = f"Connection failed: {str(e)[:100]}"
        except aiohttp.ClientError as e:
            result["outcome"] = "error"
            result["details"] = f"Client error: {str(e)[:100]}"
        except Exception as e:
            result["outcome"] = "error"
            result["details"] = f"Unexpected error: {str(e)[:100]}"

        return result

    async def probe_sse_endpoint(self, endpoint: str) -> dict:
        """
        Probe an MCP server via SSE (Server-Sent Events) transport.
        Many remote MCP servers use SSE.
        """
        start = time.time()
        sse_url = endpoint.rstrip("/") + "/sse"
        result = {
            "reachable": False,
            "latency_ms": None,
            "status_code": None,
            "outcome": "error",
            "details": "",
        }

        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(sse_url) as resp:
                    latency = int((time.time() - start) * 1000)
                    result["latency_ms"] = latency
                    result["status_code"] = resp.status
                    result["reachable"] = resp.status < 500

                    if resp.status == 200:
                        content_type = resp.headers.get("content-type", "")
                        if "text/event-stream" in content_type:
                            result["outcome"] = "success"
                            result["details"] = f"SSE endpoint active in {latency}ms"
                        else:
                            result["outcome"] = "success"
                            result["details"] = f"Endpoint responds ({content_type}) in {latency}ms"
                    elif resp.status == 404:
                        # SSE not available, but server might use different transport
                        result["outcome"] = "failure"
                        result["details"] = f"SSE endpoint not found in {latency}ms"
                    else:
                        result["outcome"] = "success" if resp.status < 400 else "failure"
                        result["details"] = f"HTTP {resp.status} in {latency}ms"

        except asyncio.TimeoutError:
            result["outcome"] = "timeout"
            result["latency_ms"] = int(self.timeout.total * 1000)
            result["details"] = f"SSE timed out after {self.timeout.total}s"
        except Exception as e:
            result["outcome"] = "error"
            result["details"] = f"SSE error: {str(e)[:100]}"

        return result


async def test_server(
    server_info: dict, probe: ServerProbe, db_path: str = None
) -> dict:
    """Test a single server and record results."""
    provider_id = server_info["provider_id"]
    endpoint = server_info["endpoint"]

    print(f"  Testing {provider_id}...", end=" ", flush=True)

    # Register/update provider
    await db.upsert_provider(
        provider_id=provider_id,
        name=server_info.get("name"),
        endpoint=endpoint,
        task_types=server_info.get("task_types", "[]"),
        description=server_info.get("description"),
        source=server_info.get("source", "clawbot"),
        db_path=db_path,
    )

    # Run probes
    http_result = await probe.probe_endpoint(endpoint)
    sse_result = await probe.probe_sse_endpoint(endpoint)

    # Use the best result
    if http_result["outcome"] == "success":
        best = http_result
    elif sse_result["outcome"] == "success":
        best = sse_result
    else:
        # Both failed, use HTTP result
        best = http_result

    # Record interaction
    await db.record_interaction(
        provider_id=provider_id,
        outcome=best["outcome"],
        task_type="health_check",
        latency_ms=best["latency_ms"],
        reporter_id="clawbot",
        details=best["details"],
        db_path=db_path,
    )

    status = "✓" if best["outcome"] == "success" else "✗"
    print(f"{status} {best['outcome']} — {best['details']}")

    return {
        "provider_id": provider_id,
        "http": http_result,
        "sse": sse_result,
        "best": best,
    }


async def fetch_registry_servers(limit: int = 50) -> list[dict]:
    """
    Fetch servers from public MCP registries.
    Falls back to curated list if registry is unavailable.
    """
    servers = []

    # Try Smithery API
    try:
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=15)
        ) as session:
            # Smithery public API
            url = f"https://registry.smithery.ai/servers?limit={limit}"
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    items = data if isinstance(data, list) else data.get("servers", data.get("items", []))
                    for item in items[:limit]:
                        server_id = item.get("qualifiedName", item.get("name", item.get("id", "")))
                        if server_id:
                            servers.append({
                                "provider_id": f"smithery_{server_id}".replace("/", "_").replace("@", ""),
                                "name": item.get("displayName", item.get("name", server_id)),
                                "endpoint": f"https://server.smithery.ai/{server_id}",
                                "task_types": json.dumps(item.get("capabilities", [])),
                                "description": item.get("description", "")[:200],
                                "source": "registry",
                            })
                    print(f"  Fetched {len(servers)} servers from Smithery registry")
    except Exception as e:
        print(f"  Could not fetch from Smithery registry: {e}")

    if not servers:
        print("  Using curated seed list")
        servers = SEED_SERVERS.copy()

    return servers


async def run_test_suite(
    servers: list[dict] = None,
    rounds: int = 3,
    db_path: str = None,
):
    """Run the full test suite against a list of servers."""
    if db_path is None:
        db_path = str(db.DB_PATH)

    await db.init_db(db_path)

    if servers is None:
        print("Fetching servers from registry...")
        servers = await fetch_registry_servers(limit=50)

    probe = ServerProbe(timeout_seconds=10)
    total_servers = len(servers)

    print(f"\nTesting {total_servers} servers ({rounds} rounds each)")
    print("=" * 60)

    all_results = []

    for round_num in range(1, rounds + 1):
        print(f"\n--- Round {round_num}/{rounds} ---")
        round_results = []

        for server_info in servers:
            result = await test_server(server_info, probe, db_path)
            round_results.append(result)

            # Small delay between servers to be respectful
            await asyncio.sleep(0.5)

        all_results.extend(round_results)

        if round_num < rounds:
            print(f"\nWaiting 5s before next round...")
            await asyncio.sleep(5)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    successes = sum(1 for r in all_results if r["best"]["outcome"] == "success")
    failures = sum(1 for r in all_results if r["best"]["outcome"] == "failure")
    timeouts = sum(1 for r in all_results if r["best"]["outcome"] == "timeout")
    errors = sum(1 for r in all_results if r["best"]["outcome"] == "error")
    total = len(all_results)

    print(f"Total probes: {total}")
    print(f"  Success:  {successes} ({successes/total*100:.1f}%)")
    print(f"  Failure:  {failures} ({failures/total*100:.1f}%)")
    print(f"  Timeout:  {timeouts} ({timeouts/total*100:.1f}%)")
    print(f"  Error:    {errors} ({errors/total*100:.1f}%)")

    # Top and bottom providers
    print(f"\nTop providers by trust score:")
    all_provider_ids = list({s["provider_id"] for s in servers})
    ranked = await db.get_ranked_providers(all_provider_ids, db_path=db_path)

    for i, p in enumerate(ranked[:10]):
        flags = ", ".join(p.get("flags", [])) if p.get("flags") else "none"
        print(f"  {i+1}. {p['provider_id']}: score={p['trust_score']:.3f} "
              f"reliability={p['reliability']:.3f} samples={p['sample_size']} flags=[{flags}]")

    if len(ranked) > 10:
        print(f"\n  ... and {len(ranked) - 10} more providers")

    bottom = [p for p in ranked if p["trust_score"] < 0.5 and p["sample_size"] > 0]
    if bottom:
        print(f"\nUnreliable providers (score < 0.5):")
        for p in bottom:
            print(f"  ⚠ {p['provider_id']}: score={p['trust_score']:.3f} "
                  f"reliability={p['reliability']:.3f}")

    print(f"\nDatabase: {db_path}")
    print("Done.")


async def main():
    parser = argparse.ArgumentParser(description="ClawBot MCP Server Testing Harness")
    parser.add_argument("--file", type=str, help="JSON file with server list")
    parser.add_argument("--url", type=str, help="Test a single server URL")
    parser.add_argument("--name", type=str, default="manual_test", help="Name for single URL test")
    parser.add_argument("--rounds", type=int, default=3, help="Number of test rounds (default: 3)")
    parser.add_argument("--db", type=str, default=None, help="Database path")
    parser.add_argument("--seed-only", action="store_true", help="Only use curated seed list")
    args = parser.parse_args()

    if args.url:
        servers = [{
            "provider_id": args.name,
            "name": args.name,
            "endpoint": args.url,
            "task_types": "[]",
            "description": f"Manual test: {args.url}",
            "source": "manual",
        }]
    elif args.file:
        with open(args.file) as f:
            servers = json.load(f)
    elif args.seed_only:
        servers = SEED_SERVERS.copy()
    else:
        servers = None  # Will fetch from registry

    await run_test_suite(servers=servers, rounds=args.rounds, db_path=args.db)


if __name__ == "__main__":
    asyncio.run(main())
