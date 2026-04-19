"""
models.py — Pydantic schemas for all request bodies, responses, and DB documents.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ─── AUTH ─────────────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    name: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ─── GALLERY / SOURCE ─────────────────────────────────────────────────────────

class GalleryImage(BaseModel):
    url: str
    caption: str


class Source(BaseModel):
    title: str
    description: str
    url: str
    domain: str


# ─── ANALYSIS ─────────────────────────────────────────────────────────────────

class AnalysisResult(BaseModel):
    """Mirrors exactly what analyze.py returns — stored whole in MongoDB."""
    name: str
    raw_label: str
    db_key: str
    location: str
    architecture: str
    style: str
    built: str
    builder: str
    period: str
    description: str
    features: List[str]
    probabilities: Dict[str, int]
    gallery: List[GalleryImage]
    sources: List[Source]


class AnalysisDocument(BaseModel):
    """Full document stored in the analyses collection."""
    user_email: str
    image_filename: str
    image_size_bytes: int
    image_mimetype: str
    # All AI-generated fields
    monument_name: str
    raw_label: str
    db_key: str
    location: str
    architecture: str
    style: str
    built: str
    builder: str
    period: str
    description: str
    features: List[str]
    probabilities: Dict[str, int]
    gallery: List[Dict[str, str]]
    sources: List[Dict[str, str]]
    # Meta
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AnalysisOut(BaseModel):
    """What the API returns to the frontend — includes DB id and timestamp."""
    id: str
    user_email: str
    image_filename: str
    monument_name: str
    raw_label: str
    db_key: str
    location: str
    architecture: str
    style: str
    built: str
    builder: str
    period: str
    description: str
    features: List[str]
    probabilities: Dict[str, int]
    gallery: List[GalleryImage]
    sources: List[Source]
    created_at: datetime


# ─── MONUMENT ─────────────────────────────────────────────────────────────────

class MonumentDocument(BaseModel):
    """One entry from requirements.json, seeded into MongoDB."""
    name: str
    architecture: str
    built: str
    builder: str
    location: str


class MonumentOut(MonumentDocument):
    id: str


# ─── HISTORY ──────────────────────────────────────────────────────────────────

class HistoryItem(BaseModel):
    """Lightweight summary for history lists."""
    id: str
    monument_name: str
    style: str
    architecture: str
    built: str
    location: str
    created_at: datetime


# ─── GENERIC ──────────────────────────────────────────────────────────────────

class MessageResponse(BaseModel):
    message: str


class HealthResponse(BaseModel):
    status: str
    mongo: str
    timestamp: datetime
