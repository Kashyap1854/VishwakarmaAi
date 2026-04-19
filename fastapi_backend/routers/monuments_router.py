"""
routers/monuments_router.py — /api/monuments
Seeds the monuments collection from requirements.json on first call,
then serves from MongoDB.
"""
import json
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from database import monuments_col
from models import MonumentOut, MessageResponse

router = APIRouter(prefix="/api/monuments", tags=["Monuments"])

REQUIREMENTS_JSON = Path(__file__).parent.parent.parent / "backend" / "requirements.json"


async def seed_monuments_if_empty():
    """Seed monuments collection from requirements.json if empty."""
    count = await monuments_col().count_documents({})
    if count > 0:
        return count

    if not REQUIREMENTS_JSON.exists():
        return 0

    with open(REQUIREMENTS_JSON, encoding="utf-8") as f:
        db = json.load(f)

    docs = []
    for name, info in db.items():
        docs.append({
            "name":         name,
            "architecture": info.get("architecture", ""),
            "built":        info.get("built", ""),
            "builder":      info.get("builder", ""),
            "location":     info.get("location", ""),
        })

    if docs:
        await monuments_col().insert_many(docs, ordered=False)

    return len(docs)


# ── GET /api/monuments ────────────────────────────────────────────────────────
@router.get("", response_model=List[MonumentOut])
async def list_monuments(
    style: Optional[str] = Query(None, description="Filter by architecture style"),
    search: Optional[str] = Query(None, description="Search monument name"),
):
    await seed_monuments_if_empty()

    query: dict = {}
    if style:
        query["architecture"] = {"$regex": style, "$options": "i"}
    if search:
        query["name"] = {"$regex": search, "$options": "i"}

    cursor = monuments_col().find(query).sort("name", 1)
    items = []
    async for doc in cursor:
        items.append(MonumentOut(
            id=str(doc["_id"]),
            name=doc["name"],
            architecture=doc.get("architecture", ""),
            built=doc.get("built", ""),
            builder=doc.get("builder", ""),
            location=doc.get("location", ""),
        ))
    return items


# ── GET /api/monuments/{name} ─────────────────────────────────────────────────
@router.get("/{name}", response_model=MonumentOut)
async def get_monument(name: str):
    await seed_monuments_if_empty()

    doc = await monuments_col().find_one({"name": {"$regex": f"^{name}$", "$options": "i"}})
    if not doc:
        raise HTTPException(status_code=404, detail=f"Monument '{name}' not found")

    return MonumentOut(
        id=str(doc["_id"]),
        name=doc["name"],
        architecture=doc.get("architecture", ""),
        built=doc.get("built", ""),
        builder=doc.get("builder", ""),
        location=doc.get("location", ""),
    )


# ── POST /api/monuments/seed ──────────────────────────────────────────────────
@router.post("/seed", response_model=MessageResponse)
async def force_seed():
    """Force re-seed monuments from requirements.json (drops existing first)."""
    await monuments_col().drop()

    if not REQUIREMENTS_JSON.exists():
        raise HTTPException(status_code=404, detail="requirements.json not found")

    with open(REQUIREMENTS_JSON, encoding="utf-8") as f:
        db = json.load(f)

    docs = [
        {
            "name":         name,
            "architecture": info.get("architecture", ""),
            "built":        info.get("built", ""),
            "builder":      info.get("builder", ""),
            "location":     info.get("location", ""),
        }
        for name, info in db.items()
    ]
    await monuments_col().insert_many(docs)
    return MessageResponse(message=f"Seeded {len(docs)} monuments into MongoDB")
