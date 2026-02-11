"""SQLite database layer for TrustScore MCP server."""

import aiosqlite
import math
import time
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).parent.parent / "trustscore.db"
RECENCY_HALF_LIFE_DAYS = 30


async def init_db(db_path: str = None):
    """Initialize the database with required tables."""
    path = db_path or str(DB_PATH)
    async with aiosqlite.connect(path) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS providers (
                provider_id TEXT PRIMARY KEY,
                name TEXT,
                endpoint TEXT,
                task_types TEXT,  -- JSON array as string
                description TEXT,
                source TEXT DEFAULT 'registry',
                first_seen REAL,
                last_tested REAL
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                provider_id TEXT NOT NULL,
                reporter_id TEXT DEFAULT 'anonymous',
                task_type TEXT,
                outcome TEXT NOT NULL,  -- success | failure | timeout | error
                latency_ms INTEGER,
                details TEXT,
                timestamp REAL NOT NULL,
                FOREIGN KEY (provider_id) REFERENCES providers(provider_id)
            )
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_interactions_provider
            ON interactions(provider_id, timestamp DESC)
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_interactions_task
            ON interactions(task_type, timestamp DESC)
        """)
        await db.commit()
    return path


async def upsert_provider(
    provider_id: str,
    name: str = None,
    endpoint: str = None,
    task_types: str = "[]",
    description: str = None,
    source: str = "registry",
    db_path: str = None,
):
    """Insert or update a provider record."""
    path = db_path or str(DB_PATH)
    now = time.time()
    async with aiosqlite.connect(path) as db:
        await db.execute(
            """
            INSERT INTO providers (provider_id, name, endpoint, task_types, description, source, first_seen, last_tested)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(provider_id) DO UPDATE SET
                name = COALESCE(excluded.name, providers.name),
                endpoint = COALESCE(excluded.endpoint, providers.endpoint),
                task_types = COALESCE(excluded.task_types, providers.task_types),
                description = COALESCE(excluded.description, providers.description),
                last_tested = excluded.last_tested
            """,
            (provider_id, name, endpoint, task_types, description, source, now, now),
        )
        await db.commit()


async def record_interaction(
    provider_id: str,
    outcome: str,
    task_type: str = None,
    latency_ms: int = None,
    reporter_id: str = "anonymous",
    details: str = None,
    db_path: str = None,
):
    """Record an interaction outcome."""
    path = db_path or str(DB_PATH)
    now = time.time()
    async with aiosqlite.connect(path) as db:
        await db.execute(
            """
            INSERT INTO interactions (provider_id, reporter_id, task_type, outcome, latency_ms, details, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (provider_id, reporter_id, task_type, outcome, latency_ms, details, now),
        )
        await db.commit()

        # Auto-create provider if it doesn't exist
        await db.execute(
            """
            INSERT OR IGNORE INTO providers (provider_id, source, first_seen, last_tested)
            VALUES (?, 'contributor', ?, ?)
            """,
            (provider_id, now, now),
        )
        await db.commit()


def _compute_trust_score(
    successes: int, failures: int, avg_latency_ms: float, last_interaction_ts: float
) -> dict:
    """Compute trust score from raw counts using Beta distribution."""
    total = successes + failures
    if total == 0:
        return {
            "trust_score": 0.5,
            "reliability": 0.5,
            "confidence": "none",
            "sample_size": 0,
        }

    # Beta distribution mean
    # Using Bayesian prior: Beta(1,1) = uniform prior
    alpha = successes + 1
    beta_param = failures + 1
    base_score = alpha / (alpha + beta_param)

    # Confidence based on sample size
    # Ramps from 0 to 1 as samples increase
    confidence_val = 1.0 - (1.0 / math.sqrt(total + 1))

    # Recency weighting — decay if no recent interactions
    now = time.time()
    days_since_last = (now - last_interaction_ts) / 86400 if last_interaction_ts else 30
    recency_factor = math.exp(-0.693 * days_since_last / RECENCY_HALF_LIFE_DAYS)

    # Composite score
    trust_score = round(base_score * (0.5 + 0.5 * confidence_val) * (0.5 + 0.5 * recency_factor), 4)

    # Reliability is just success rate
    reliability = round(successes / total, 4) if total > 0 else 0.5

    # Confidence label
    if total >= 100:
        conf_label = "high"
    elif total >= 20:
        conf_label = "medium"
    elif total >= 5:
        conf_label = "low"
    else:
        conf_label = "very_low"

    return {
        "trust_score": trust_score,
        "reliability": reliability,
        "confidence": conf_label,
        "sample_size": total,
    }


async def get_provider_score(
    provider_id: str, task_type: str = None, db_path: str = None
) -> Optional[dict]:
    """Get computed trust score for a provider."""
    path = db_path or str(DB_PATH)
    async with aiosqlite.connect(path) as db:
        db.row_factory = aiosqlite.Row

        # Get provider info
        cursor = await db.execute(
            "SELECT * FROM providers WHERE provider_id = ?", (provider_id,)
        )
        provider = await cursor.fetchone()
        if not provider:
            return None

        # Build query for interactions
        if task_type:
            cursor = await db.execute(
                """
                SELECT
                    SUM(CASE WHEN outcome = 'success' THEN 1 ELSE 0 END) as successes,
                    SUM(CASE WHEN outcome != 'success' THEN 1 ELSE 0 END) as failures,
                    AVG(latency_ms) as avg_latency,
                    MAX(timestamp) as last_ts
                FROM interactions
                WHERE provider_id = ? AND (task_type = ? OR task_type IS NULL)
                """,
                (provider_id, task_type),
            )
        else:
            cursor = await db.execute(
                """
                SELECT
                    SUM(CASE WHEN outcome = 'success' THEN 1 ELSE 0 END) as successes,
                    SUM(CASE WHEN outcome != 'success' THEN 1 ELSE 0 END) as failures,
                    AVG(latency_ms) as avg_latency,
                    MAX(timestamp) as last_ts
                FROM interactions
                WHERE provider_id = ?
                """,
                (provider_id,),
            )

        row = await cursor.fetchone()
        successes = row["successes"] or 0
        failures = row["failures"] or 0
        avg_latency = row["avg_latency"] or 0
        last_ts = row["last_ts"] or 0

        scores = _compute_trust_score(successes, failures, avg_latency, last_ts)

        # Get time-windowed stats
        now = time.time()
        history = {}
        for label, days in [("7d", 7), ("30d", 30), ("90d", 90)]:
            cutoff = now - (days * 86400)
            cursor = await db.execute(
                """
                SELECT
                    SUM(CASE WHEN outcome = 'success' THEN 1 ELSE 0 END) as s,
                    COUNT(*) as t,
                    AVG(latency_ms) as lat
                FROM interactions
                WHERE provider_id = ? AND timestamp > ?
                """,
                (provider_id, cutoff),
            )
            h = await cursor.fetchone()
            t = h["t"] or 0
            s = h["s"] or 0
            history[label] = {
                "success_rate": round(s / t, 4) if t > 0 else None,
                "avg_latency_ms": round(h["lat"]) if h["lat"] else None,
                "sample_size": t,
            }

        # Flags
        flags = []
        if scores["sample_size"] < 10:
            flags.append("low_sample_size")
        if history["7d"]["success_rate"] is not None and history["7d"]["success_rate"] < 0.7:
            flags.append("recent_failures")
        if avg_latency and avg_latency > 1000:
            flags.append("high_latency")
        if history["7d"]["success_rate"] and history["30d"]["success_rate"]:
            if history["7d"]["success_rate"] < history["30d"]["success_rate"] - 0.1:
                flags.append("degrading")

        return {
            "provider_id": provider_id,
            "name": provider["name"],
            "endpoint": provider["endpoint"],
            "task_types": provider["task_types"],
            "description": provider["description"],
            "trust_score": scores["trust_score"],
            "reliability": scores["reliability"],
            "avg_latency_ms": round(avg_latency) if avg_latency else None,
            "success_rate_30d": history["30d"]["success_rate"],
            "sample_size": scores["sample_size"],
            "flags": flags,
            "confidence": scores["confidence"],
            "history": history,
        }


async def get_ranked_providers(
    provider_ids: list[str],
    task_type: str = None,
    min_score: float = 0.0,
    db_path: str = None,
) -> list[dict]:
    """Get and rank multiple providers by trust score."""
    results = []
    for pid in provider_ids:
        score = await get_provider_score(pid, task_type, db_path)
        if score and score["trust_score"] >= min_score:
            results.append(score)

    # Also include unknown providers with neutral score (only if above min_score)
    scored_ids = {r["provider_id"] for r in results}
    for pid in provider_ids:
        if pid not in scored_ids and 0.5 >= min_score:
            results.append({
                "provider_id": pid,
                "trust_score": 0.5,
                "reliability": 0.5,
                "avg_latency_ms": None,
                "success_rate_30d": None,
                "sample_size": 0,
                "flags": ["unknown_provider"],
                "confidence": "none",
            })

    results.sort(key=lambda x: x["trust_score"], reverse=True)
    return results


async def discover_providers(
    task_type: str = None,
    min_score: float = 0.0,
    limit: int = 10,
    db_path: str = None,
) -> list[dict]:
    """Discover trusted providers, optionally filtered by task type."""
    path = db_path or str(DB_PATH)
    async with aiosqlite.connect(path) as db:
        db.row_factory = aiosqlite.Row

        if task_type:
            cursor = await db.execute(
                "SELECT provider_id FROM providers WHERE task_types LIKE ?",
                (f"%{task_type}%",),
            )
        else:
            cursor = await db.execute("SELECT provider_id FROM providers")

        rows = await cursor.fetchall()
        provider_ids = [r["provider_id"] for r in rows]

    scores = await get_ranked_providers(provider_ids, task_type, min_score, db_path)
    return scores[:limit]


async def get_contributor_stats(reporter_id: str, db_path: str = None) -> dict:
    """Get contribution stats for a reporter."""
    path = db_path or str(DB_PATH)
    async with aiosqlite.connect(path) as db:
        cursor = await db.execute(
            "SELECT COUNT(*) as total FROM interactions WHERE reporter_id = ?",
            (reporter_id,),
        )
        row = await cursor.fetchone()
        total = row[0] if row else 0

        status = "new" if total < 5 else "active" if total < 100 else "trusted"
        return {"total_contributions": total, "contributor_status": status}
