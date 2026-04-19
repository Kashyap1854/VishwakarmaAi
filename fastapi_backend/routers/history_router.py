"""
routers/history_router.py — /api/history
Returns paginated analysis history for the logged-in user.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from bson import ObjectId
from datetime import datetime
from typing import List

from database import analyses_col
from auth import get_current_user
from models import AnalysisOut, HistoryItem, MessageResponse, GalleryImage, Source

router = APIRouter(prefix="/api/history", tags=["History"])


def doc_to_out(doc: dict) -> AnalysisOut:
    return AnalysisOut(
        id=str(doc["_id"]),
        user_email=doc["user_email"],
        image_filename=doc.get("image_filename", ""),
        monument_name=doc["monument_name"],
        raw_label=doc.get("raw_label", ""),
        db_key=doc.get("db_key", ""),
        location=doc.get("location", ""),
        architecture=doc.get("architecture", ""),
        style=doc.get("style", ""),
        built=doc.get("built", ""),
        builder=doc.get("builder", ""),
        period=doc.get("period", ""),
        description=doc.get("description", ""),
        features=doc.get("features", []),
        probabilities=doc.get("probabilities", {}),
        gallery=[GalleryImage(**g) for g in doc.get("gallery", [])],
        sources=[Source(**s) for s in doc.get("sources", [])],
        created_at=doc["created_at"],
    )


# ── GET /api/history  — paginated list ───────────────────────────────────────
@router.get("", response_model=List[HistoryItem])
async def get_history(
    skip:  int = Query(0,  ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
):
    cursor = (
        analyses_col()
        .find({"user_email": current_user["email"]})
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    )

    items = []
    async for doc in cursor:
        items.append(HistoryItem(
            id=str(doc["_id"]),
            monument_name=doc["monument_name"],
            style=doc.get("style", ""),
            architecture=doc.get("architecture", ""),
            built=doc.get("built", ""),
            location=doc.get("location", ""),
            created_at=doc["created_at"],
        ))
    return items


# ── GET /api/history/{id}  — single full analysis ────────────────────────────
@router.get("/{analysis_id}", response_model=AnalysisOut)
async def get_analysis(
    analysis_id: str,
    current_user: dict = Depends(get_current_user),
):
    if not ObjectId.is_valid(analysis_id):
        raise HTTPException(status_code=400, detail="Invalid analysis ID")

    doc = await analyses_col().find_one({
        "_id":        ObjectId(analysis_id),
        "user_email": current_user["email"],
    })
    if not doc:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return doc_to_out(doc)


# ── DELETE /api/history/{id}  — delete one ───────────────────────────────────
@router.delete("/{analysis_id}", response_model=MessageResponse)
async def delete_analysis(
    analysis_id: str,
    current_user: dict = Depends(get_current_user),
):
    if not ObjectId.is_valid(analysis_id):
        raise HTTPException(status_code=400, detail="Invalid analysis ID")

    result = await analyses_col().delete_one({
        "_id":        ObjectId(analysis_id),
        "user_email": current_user["email"],
    })
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return MessageResponse(message="Analysis deleted")


# ── DELETE /api/history  — clear all for user ────────────────────────────────
@router.delete("", response_model=MessageResponse)
async def clear_history(current_user: dict = Depends(get_current_user)):
    result = await analyses_col().delete_many({"user_email": current_user["email"]})
    return MessageResponse(message=f"Deleted {result.deleted_count} analyses")
