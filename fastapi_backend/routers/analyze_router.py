"""
routers/analyze_router.py — POST /api/analyze

Flow per request:
  1. Validate image
  2. Run CLIP+FAISS in-process (model already loaded, ~0.5s)
  3. Check monument_cache in DB by monument_name
     → HIT:  use stored description/images/sources (instant, no Wikipedia)
     → MISS: fetch Wikipedia, store in monument_cache for future requests
  4. Store FULL analysis in analyses collection (all tab data)
  5. Log to search_logs (perf metrics)
  6. Return AnalysisOut
"""
import uuid, logging
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
import asyncio

from database import analyses_col, monument_cache_col, search_logs_col
from auth import get_current_user
from models import AnalysisOut, GalleryImage, Source

logger = logging.getLogger("vishwakarma.analyze")
router = APIRouter(prefix="/api", tags=["Analysis"])

UPLOADS_DIR = Path(__file__).parent.parent / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)
ALLOWED = {"image/jpeg","image/png","image/webp","image/gif","image/jpg"}
MAX_MB   = 10


def _doc_to_out(doc: dict) -> AnalysisOut:
    return AnalysisOut(
        id=str(doc["_id"]),
        user_email=doc["user_email"],
        image_filename=doc["image_filename"],
        monument_name=doc["monument_name"],
        raw_label=doc.get("raw_label",""),
        db_key=doc.get("db_key",""),
        location=doc.get("location",""),
        architecture=doc.get("architecture",""),
        style=doc.get("style",""),
        built=doc.get("built",""),
        builder=doc.get("builder",""),
        period=doc.get("period",""),
        description=doc.get("description",""),
        features=doc.get("features",[]),
        probabilities=doc.get("probabilities",{}),
        gallery=[GalleryImage(**g) for g in doc.get("gallery",[])],
        sources=[Source(**s) for s in doc.get("sources",[])],
        created_at=doc["created_at"],
    )


@router.post("/analyze", response_model=AnalysisOut, status_code=201)
async def analyze(
    image: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    t0 = datetime.utcnow()

    # ── 1. Validate ───────────────────────────────────────────────
    if image.content_type not in ALLOWED:
        raise HTTPException(415, f"Unsupported: {image.content_type}. Use JPEG/PNG/WEBP.")

    contents  = await image.read()
    file_size = len(contents)
    if file_size > MAX_MB * 1024 * 1024:
        raise HTTPException(413, f"Max {MAX_MB}MB.")

    # ── 2. Save temp file ─────────────────────────────────────────
    ext = Path(image.filename or "img").suffix or ".jpg"
    tmp = UPLOADS_DIR / f"{uuid.uuid4().hex}{ext}"
    tmp.write_bytes(contents)

    # ── 3. Get monument name first (fast CLIP inference) ──────────
    try:
        from services.ai_service import analyze_image_sync, _faiss_search, _resolve, _monument_db
        loop = asyncio.get_event_loop()

        # Run just FAISS search to get monument name
        def _quick_identify():
            raw = _faiss_search(str(tmp))
            return raw, _resolve(raw)

        raw_label, db_key = await loop.run_in_executor(None, _quick_identify)
        monument_name = db_key

        # ── 4. DB-first: check monument_cache ────────────────────
        cached = await monument_cache_col().find_one({"monument_name": monument_name})

        # ── 5. Run full analysis (passes cache if available) ──────
        ai = await loop.run_in_executor(None, analyze_image_sync, str(tmp), cached)

    except Exception as e:
        logger.error(f"Analysis error: {e}", exc_info=True)
        raise HTTPException(500, str(e))
    finally:
        tmp.unlink(missing_ok=True)

    if "error" in ai:
        raise HTTPException(500, ai["error"])

    ai_ms = int((datetime.utcnow() - t0).total_seconds() * 1000)
    name  = ai.get("name", "")
    now   = datetime.utcnow()

    # ── 6. If cache MISS → store in monument_cache ───────────────
    if not cached:
        await monument_cache_col().update_one(
            {"monument_name": name},
            {"$set": {
                "monument_name": name,
                "description":   ai.get("description", ""),
                "images":        ai.get("_raw_images", []),
                "sources":       ai.get("sources", []),
                "architecture":  ai.get("architecture",""),
                "style":         ai.get("style",""),
                "features":      ai.get("features",[]),
                "probabilities": ai.get("probabilities",{}),
                "fetched_at":    now,
                "cache_hits":    0,
            }},
            upsert=True,
        )
    else:
        # Increment hit counter
        await monument_cache_col().update_one(
            {"monument_name": name},
            {"$inc": {"cache_hits": 1}, "$set": {"last_hit": now}},
        )

    # ── 7. Build full analysis doc (all tabs stored) ──────────────
    gallery_clean = [g for g in ai.get("gallery",[]) if not g.get("url","").startswith("_")]
    doc = {
        # meta
        "user_email":       current_user["email"],
        "image_filename":   image.filename,
        "image_size_bytes": file_size,
        "image_mimetype":   image.content_type,
        # details tab
        "monument_name":    name,
        "raw_label":        ai.get("rawLabel",""),
        "db_key":           ai.get("dbKey",""),
        "location":         ai.get("location","India"),
        "architecture":     ai.get("architecture","Traditional Indian"),
        "style":            ai.get("style","Traditional"),
        "built":            ai.get("built","Ancient"),
        "builder":          ai.get("builder","Traditional craftsmen"),
        "period":           ai.get("period","Ancient"),
        "description":      ai.get("description",""),
        # analysis tab
        "features":         ai.get("features",[]),
        "probabilities":    ai.get("probabilities",{}),
        # images tab
        "gallery": [{"url":g.get("url",""), "caption":g.get("caption","")}
                    for g in gallery_clean],
        # sources tab
        "sources": [{"title":s.get("title",""), "description":s.get("description",""),
                     "url":s.get("url",""), "domain":s.get("domain","")}
                    for s in ai.get("sources",[])],
        # perf
        "ai_latency_ms":    ai_ms,
        "cache_hit":        bool(cached),
        "created_at":       t0,
    }

    result = await analyses_col().insert_one(doc)
    doc["_id"] = result.inserted_id

    # ── 8. Log search ─────────────────────────────────────────────
    await search_logs_col().insert_one({
        "user_email":       current_user["email"],
        "monument_name":    name,
        "raw_label":        ai.get("rawLabel",""),
        "ai_latency_ms":    ai_ms,
        "cache_hit":        bool(cached),
        "image_size_bytes": file_size,
        "created_at":       t0,
    })

    logger.info(f"{'⚡ Cache' if cached else '🌐 Fresh'} | {name} | {ai_ms}ms | {current_user['email']}")
    return _doc_to_out(doc)


@router.get("/analyze/stats", tags=["Analysis"])
async def analyze_stats(current_user: dict = Depends(get_current_user)):
    """Performance stats for current user."""
    pipeline = [
        {"$match": {"user_email": current_user["email"]}},
        {"$group": {
            "_id": None,
            "total":     {"$sum": 1},
            "avg_ms":    {"$avg": "$ai_latency_ms"},
            "min_ms":    {"$min": "$ai_latency_ms"},
            "max_ms":    {"$max": "$ai_latency_ms"},
            "cache_hits":{"$sum": {"$cond": ["$cache_hit", 1, 0]}},
            "monuments": {"$addToSet": "$monument_name"},
        }}
    ]
    docs = await search_logs_col().aggregate(pipeline).to_list(1)
    if not docs:
        return {"total":0,"avg_latency_ms":0,"cache_hits":0,"unique_monuments":0}
    s = docs[0]
    return {
        "total":            s["total"],
        "avg_latency_ms":   round(s.get("avg_ms") or 0),
        "min_latency_ms":   s.get("min_ms",0),
        "max_latency_ms":   s.get("max_ms",0),
        "cache_hits":       s.get("cache_hits",0),
        "cache_hit_rate":   f"{round(100*s.get('cache_hits',0)/max(s['total'],1))}%",
        "unique_monuments": len(s.get("monuments",[])),
    }