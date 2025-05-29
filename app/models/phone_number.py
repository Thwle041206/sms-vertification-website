'''
Giải thích các thành phần chính:

SMSMessage Model:

Định nghĩa cấu trúc tin nhắn SMS nhận được
Bao gồm nội dung, số gửi và thời gian nhận
PhoneNumberStatus Enum:

Các trạng thái của số điện thoại: active, inactive, banned
PhoneNumberSchema (Pydantic Model):

Định nghĩa cấu trúc dữ liệu số điện thoại với tất cả các trường yêu cầu
Validation cho số điện thoại theo chuẩn E.164
Giá trị mặc định hợp lý cho các trường
PhoneNumber Class (MongoDB Operations):

create_phone_number: Tạo bản ghi số điện thoại mới
get_available_number: Lấy số điện thoại khả dụng
assign_to_user: Gán số cho người dùng
release_number: Giải phóng số (khi không dùng nữa)
add_sms_message: Thêm tin nhắn vào lịch sử SMS
extend_expiration: Gia hạn thời gian sử dụng số
get_numbers_by_user: Lấy tất cả số của người dùng
update_number_status: Cập nhật trạng thái số
get_active_numbers_by_service: Lấy số active theo dịch vụ
Cách sử dụng cơ bản:
# Tạo số điện thoại mới
phone_data = {
    "number": "+1234567890",
    "country_id": "507f1f77bcf86cd799439011",
    "service_id": "507f1f77bcf86cd799439012",
    "provider": "Twilio"
}
phone_id = PhoneNumber.create_phone_number(phone_data)

# Lấy số khả dụng
available_number = PhoneNumber.get_available_number(
    service_id="507f1f77bcf86cd799439012",
    country_id="507f1f77bcf86cd799439011"
)

# Gán số cho người dùng
PhoneNumber.assign_to_user(phone_id, "507f1f77bcf86cd799439013")

# Thêm tin nhắn nhận được
PhoneNumber.add_sms_message(phone_id, {
    "content": "Your code is 123456",
    "from": "+1987654321"
})

'''

from typing import List, Optional, Dict, Any
from bson import ObjectId
from pydantic import BaseModel, Field, validator
from datetime import datetime, timedelta
from app.config.database import db
from enum import Enum

class SMSMessage(BaseModel):
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    from_number: str = Field(..., alias='from')

    class Config:
        validate_by_name = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

class PhoneNumberStatus(str, Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    BANNED = 'banned'

class PhoneNumberSchema(BaseModel):
    id: Optional[str] = Field(None, alias='_id')
    number: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$')  # E.164 format
    country_id: str
    service_id: str
    provider: str = Field(..., min_length=2, max_length=50)
    status: PhoneNumberStatus = Field(default=PhoneNumberStatus.ACTIVE)
    is_used: bool = Field(default=False)
    current_user: Optional[str] = None
    expiration_time: datetime = Field(
        default_factory=lambda: datetime.now() + timedelta(days=30)
    )
    last_used: Optional[datetime] = None
    sms_received: List[SMSMessage] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_encoders = {
            ObjectId: str,
            datetime: lambda dt: dt.isoformat()
        }
        json_schema_extra = {
            "example": {
                "number": "+1234567890",
                "country_id": "507f1f77bcf86cd799439011",
                "service_id": "507f1f77bcf86cd799439012",
                "provider": "Twilio",
                "status": "active",
                "sms_received": [{
                    "content": "Your verification code is 123456",
                    "from": "+1987654321",
                    "timestamp": "2023-01-01T12:00:00Z"
                }]
            }
        }

    @validator('number')
    def normalize_phone_number(cls, v):
        """Normalize phone number to E.164 format"""
        if v.startswith('00'):
            return '+' + v[2:]
        return v

class PhoneNumber:
    collection = db['phone_numbers']

    @staticmethod
    def create_phone_number(phone_data: dict) -> str:
        """Create a new phone number record"""
        phone_data['created_at'] = datetime.now()
        phone_data['updated_at'] = datetime.now()
        result = PhoneNumber.collection.insert_one(phone_data)
        return str(result.inserted_id)

    @staticmethod
    def get_available_number(service_id: str, country_id: str) -> Optional[dict]:
        """Get an available phone number for the service and country"""
        return PhoneNumber.collection.find_one_and_update(
            {
                'service_id': ObjectId(service_id),
                'country_id': ObjectId(country_id),
                'is_used': False,
                'status': PhoneNumberStatus.ACTIVE.value,
                'expiration_time': {'$gt': datetime.now()}
            },
            {
                '$set': {
                    'is_used': True,
                    'updated_at': datetime.now()
                }
            },
            return_document=True
        )

    @staticmethod
    def assign_to_user(number_id: str, user_id: str) -> bool:
        """Assign a phone number to a user"""
        result = PhoneNumber.collection.update_one(
            {
                '_id': ObjectId(number_id),
                'is_used': False
            },
            {
                '$set': {
                    'current_user': ObjectId(user_id),
                    'is_used': True,
                    'last_used': datetime.now(),
                    'updated_at': datetime.now()
                }
            }
        )
        return result.modified_count > 0

    @staticmethod
    def release_number(number_id: str) -> bool:
        """Release a phone number (make it available again)"""
        result = PhoneNumber.collection.update_one(
            {'_id': ObjectId(number_id)},
            {
                '$set': {
                    'current_user': None,
                    'is_used': False,
                    'updated_at': datetime.now()
                }
            }
        )
        return result.modified_count > 0

    @staticmethod
    def add_sms_message(number_id: str, message_data: dict) -> bool:
        """Add a received SMS message to the phone number's history"""
        message_data['timestamp'] = datetime.now()
        result = PhoneNumber.collection.update_one(
            {'_id': ObjectId(number_id)},
            {
                '$push': {'sms_received': message_data},
                '$set': {'updated_at': datetime.now()}
            }
        )
        return result.modified_count > 0

    @staticmethod
    def extend_expiration(number_id: str, days: int = 7) -> bool:
        """Extend the expiration time of a phone number"""
        result = PhoneNumber.collection.update_one(
            {'_id': ObjectId(number_id)},
            {
                '$set': {
                    'expiration_time': datetime.now() + timedelta(days=days),
                    'updated_at': datetime.now()
                }
            }
        )
        return result.modified_count > 0

    @staticmethod
    def get_numbers_by_user(user_id: str) -> List[dict]:
        """Get all phone numbers assigned to a user"""
        return list(PhoneNumber.collection.find({
            'current_user': ObjectId(user_id)
        }))

    @staticmethod
    def update_number_status(number_id: str, status: PhoneNumberStatus) -> bool:
        """Update the status of a phone number (active/inactive/banned)"""
        result = PhoneNumber.collection.update_one(
            {'_id': ObjectId(number_id)},
            {
                '$set': {
                    'status': status.value,
                    'updated_at': datetime.now()
                }
            }
        )
        return result.modified_count > 0

    @staticmethod
    def get_active_numbers_by_service(service_id: str) -> List[dict]:
        """Get all active phone numbers for a service"""
        return list(PhoneNumber.collection.find({
            'service_id': ObjectId(service_id),
            'status': PhoneNumberStatus.ACTIVE.value
        }))
