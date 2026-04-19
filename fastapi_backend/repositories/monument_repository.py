from database import monuments_col

class MonumentRepository:
    @staticmethod
    async def get_all():
        cursor = monuments_col().find()
        return [doc async for doc in cursor]

    @staticmethod
    async def get_by_id(monument_id):
        return await monuments_col().find_one({"_id": monument_id})

    @staticmethod
    async def create(monument):
        result = await monuments_col().insert_one(monument)
        return result.inserted_id

    @staticmethod
    async def update(monument_id, update):
        await monuments_col().update_one({"_id": monument_id}, {"$set": update})

    @staticmethod
    async def delete(monument_id):
        await monuments_col().delete_one({"_id": monument_id})
