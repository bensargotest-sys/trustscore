"""
End-to-end simulation: Simulates realistic agent usage of TrustScore.
Tests the full flow: seed data → query scores → report outcomes → scores update.
"""

import asyncio
import json
import os
import sys
import random
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.database import (
    init_db, upsert_provider, record_interaction,
    get_provider_score, get_ranked_providers, discover_providers,
)
from src.server import call_tool


# Simulated provider profiles (name, success_rate, avg_latency)
MOCK_PROVIDERS = {
    "uniswap_v3_base": ("Uniswap V3 Base", 0.95, 200, '["defi_swap"]'),
    "sushiswap_base": ("SushiSwap Base", 0.88, 350, '["defi_swap"]'),
    "pancakeswap_bsc": ("PancakeSwap BSC", 0.82, 500, '["defi_swap"]'),
    "jupiter_solana": ("Jupiter Solana", 0.91, 180, '["defi_swap", "defi_route"]'),
    "aave_v3_base": ("Aave V3 Base", 0.93, 250, '["defi_lending"]'),
    "compound_eth": ("Compound ETH", 0.85, 400, '["defi_lending"]'),
    "chainlink_oracle": ("Chainlink Oracle", 0.97, 150, '["price_feed"]'),
    "pyth_oracle": ("Pyth Oracle", 0.90, 130, '["price_feed"]'),
    "sketchy_dex": ("Sketchy DEX", 0.30, 2000, '["defi_swap"]'),
    "unreliable_bridge": ("Unreliable Bridge", 0.45, 3000, '["bridge"]'),
    "web_search_a": ("Web Search A", 0.92, 300, '["web_search"]'),
    "web_search_b": ("Web Search B", 0.78, 600, '["web_search"]'),
    "code_search": ("Code Search", 0.89, 250, '["code_search"]'),
    "memory_server": ("Memory Server", 0.94, 100, '["memory"]'),
    "fast_but_flaky": ("Fast But Flaky", 0.60, 80, '["defi_swap"]'),
}


async def simulate_interactions(db_path: str, num_interactions: int = 500):
    """Simulate realistic agent interactions with providers."""
    for _ in range(num_interactions):
        pid = random.choice(list(MOCK_PROVIDERS.keys()))
        _, success_rate, avg_latency, _ = MOCK_PROVIDERS[pid]

        # Simulate outcome
        outcome = "success" if random.random() < success_rate else random.choice(["failure", "timeout", "error"])
        latency = max(10, int(random.gauss(avg_latency, avg_latency * 0.3)))
        if outcome != "success":
            latency = latency * 3  # Failures are slower

        reporter = random.choice(["agent_alpha", "agent_beta", "agent_gamma", "clawbot"])

        await record_interaction(
            provider_id=pid,
            outcome=outcome,
            task_type=MOCK_PROVIDERS[pid][3].strip('[]"').split('", "')[0],
            latency_ms=latency,
            reporter_id=reporter,
            db_path=db_path,
        )


async def test_e2e():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    await init_db(db_path)

    # Phase 1: Register providers
    print("Phase 1: Registering 15 providers...")
    for pid, (name, _, _, task_types) in MOCK_PROVIDERS.items():
        await upsert_provider(
            pid, name, f"https://mcp.example.com/{pid}",
            task_types, f"Simulated: {name}", "clawbot", db_path
        )
    print("  ✓ 15 providers registered")

    # Phase 2: Simulate 500 interactions
    print("\nPhase 2: Simulating 500 agent interactions...")
    await simulate_interactions(db_path, 500)
    print("  ✓ 500 interactions recorded")

    # Phase 3: Test trustscore_rank (via tool interface)
    print("\nPhase 3: Testing trustscore_rank...")
    # Temporarily override DB_PATH for tool calls
    import src.database as dbmod
    original_path = dbmod.DB_PATH
    dbmod.DB_PATH = db_path

    result = await call_tool("trustscore_rank", {
        "providers": ["uniswap_v3_base", "sketchy_dex", "jupiter_solana", "fast_but_flaky"],
        "task_type": "defi_swap",
    })
    data = json.loads(result[0].text)
    print(f"  Recommendation: {data['recommendation']}")
    for p in data["ranked"]:
        print(f"    {p['provider_id']}: score={p['trust_score']:.3f} "
              f"reliability={p['reliability']:.3f} confidence={p['confidence']}")

    assert data["recommendation"] in ("uniswap_v3_base", "jupiter_solana"), \
        f"Should recommend Uniswap or Jupiter, got {data['recommendation']}"
    assert data["ranked"][-1]["provider_id"] in ("sketchy_dex", "fast_but_flaky"), \
        "Sketchy or Flaky should be ranked last"
    print("  ✓ Ranking correct")

    # Phase 4: Test trustscore_check
    print("\nPhase 4: Testing trustscore_check...")
    result = await call_tool("trustscore_check", {
        "provider_id": "chainlink_oracle",
        "task_type": "price_feed",
    })
    data = json.loads(result[0].text)
    print(f"  Chainlink: score={data['trust_score']:.3f} reliability={data['reliability']:.3f}")
    assert data["trust_score"] > 0.8, "Chainlink should have high score"
    assert data["history"]["7d"]["success_rate"] is not None
    print("  ✓ Check returns detailed data")

    # Phase 5: Test trustscore_report
    print("\nPhase 5: Testing trustscore_report...")
    result = await call_tool("trustscore_report", {
        "provider_id": "uniswap_v3_base",
        "outcome": "success",
        "task_type": "defi_swap",
        "latency_ms": 195,
        "reporter_id": "test_agent",
    })
    data = json.loads(result[0].text)
    assert data["accepted"] is True
    print(f"  ✓ Report accepted. Status: {data['contributor_status']}, total: {data['total_contributions']}")

    # Phase 6: Test trustscore_discover
    print("\nPhase 6: Testing trustscore_discover...")
    result = await call_tool("trustscore_discover", {
        "task_type": "defi_swap",
        "min_score": 0.5,
        "limit": 5,
    })
    data = json.loads(result[0].text)
    print(f"  Found {data['total_matching']} providers for defi_swap (min_score=0.5)")
    for p in data["providers"]:
        print(f"    {p['provider_id']}: score={p['trust_score']:.3f}")

    # Sketchy should be filtered out
    ids = [p["provider_id"] for p in data["providers"]]
    assert "sketchy_dex" not in ids, "Sketchy DEX should be filtered at min_score=0.5"
    print("  ✓ Discovery filters correctly")

    # Phase 7: Verify score ordering matches real reliability
    print("\nPhase 7: Verifying score ordering matches simulated reliability...")
    all_ids = list(MOCK_PROVIDERS.keys())
    all_ranked = await get_ranked_providers(all_ids, db_path=db_path)

    print("\n  Final Leaderboard:")
    print(f"  {'Rank':<5} {'Provider':<25} {'Score':<8} {'Reliability':<12} {'Samples':<8} {'True Rate'}")
    print(f"  {'-'*5} {'-'*25} {'-'*8} {'-'*12} {'-'*8} {'-'*10}")
    for i, p in enumerate(all_ranked):
        true_rate = MOCK_PROVIDERS.get(p["provider_id"], (None, 0, 0, None))[1]
        print(f"  {i+1:<5} {p['provider_id']:<25} {p['trust_score']:<8.3f} "
              f"{p['reliability']:<12.3f} {p['sample_size']:<8} {true_rate:.2f}")

    # Top 3 should be high-reliability providers
    top3_ids = {p["provider_id"] for p in all_ranked[:3]}
    high_reliability = {"chainlink_oracle", "uniswap_v3_base", "jupiter_solana", "memory_server", "aave_v3_base"}
    overlap = top3_ids & high_reliability
    assert len(overlap) >= 2, f"Top 3 should contain at least 2 high-reliability providers, got {top3_ids}"
    print(f"\n  ✓ Top 3 contains {len(overlap)}/3 known high-reliability providers")

    # Bottom 3 should be low-reliability providers
    bottom3_ids = {p["provider_id"] for p in all_ranked[-3:]}
    low_reliability = {"sketchy_dex", "unreliable_bridge", "fast_but_flaky"}
    overlap = bottom3_ids & low_reliability
    assert len(overlap) >= 2, f"Bottom 3 should contain at least 2 low-reliability providers, got {bottom3_ids}"
    print(f"  ✓ Bottom 3 contains {len(overlap)}/3 known low-reliability providers")

    # Restore
    dbmod.DB_PATH = original_path
    os.unlink(db_path)

    print("\n" + "=" * 60)
    print("END-TO-END SIMULATION PASSED ✓")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_e2e())
