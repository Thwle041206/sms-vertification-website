from motor.motor_asyncio import AsyncIOMotorClient
from app.config.settings import settings

# Khởi tạo client và db ngay khi import
client = AsyncIOMotorClient(settings.mongo_uri)
db = client[settings.mongo_db_name]

async def connect_to_mongo():
    global client, db
    try:
        client = AsyncIOMotorClient(settings.mongo_uri)  # Sửa thành settings.mongo_uri
        db = client[settings.mongo_db_name]  # Sửa thành settings.mongo_db_name
        await db.command('ping')
        print("Connected to MongoDB")
        return True
    except Exception as e:
        print(f"MongoDB connection error: {e}")
        return False

async def close_mongo_connection():
    global client
    if client:
        client.close()
        print("❌ Disconnected from MongoDB")

