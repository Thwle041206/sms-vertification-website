'''
Giải thích các thành phần chính:

ServiceSchema (Pydantic Model):

Định nghĩa cấu trúc dữ liệu service với tất cả các trường yêu cầu
Validation cho các trường quan trọng:

Giá cả phải lớn hơn 0
current_price không được nhỏ hơn base_price
success_rate trong khoảng 0-1
Giá trị mặc định hợp lý cho các trường
Service Class (MongoDB Operations):

create_service: Tạo service mới
get_service_by_id: Lấy thông tin service bằng ID
get_popular_services: Lấy các service phổ biến nhất
get_services_by_country: Lấy các service có sẵn tại country cụ thể
update_service_prices: Cập nhật giá cả (kiểm tra base_price)
add_country_to_service: Thêm country vào danh sách available_countries
remove_country_from_service: Xóa country khỏi danh sách available_countries
update_success_rate: Cập nhật tỷ lệ thành công (thống kê)
increment_popularity: Tăng độ phổ biến của service
Cách sử dụng cơ bản:

# Tạo service mới
service_data = {
    "name": "WhatsApp",
    "icon": "https://example.com/icons/whatsapp.png",
    "base_price": 0.15,
    "current_price": 0.20,
    "available_countries": ["507f1f77bcf86cd799439011"],
    "is_free_allowed": True,
    "free_daily_limit": 3
}
service_id = Service.create_service(service_data)

# Lấy service phổ biến
popular_services = Service.get_popular_services()

# Cập nhật giá
Service.update_service_prices(service_id, 0.25)

# Thêm country vào service
Service.add_country_to_service(service_id, "507f1f77bcf86cd799439012")
'''
from typing import Optional, Dict, Any, List
from bson import ObjectId
from pydantic import BaseModel, Field, validator
from app.config.database import db
from datetime import datetime

class ServiceSchema(BaseModel):
    id: Optional[str] = Field(None, alias='_id')
    name: str = Field(..., min_length=2, max_length=50)
    icon: str = Field(..., description="URL to service icon image")
    base_price: float = Field(..., gt=0, description="Base price in USD")
    current_price: float = Field(..., gt=0, description="Current price in USD")
    available_countries: List[str] = Field(default_factory=list)
    success_rate: float = Field(default=0.0, ge=0, le=1)
    popularity: float = Field(default=0.0, ge=0)
    is_free_allowed: bool = Field(default=False)
    free_daily_limit: int = Field(default=0, ge=0)
    last_updated: datetime = Field(default_factory=datetime.now)

    class Config:
        json_encoders = {
            ObjectId: str,
            datetime: lambda dt: dt.isoformat()
        }
        json_schema_extra = {
            "example": {
                "name": "Telegram",
                "icon": "https://example.com/icons/telegram.png",
                "base_price": 0.10,
                "current_price": 0.15,
                "available_countries": ["507f1f77bcf86cd799439011"],
                "success_rate": 0.95,
                "popularity": 4.5,
                "is_free_allowed": True,
                "free_daily_limit": 2
            }
        }

    @validator('current_price')
    def current_price_not_less_than_base(cls, v, values):
        if 'base_price' in values and v < values['base_price']:
            raise ValueError('Current price cannot be less than base price')
        return v

class Service:
    collection = db['services']

    @staticmethod
    def create_service(service_data: dict) -> str:
        """Create a new service"""
        result = Service.collection.insert_one(service_data)
        return str(result.inserted_id)

    @staticmethod
    def get_service_by_id(service_id: str) -> Optional[dict]:
        """Get service by ID"""
        return Service.collection.find_one({'_id': ObjectId(service_id)})

    @staticmethod
    def get_popular_services(limit: int = 5) -> List[dict]:
        """Get most popular services"""
        return list(Service.collection.find()
                     .sort('popularity', -1)
                     .limit(limit))

    @staticmethod
    def get_services_by_country(country_id: str) -> List[dict]:
        """Get services available in a specific country"""
        return list(Service.collection.find({
            'available_countries': ObjectId(country_id)
        }))

    @staticmethod
    def update_service_prices(service_id: str, new_price: float) -> bool:
        """Update service prices (both current and base if current is lower)"""
        service = Service.collection.find_one({'_id': ObjectId(service_id)})
        if not service:
            return False

        updates = {
            'current_price': new_price,
            'last_updated': datetime.now()
        }

        if new_price < service['base_price']:
            updates['base_price'] = new_price

        result = Service.collection.update_one(
            {'_id': ObjectId(service_id)},
            {'$set': updates}
        )
        return result.modified_count > 0

    @staticmethod
    def add_country_to_service(service_id: str, country_id: str) -> bool:
        """Add a country to service's available countries"""
        result = Service.collection.update_one(
            {'_id': ObjectId(service_id)},
            {'$addToSet': {'available_countries': ObjectId(country_id)}}
        )
        return result.modified_count > 0

    @staticmethod
    def remove_country_from_service(service_id: str, country_id: str) -> bool:
        """Remove a country from service's available countries"""
        result = Service.collection.update_one(
            {'_id': ObjectId(service_id)},
            {'$pull': {'available_countries': ObjectId(country_id)}}
        )
        return result.modified_count > 0

    @staticmethod
    def update_success_rate(service_id: str, success: bool) -> bool:
        """Update service success rate (call when a service is used)"""
        # This would typically be more sophisticated in production
        # with proper statistical calculations
        service = Service.get_service_by_id(service_id)
        if not service:
            return False

        new_success_rate = ((service['success_rate'] * 100) + (1 if success else 0)) / 101

        result = Service.collection.update_one(
            {'_id': ObjectId(service_id)},
            {'$set': {'success_rate': new_success_rate}}
        )
        return result.modified_count > 0

    @staticmethod
    def increment_popularity(service_id: str, increment: float = 0.1) -> bool:
        """Increase service popularity"""
        result = Service.collection.update_one(
            {'_id': ObjectId(service_id)},
            {'$inc': {'popularity': increment}}
        )
        return result.modified_count > 0