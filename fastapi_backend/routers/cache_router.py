"""
routers/cache_router.py — /api/cache
Read monument_cache collection.
monument_cache stores: description, images, sources, features, probabilities
— all tab data cached per unique monument name.
"""
from fastapi import APIRouter, HTTPException
from database import monument_cache_col, search_logs_col

router = APIRouter(prefix="/api/cache", tags=["Cache"])


@router.get("/{monument_name}")
async def get_monument_cache(monument_name: str):
    """Return all cached data for a monument (all tabs)."""
    doc = await monument_cache_col().find_one({"monument_name": monument_name})
    if not doc:
        raise HTTPException(404, f"No cache for '{monument_name}'")
    doc.pop("_id", None)
    return doc


@router.get("")
async def list_cached():
    """List all cached monuments with hit counts."""
    cursor = monument_cache_col().find(
        {}, {"monument_name":1,"cache_hits":1,"fetched_at":1,"_id":0}
    ).sort("cache_hits", -1)
    return await cursor.to_list(200)


@router.get("/stats/global")
async def global_stats():
    """Global cache + performance stats."""
    cached   = await monument_cache_col().count_documents({})
    total_searches = await search_logs_col().count_documents({})
    cache_hits     = await search_logs_col().count_documents({"cache_hit": True})
    pipeline = [{"$group": {"_id": None,
                             "avg_ms": {"$avg": "$ai_latency_ms"},
                             "min_ms": {"$min": "$ai_latency_ms"},
                             "max_ms": {"$max": "$ai_latency_ms"}}}]
    perf = await search_logs_col().aggregate(pipeline).to_list(1)
    perf = perf[0] if perf else {}
    return {
        "monuments_cached":  cached,
        "total_searches":    total_searches,
        "cache_hits":        cache_hits,
        "cache_misses":      total_searches - cache_hits,
        "cache_hit_rate":    f"{round(100*cache_hits/max(total_searches,1))}%",
        "avg_latency_ms":    round(perf.get("avg_ms") or 0),
        "min_latency_ms":    perf.get("min_ms", 0),
        "max_latency_ms":    perf.get("max_ms", 0),
    }