'''
Giải thích các thành phần chính:

OrderStatus Enum:

Các trạng thái đơn hàng: pending, active, completed, failed
OrderSchema (Pydantic Model):

Định nghĩa cấu trúc đơn hàng với tất cả các trường yêu cầu
Validation cho verification code (chỉ chứa số)
Giá trị mặc định hợp lý cho các trường
Order Class (MongoDB Operations):

create_order: Tạo đơn hàng mới
get_order_by_id: Lấy thông tin đơn hàng bằng ID
update_order_status: Cập nhật trạng thái đơn hàng
set_verification_code: Thiết lập mã xác thực
get_active_orders_by_user: Lấy đơn hàng active của người dùng
get_completed_orders_by_service: Lấy đơn hàng đã hoàn thành theo dịch vụ
get_orders_by_phone_number: Lấy đơn hàng theo số điện thoại
expire_pending_orders: Đánh dấu đơn hàng pending quá hạn là failed
Cách sử dụng cơ bản:

# Tạo đơn hàng mới
order_data = {
    "user_id": "507f1f77bcf86cd799439011",
    "service_id": "507f1f77bcf86cd799439012",
    "country_id": "507f1f77bcf86cd799439013",
    "phone_number_id": "507f1f77bcf86cd799439014",
    "price": 0.50,
    "ip_address": "192.168.1.1"
}
order_id = Order.create_order(order_data)

# Cập nhật trạng thái đơn hàng
Order.update_order_status(order_id, OrderStatus.ACTIVE)

# Thiết lập mã xác thực
Order.set_verification_code(order_id, "123456")

# Lấy đơn hàng active của người dùng
active_orders = Order.get_active_orders_by_user("507f1f77bcf86cd799439011")
'''

from typing import Optional, List
from bson import ObjectId
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum
from app.config.database import db

class OrderStatus(str, Enum):
    PENDING = 'pending'
    ACTIVE = 'active'
    COMPLETED = 'completed'
    FAILED = 'failed'

class OrderSchema(BaseModel):
    id: Optional[str] = Field(None, alias='_id')
    user_id: str
    service_id: str
    country_id: str
    phone_number_id: str
    price: float = Field(..., gt=0)
    status: OrderStatus = Field(default=OrderStatus.PENDING)
    start_time: datetime = Field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    verification_code: Optional[str] = Field(None, min_length=4, max_length=8)
    ip_address: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_encoders = {
            ObjectId: str,
            datetime: lambda dt: dt.isoformat()
        }
        json_schema_extra = {
            "example": {
                "user_id": "507f1f77bcf86cd799439011",
                "service_id": "507f1f77bcf86cd799439012",
                "country_id": "507f1f77bcf86cd799439013",
                "phone_number_id": "507f1f77bcf86cd799439014",
                "price": 0.50,
                "status": "pending",
                "ip_address": "192.168.1.1",
                "verification_code": "123456"
            }
        }

    @validator('verification_code')
    def validate_verification_code(cls, v):
        if v and not v.isdigit():
            raise ValueError('Verification code must contain only digits')
        return v

class Order:
    collection = db['orders']

    @staticmethod
    def create_order(order_data: dict) -> str:
        """Create a new order"""
        order_data['created_at'] = datetime.now()
        order_data['updated_at'] = datetime.now()
        result = Order.collection.insert_one(order_data)
        return str(result.inserted_id)

    @staticmethod
    def get_order_by_id(order_id: str) -> Optional[dict]:
        """Get order by ID"""
        return Order.collection.find_one({'_id': ObjectId(order_id)})

    @staticmethod
    def update_order_status(order_id: str, status: OrderStatus) -> bool:
        """Update order status"""
        updates = {
            'status': status.value,
            'updated_at': datetime.now()
        }

        if status == OrderStatus.COMPLETED:
            updates['end_time'] = datetime.now()

        result = Order.collection.update_one(
            {'_id': ObjectId(order_id)},
            {'$set': updates}
        )
        return result.modified_count > 0

    @staticmethod
    def set_verification_code(order_id: str, code: str) -> bool:
        """Set verification code for an order"""
        result = Order.collection.update_one(
            {'_id': ObjectId(order_id)},
            {
                '$set': {
                    'verification_code': code,
                    'updated_at': datetime.now()
                }
            }
        )
        return result.modified_count > 0

    @staticmethod
    def get_active_orders_by_user(user_id: str) -> List[dict]:
        """Get all active orders for a user"""
        return list(Order.collection.find({
            'user_id': ObjectId(user_id),
            'status': {'$in': [OrderStatus.PENDING.value, OrderStatus.ACTIVE.value]}
        }))

    @staticmethod
    def get_completed_orders_by_service(service_id: str, limit: int = 100) -> List[dict]:
        """Get completed orders for a service"""
        return list(Order.collection.find({
            'service_id': ObjectId(service_id),
            'status': OrderStatus.COMPLETED.value
        }).sort('end_time', -1).limit(limit))

    @staticmethod
    def get_orders_by_phone_number(phone_number_id: str) -> List[dict]:
        """Get all orders for a phone number"""
        return list(Order.collection.find({
            'phone_number_id': ObjectId(phone_number_id)
        }).sort('start_time', -1))

    @staticmethod
    def expire_pending_orders(hours: int = 1) -> int:
        """Mark pending orders older than X hours as failed"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        result = Order.collection.update_many(
            {
                'status': OrderStatus.PENDING.value,
                'created_at': {'$lt': cutoff_time}
            },
            {
                '$set': {
                    'status': OrderStatus.FAILED.value,
                    'updated_at': datetime.now(),
                    'end_time': datetime.now()
                }
            }
        )
        return result.modified_count