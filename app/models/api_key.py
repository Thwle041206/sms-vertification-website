from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId
from app.config.database import db
from datetime import datetime

class APIKeySchema(BaseModel):
    id: Optional[str] = Field(None, alias='_id')
    key: str = Field(..., min_length=32, max_length=64)
    user_id: str
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    is_active: bool = Field(default=True)

    class Config:
        json_encoders = {
            ObjectId: str,
            datetime: lambda dt: dt.isoformat()
        }
        json_schema_extra = {
            "example": {
                "key": "1234567890abcdef1234567890abcdef",
                "user_id": "507f1f77bcf86cd799439011",
                "is_active": True
            }
        }

class APIKey:
    collection = db['api_keys']

    @staticmethod
    def create_api_key(api_key_data: dict) -> str:
        api_key_data['created_at'] = datetime.now()
        result = APIKey.collection.insert_one(api_key_data)
        return str(result.inserted_id)

    @staticmethod
    def get_api_key_by_id(api_key_id: str) -> Optional[dict]:
        return APIKey.collection.find_one({'_id': ObjectId(api_key_id)})

    @staticmethod
    def deactivate_api_key(api_key_id: str) -> bool:
        result = APIKey.collection.update_one(
            {'_id': ObjectId(api_key_id)},
            {'$set': {'is_active': False}}
        )
        return result.modified_count > 0

    @staticmethod
    def activate_api_key(api_key_id: str) -> bool:
        result = APIKey.collection.update_one(
            {'_id': ObjectId(api_key_id)},
            {'$set': {'is_active': True}}
        )
        return result.modified_count > 0
