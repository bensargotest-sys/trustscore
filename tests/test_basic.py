"""Basic tests for TrustScore MCP server."""

import asyncio
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.database import (
    init_db,
    upsert_provider,
    record_interaction,
    get_provider_score,
    get_ranked_providers,
    discover_providers,
    get_contributor_stats,
)


async def test_all():
    """Run all tests."""
    # Use temp database
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    print("Initializing database...")
    await init_db(db_path)
    print("  ✓ Database initialized")

    # Test: Create providers
    print("\nCreating test providers...")
    await upsert_provider("uniswap_v3_base", "Uniswap V3 (Base)", "https://mcp.uniswap.io",
                          '["defi_swap", "defi_liquidity"]', "Uniswap V3 on Base L2", "clawbot", db_path)
    await upsert_provider("jupiter_solana", "Jupiter (Solana)", "https://mcp.jupiter.io",
                          '["defi_swap"]', "Jupiter aggregator on Solana", "clawbot", db_path)
    await upsert_provider("sketchy_swap", "Sketchy Swap", "https://sketchy.io",
                          '["defi_swap"]', "Unknown swap provider", "registry", db_path)
    print("  ✓ 3 providers created")

    # Test: Record interactions
    print("\nRecording interactions...")
    # Uniswap: mostly successful
    for i in range(80):
        await record_interaction("uniswap_v3_base", "success", "defi_swap", 200 + i, "clawbot", db_path=db_path)
    for i in range(5):
        await record_interaction("uniswap_v3_base", "failure", "defi_swap", 3000, "clawbot", db_path=db_path)

    # Jupiter: decent
    for i in range(30):
        await record_interaction("jupiter_solana", "success", "defi_swap", 400 + i, "clawbot", db_path=db_path)
    for i in range(10):
        await record_interaction("jupiter_solana", "failure", "defi_swap", 5000, "clawbot", db_path=db_path)

    # Sketchy: unreliable
    for i in range(5):
        await record_interaction("sketchy_swap", "success", "defi_swap", 1500, "clawbot", db_path=db_path)
    for i in range(15):
        await record_interaction("sketchy_swap", "failure", "defi_swap", 8000, "clawbot", db_path=db_path)

    print("  ✓ 145 interactions recorded")

    # Test: Get individual scores
    print("\nComputing trust scores...")
    uniswap = await get_provider_score("uniswap_v3_base", "defi_swap", db_path)
    jupiter = await get_provider_score("jupiter_solana", "defi_swap", db_path)
    sketchy = await get_provider_score("sketchy_swap", "defi_swap", db_path)

    print(f"  Uniswap:  score={uniswap['trust_score']:.3f}  reliability={uniswap['reliability']:.3f}  "
          f"samples={uniswap['sample_size']}  confidence={uniswap['confidence']}  flags={uniswap['flags']}")
    print(f"  Jupiter:  score={jupiter['trust_score']:.3f}  reliability={jupiter['reliability']:.3f}  "
          f"samples={jupiter['sample_size']}  confidence={jupiter['confidence']}  flags={jupiter['flags']}")
    print(f"  Sketchy:  score={sketchy['trust_score']:.3f}  reliability={sketchy['reliability']:.3f}  "
          f"samples={sketchy['sample_size']}  confidence={sketchy['confidence']}  flags={sketchy['flags']}")

    # Verify ordering
    assert uniswap["trust_score"] > jupiter["trust_score"], "Uniswap should rank above Jupiter"
    assert jupiter["trust_score"] > sketchy["trust_score"], "Jupiter should rank above Sketchy"
    print("  ✓ Scores correctly ordered (Uniswap > Jupiter > Sketchy)")

    # Verify reliability
    assert uniswap["reliability"] > 0.9, f"Uniswap reliability should be >0.9, got {uniswap['reliability']}"
    assert sketchy["reliability"] < 0.3, f"Sketchy reliability should be <0.3, got {sketchy['reliability']}"
    print("  ✓ Reliability values correct")

    # Test: Rank providers
    print("\nRanking providers...")
    ranked = await get_ranked_providers(
        ["sketchy_swap", "uniswap_v3_base", "jupiter_solana", "unknown_provider"],
        "defi_swap",
        db_path=db_path,
    )
    print(f"  Ranked order: {[r['provider_id'] for r in ranked]}")
    assert ranked[0]["provider_id"] == "uniswap_v3_base", "Uniswap should be #1"
    assert ranked[-1]["provider_id"] in ("sketchy_swap", "unknown_provider"), "Sketchy/unknown should be last"
    print("  ✓ Ranking correct")

    # Test: Unknown provider included with neutral score
    unknown = [r for r in ranked if r["provider_id"] == "unknown_provider"]
    assert len(unknown) == 1, "Unknown provider should be included"
    assert unknown[0]["trust_score"] == 0.5, "Unknown should have neutral 0.5 score"
    assert "unknown_provider" in unknown[0]["flags"], "Should be flagged as unknown"
    print("  ✓ Unknown providers handled correctly")

    # Test: Discover providers
    print("\nDiscovering providers...")
    discovered = await discover_providers("defi_swap", min_score=0.0, limit=10, db_path=db_path)
    print(f"  Found {len(discovered)} providers for defi_swap")
    assert len(discovered) >= 3, "Should find at least 3 providers"
    assert discovered[0]["provider_id"] == "uniswap_v3_base", "Uniswap should be top discovery"
    print("  ✓ Discovery working")

    # Test: Min score filter
    high_only = await discover_providers("defi_swap", min_score=0.6, limit=10, db_path=db_path)
    sketchy_in_results = [p for p in high_only if p["provider_id"] == "sketchy_swap"]
    assert len(sketchy_in_results) == 0, "Sketchy should be filtered by min_score=0.6"
    print("  ✓ Min score filtering works")

    # Test: Contributor stats
    print("\nChecking contributor stats...")
    stats = await get_contributor_stats("clawbot", db_path)
    assert stats["total_contributions"] == 145, f"Expected 145 contributions, got {stats['total_contributions']}"
    assert stats["contributor_status"] == "trusted", f"ClawBot should be 'trusted' status"
    print(f"  ✓ ClawBot: {stats['total_contributions']} contributions, status={stats['contributor_status']}")

    # Test: History windows
    print("\nChecking history windows...")
    assert uniswap["history"]["7d"]["success_rate"] is not None, "Should have 7d history"
    assert uniswap["history"]["30d"]["success_rate"] is not None, "Should have 30d history"
    print(f"  Uniswap 7d: {uniswap['history']['7d']}")
    print(f"  Uniswap 30d: {uniswap['history']['30d']}")
    print("  ✓ History windows populated")

    # Test: Flags
    print("\nChecking flags...")
    assert "recent_failures" in sketchy["flags"] or sketchy["reliability"] < 0.3, "Sketchy should have warning flags"
    print(f"  Sketchy flags: {sketchy['flags']}")
    print("  ✓ Flags generated correctly")

    # Cleanup
    os.unlink(db_path)

    print("\n" + "=" * 50)
    print("ALL TESTS PASSED ✓")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(test_all())
