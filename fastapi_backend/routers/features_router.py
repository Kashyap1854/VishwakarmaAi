from fastapi import APIRouter, HTTPException
from repositories.feature_repository import FeatureRepository
from pydantic import BaseModel
from bson import ObjectId

class FeatureModel(BaseModel):
    name: str
    description: str = ""

router = APIRouter(prefix="/api/features", tags=["Features"])

@router.get("", response_model=list[FeatureModel])
async def get_all_features():
    docs = await FeatureRepository.get_all()
    return [FeatureModel(**doc) for doc in docs]

@router.get("/{feature_id}", response_model=FeatureModel)
async def get_feature(feature_id: str):
    doc = await FeatureRepository.get_by_id(ObjectId(feature_id))
    if not doc:
        raise HTTPException(status_code=404, detail="Feature not found")
    return FeatureModel(**doc)

@router.post("", response_model=str)
async def create_feature(feature: FeatureModel):
    inserted_id = await FeatureRepository.create(feature.model_dump())
    return str(inserted_id)

@router.put("/{feature_id}")
async def update_feature(feature_id: str, feature: FeatureModel):
    await FeatureRepository.update(ObjectId(feature_id), feature.model_dump())
    return {"message": "Updated"}

@router.delete("/{feature_id}")
async def delete_feature(feature_id: str):
    await FeatureRepository.delete(ObjectId(feature_id))
    return {"message": "Deleted"}
