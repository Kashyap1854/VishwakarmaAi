"""
seed.py — One-time script to seed the monuments collection from requirements.json.
Run: python seed.py
"""
import asyncio
import json
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from config import settings

REQUIREMENTS_JSON = Path(__file__).parent.parent / "backend" / "requirements.json"

async def main():
    client = AsyncIOMotorClient(settings.MONGO_URI)
    db = client[settings.MONGO_DB]
    col = db["monuments"]

    # Drop and re-seed
    await col.drop()

    with open(REQUIREMENTS_JSON, encoding="utf-8") as f:
        data = json.load(f)

    docs = [
        {
            "name":         name,
            "architecture": info.get("architecture", ""),
            "built":        info.get("built", ""),
            "builder":      info.get("builder", ""),
            "location":     info.get("location", ""),
        }
        for name, info in data.items()
    ]

    result = await col.insert_many(docs)
    print(f"✅  Seeded {len(result.inserted_ids)} monuments into MongoDB")
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
