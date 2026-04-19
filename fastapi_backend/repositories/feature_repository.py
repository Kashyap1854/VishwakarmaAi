from database import features_col

class FeatureRepository:
    @staticmethod
    async def get_all():
        cursor = features_col().find()
        return [doc async for doc in cursor]

    @staticmethod
    async def get_by_id(feature_id):
        return await features_col().find_one({"_id": feature_id})

    @staticmethod
    async def create(feature):
        result = await features_col().insert_one(feature)
        return result.inserted_id

    @staticmethod
    async def update(feature_id, update):
        await features_col().update_one({"_id": feature_id}, {"$set": update})

    @staticmethod
    async def delete(feature_id):
        await features_col().delete_one({"_id": feature_id})
