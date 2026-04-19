from database import images_col

class ImageRepository:
    @staticmethod
    async def get_all():
        cursor = images_col().find()
        return [doc async for doc in cursor]

    @staticmethod
    async def get_by_id(image_id):
        return await images_col().find_one({"_id": image_id})

    @staticmethod
    async def create(image):
        result = await images_col().insert_one(image)
        return result.inserted_id

    @staticmethod
    async def update(image_id, update):
        await images_col().update_one({"_id": image_id}, {"$set": update})

    @staticmethod
    async def delete(image_id):
        await images_col().delete_one({"_id": image_id})
