"""
main.py — FastAPI application entry point.
Start: uvicorn main:app --host 0.0.0.0 --port 5000 --reload

Startup sequence:
  1. Connect MongoDB + ensure indexes
  2. Seed monuments collection if empty
  3. Load CLIP + FAISS into memory (once, ~5-8s)
     All subsequent requests use the loaded model — no subprocess, no cold start.
"""
import sys, asyncio, logging

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

logging.basicConfig(level=logging.INFO, format="%(name)s | %(levelname)s | %(message)s")

from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from database import connect_db, close_db, get_client

from routers.auth_router      import router as auth_router
from routers.analyze_router   import router as analyze_router
from routers.history_router   import router as history_router
from routers.monuments_router import router as monuments_router
from routers.cache_router     import router as cache_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Database
    await connect_db()

    # 2. Seed monuments if empty
    from routers.monuments_router import seed_monuments_if_empty
    n = await seed_monuments_if_empty()
    if n:
        print(f"✅  Monuments seeded: {n}")

    # 3. Load AI models in thread (non-blocking)
    loop = asyncio.get_event_loop()
    from services.ai_service import load_ai_models
    await loop.run_in_executor(None, load_ai_models)

    yield
    await close_db()


app = FastAPI(
    title="Vishwakarma AI API",
    description="AI-powered Indian monument recognition — FastAPI + MongoDB",
    version="3.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(analyze_router)
app.include_router(history_router)
app.include_router(monuments_router)
app.include_router(cache_router)


@app.get("/api/health", tags=["Health"])
async def health():
    try:
        await get_client().admin.command("ping")
        mongo = "connected"
    except Exception as e:
        mongo = f"error: {e}"
    return {"status": "ok", "mongo": mongo, "timestamp": datetime.utcnow().isoformat()}


@app.get("/", tags=["Root"])
async def root():
    return {"app": "Vishwakarma AI", "version": "3.0.0", "docs": "/docs"}