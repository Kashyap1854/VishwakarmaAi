"""
database.py — Motor async MongoDB client.

Collections in vishwakarma_ai:
  users            — accounts (email, name, password hash, created_at)
  analyses         — every full analysis (all tabs data stored here)
  monuments        — static monument DB seeded from requirements.json
  monument_cache   — per-monument cached data: description, images, sources
  search_logs      — lightweight perf log per search (latency, user, monument)
  sessions         — reserved for future session tracking
"""
from motor.motor_asyncio import AsyncIOMotorClient
from config import settings

_client = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(
            settings.MONGO_URI,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
        )
    return _client


def get_db():
    return get_client()[settings.MONGO_DB]


# ── Collection accessors ──────────────────────────────────────────────────────
def users_col():          return get_db()["users"]
def analyses_col():       return get_db()["analyses"]
def monuments_col():      return get_db()["monuments"]
def monument_cache_col(): return get_db()["monument_cache"]   # wiki+gallery+sources per monument
def search_logs_col():    return get_db()["search_logs"]
def sessions_col():       return get_db()["sessions"]


# ── Startup / Shutdown ────────────────────────────────────────────────────────
async def connect_db():
    client = get_client()
    await client.admin.command("ping")
    print(f"✅  MongoDB → {settings.MONGO_URI} / {settings.MONGO_DB}")
    await _ensure_indexes()
    print("✅  Indexes ready")


async def _ensure_indexes():
    # users
    await users_col().create_index("email", unique=True)

    # analyses — every field the frontend reads
    await analyses_col().create_index("user_email")
    await analyses_col().create_index("created_at")
    await analyses_col().create_index("monument_name")
    await analyses_col().create_index([("user_email", 1), ("created_at", -1)])

    # monuments
    await monuments_col().create_index("name", unique=True)
    await monuments_col().create_index("architecture")

    # monument_cache — one doc per monument, keyed by name
    await monument_cache_col().create_index("monument_name", unique=True)
    await monument_cache_col().create_index("fetched_at")

    # search_logs
    await search_logs_col().create_index("user_email")
    await search_logs_col().create_index("created_at")
    await search_logs_col().create_index("monument_name")


async def close_db():
    global _client
    if _client:
        _client.close()
        _client = None
        print("MongoDB connection closed")