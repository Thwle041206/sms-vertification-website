'''
Giải thích các thành phần chính:

UserStatus Enum: Định nghĩa các trạng thái có thể có của user
UserSchema (Pydantic Model):

Định nghĩa cấu trúc dữ liệu user với các trường đầy đủ như yêu cầu
Bao gồm validation cho email (EmailStr) và phone number
Có các giá trị mặc định cho các trường như balance, status, verification_level
Hỗ trợ chuyển đổi ObjectId và datetime khi trả về JSON
User Class (MongoDB Operations):

create_user: Tạo user mới với các giá trị mặc định
find_by_id/find_by_email: Tìm user bằng ID hoặc email
update_login_time: Cập nhật thời gian đăng nhập cuối và lưu IP
update_balance: Cập nhật số dư tài khoản
update_status: Thay đổi trạng thái user (active/suspended)
set_api_key: Gán API key cho user
increase_verification_level: Tăng cấp độ xác thực
Cách sử dụng cơ bản:
# Tạo user mới
user_data = {
    "username": "john_doe",
    "email": "john@example.com",
    "password": "hashed_password",
    "phone": "+1234567890"
}
user_id = User.create_user(user_data)

# Tìm user bằng email
user = User.find_by_email("john@example.com")

# Cập nhật thời gian đăng nhập
User.update_login_time(user_id, "192.168.1.1")

# Cập nhật số dư
new_balance = User.update_balance(user_id, 50.0)
'''

from typing import Optional, Dict, Any, List
from datetime import datetime
from bson import ObjectId
from app.config.database import db
from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional
from enum import Enum

class UserStatus(str, Enum):
    ACTIVE = 'active'
    SUSPENDED = 'suspended'

class UserSchema(BaseModel):
    id: Optional[str] = Field(alias='_id')
    username: str
    email: EmailStr
    password: str
    phone: str
    balance: float = Field(default=0.0)
    api_key: Optional[str] = None
    registration_date: datetime = Field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    status: UserStatus = Field(default=UserStatus.ACTIVE)
    ip_history: List[str] = Field(default_factory=list)
    verification_level: int = Field(default=0, ge=0, le=5)

    class Config:
        json_encoders = {
            ObjectId: str,
            datetime: lambda dt: dt.isoformat()
        }
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john@example.com",
                "password": "securepassword123",
                "phone": "+1234567890",
                "balance": 100.50,
                "status": "active",
                "verification_level": 1
            }
        }

    @validator('phone')
    def validate_phone(cls, v):
        if not v.startswith('+'):
            raise ValueError('Phone number must start with +')
        return v

class User:
    collection = db['users']

    @staticmethod
    async def create_user(user_data: dict) -> str:
        """Create a new user with default values"""
        user_data['balance'] = user_data.get('balance', 0)
        user_data['status'] = user_data.get('status', UserStatus.ACTIVE.value)
        user_data['verification_level'] = user_data.get('verification_level', 0)
        user_data['registration_date'] = datetime.now()
        user_data['ip_history'] = user_data.get('ip_history', [])
        
        result = await User.collection.insert_one(user_data)
        return str(result.inserted_id)

    @staticmethod
    def find_by_id(user_id: str) -> Optional[dict]:
        """Find user by ID"""
        return User.collection.find_one({'_id': ObjectId(user_id)})

    @staticmethod
    def find_by_email(email: str) -> Optional[dict]:
        """Find user by email"""
        return User.collection.find_one({'email': email})

    @staticmethod
    def update_login_time(user_id: str, ip_address: str) -> None:
        """Update last login time and add IP to history"""
        User.collection.update_one(
            {'_id': ObjectId(user_id)},
            {
                '$set': {'last_login': datetime.now()},
                '$addToSet': {'ip_history': ip_address}
            }
        )

    @staticmethod
    def update_balance(user_id: str, amount: float) -> Optional[float]:
        """Update user balance and return new balance"""
        result = User.collection.find_one_and_update(
            {'_id': ObjectId(user_id)},
            {'$inc': {'balance': amount}},
            return_document=True
        )
        return result['balance'] if result else None

    @staticmethod
    def update_status(user_id: str, status: UserStatus) -> bool:
        """Update user status"""
        result = User.collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'status': status.value}}
        )
        return result.modified_count > 0

    @staticmethod
    def set_api_key(user_id: str, api_key: str) -> bool:
        """Set API key for user"""
        result = User.collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'api_key': api_key}}
        )
        return result.modified_count > 0

    @staticmethod
    def increase_verification_level(user_id: str) -> Optional[int]:
        """Increase user verification level by 1 (max 5)"""
        result = User.collection.find_one_and_update(
            {'_id': ObjectId(user_id), 'verification_level': {'$lt': 5}},
            {'$inc': {'verification_level': 1}},
            return_document=True
        )
        return result['verification_level'] if result else None