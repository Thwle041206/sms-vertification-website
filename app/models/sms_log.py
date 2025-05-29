from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId
from app.config.database import db
from datetime import datetime

class SMSLogSchema(BaseModel):
    id: Optional[str] = Field(None, alias='_id')
    phone_number: str = Field(...)
    message_content: str = Field(...)
    received_at: datetime = Field(default_factory=datetime.now)
    status: str = Field(default="received")

    class Config:
        json_encoders = {
            ObjectId: str,
            datetime: lambda dt: dt.isoformat()
        }
        json_schema_extra = {
            "example": {
                "phone_number": "+1234567890",
                "message_content": "Your verification code is 123456",
                "status": "received"
            }
        }

class SMSLog:
    collection = db['sms_logs']

    @staticmethod
    def create_sms_log(sms_log_data: dict) -> str:
        sms_log_data['received_at'] = datetime.now()
        result = SMSLog.collection.insert_one(sms_log_data)
        return str(result.inserted_id)

    @staticmethod
    def get_sms_log_by_id(sms_log_id: str) -> Optional[dict]:
        return SMSLog.collection.find_one({'_id': ObjectId(sms_log_id)})

    @staticmethod
    def get_sms_logs_by_phone_number(phone_number: str) -> list:
        return list(SMSLog.collection.find({'phone_number': phone_number}).sort('received_at', -1))
