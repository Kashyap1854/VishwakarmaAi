from fastapi import APIRouter, HTTPException
from repositories.image_repository import ImageRepository
from models import GalleryImage
from bson import ObjectId

router = APIRouter(prefix="/api/images", tags=["Images"])

@router.get("", response_model=list[GalleryImage])
async def get_all_images():
    docs = await ImageRepository.get_all()
    return [GalleryImage(**doc) for doc in docs]

@router.get("/{image_id}", response_model=GalleryImage)
async def get_image(image_id: str):
    doc = await ImageRepository.get_by_id(ObjectId(image_id))
    if not doc:
        raise HTTPException(status_code=404, detail="Image not found")
    return GalleryImage(**doc)

@router.post("", response_model=str)
async def create_image(image: GalleryImage):
    inserted_id = await ImageRepository.create(image.model_dump())
    return str(inserted_id)

@router.put("/{image_id}")
async def update_image(image_id: str, image: GalleryImage):
    await ImageRepository.update(ObjectId(image_id), image.model_dump())
    return {"message": "Updated"}

@router.delete("/{image_id}")
async def delete_image(image_id: str):
    await ImageRepository.delete(ObjectId(image_id))
    return {"message": "Deleted"}
