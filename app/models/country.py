'''
Giải thích các thành phần chính:

CountrySchema (Pydantic Model):

Định nghĩa cấu trúc dữ liệu country với tất cả các trường yêu cầu
Validation cho các trường:

code: 2-3 ký tự in hoa (regex)
phone_code: bắt đầu bằng + hoặc số
name: độ dài 2-100 ký tự
Giá trị mặc định: is_active=True, available_services=[]
Country Class (MongoDB Operations):

create_country: Tạo country mới
get_country_by_id: Lấy thông tin country bằng ID
get_active_countries: Lấy danh sách các country đang active
get_countries_by_service: Lấy các country có hỗ trợ service cụ thể
update_country_status: Kích hoạt/vô hiệu hóa country
add_service_to_country: Thêm service vào danh sách available services
remove_service_from_country: Xóa service khỏi danh sách available services
search_countries: Tìm kiếm country theo tên hoặc code
Cách sử dụng cơ bản:

# Tạo country mới
country_data = {
    "name": "Vietnam",
    "code": "VN",
    "flag_icon": "https://example.com/flags/vn.svg",
    "phone_code": "+84",
    "available_services": ["507f1f77bcf86cd799439011"]
}
country_id = Country.create_country(country_data)

# Lấy danh sách country active
active_countries = Country.get_active_countries()

# Thêm service vào country
Country.add_service_to_country(country_id, "507f1f77bcf86cd799439011")

# Tìm kiếm country
search_results = Country.search_countries("Viet")
'''

from typing import List, Optional
from bson import ObjectId
from pydantic import BaseModel, Field, validator
from enum import Enum
from app.config.database import db

class CountrySchema(BaseModel):
    id: Optional[str] = Field(None, alias='_id')
    name: str = Field(..., min_length=2, max_length=100)
    code: str = Field(..., min_length=2, max_length=5, pattern='^[A-Z]{2,3}$')
    flag_icon: str = Field(..., description="URL to flag icon image")
    is_active: bool = Field(default=True)
    phone_code: str = Field(..., min_length=1, max_length=5, pattern='^\+?\d+$')
    available_services: List[str] = Field(default_factory=list)

    class Config:
        json_encoders = {
            ObjectId: str
        }
        json_schema_extra = {
            "example": {
                "name": "United States",
                "code": "US",
                "flag_icon": "https://example.com/flags/us.svg",
                "is_active": True,
                "phone_code": "+1",
                "available_services": ["507f1f77bcf86cd799439011"]
            }
        }

    @validator('code')
    def code_to_uppercase(cls, v):
        return v.upper()

class Country:
    collection = db['countries']

    @staticmethod
    def create_country(country_data: dict) -> str:
        """Create a new country"""
        result = Country.collection.insert_one(country_data)
        return str(result.inserted_id)

    @staticmethod
    def get_country_by_id(country_id: str) -> Optional[dict]:
        """Get country by ID"""
        return Country.collection.find_one({'_id': ObjectId(country_id)})

    @staticmethod
    async def get_active_countries() -> List[dict]:
        """Get all active countries"""
        countries = []
        cursor = Country.collection.find({'is_active': True})
        async for country in cursor:
            countries.append(country)
        return countries

    @staticmethod
    def get_countries_by_service(service_id: str) -> List[dict]:
        """Get countries where a service is available"""
        return list(Country.collection.find({
            'available_services': ObjectId(service_id),
            'is_active': True
        }))

    @staticmethod
    def update_country_status(country_id: str, is_active: bool) -> bool:
        """Activate/deactivate a country"""
        result = Country.collection.update_one(
            {'_id': ObjectId(country_id)},
            {'$set': {'is_active': is_active}}
        )
        return result.modified_count > 0

    @staticmethod
    def add_service_to_country(country_id: str, service_id: str) -> bool:
        """Add a service to country's available services"""
        result = Country.collection.update_one(
            {'_id': ObjectId(country_id)},
            {'$addToSet': {'available_services': ObjectId(service_id)}}
        )
        return result.modified_count > 0

    @staticmethod
    def remove_service_from_country(country_id: str, service_id: str) -> bool:
        """Remove a service from country's available services"""
        result = Country.collection.update_one(
            {'_id': ObjectId(country_id)},
            {'$pull': {'available_services': ObjectId(service_id)}}
        )
        return result.modified_count > 0

    @staticmethod
    def search_countries(query: str, limit: int = 10) -> List[dict]:
        """Search countries by name or code"""
        return list(Country.collection.find({
            '$or': [
                {'name': {'$regex': query, '$options': 'i'}},
                {'code': {'$regex': query, '$options': 'i'}}
            ],
            'is_active': True
        }).limit(limit))