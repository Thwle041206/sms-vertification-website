'''
Key features of this implementation:

BulkDiscount Model:

Defines the structure for bulk discount tiers
Validates minimum quantity and price per unit
PricingSchema:

Validates that current price isn't lower than base price
Ensures bulk discounts are properly ordered and progressive
Automatic last_updated timestamp
Pricing Class Methods:

create_pricing: Creates new pricing entry
get_pricing_by_ids: Gets pricing for specific country-service combo
update_pricing: General update method
update_current_price: Specialized price update
add_bulk_discount: Adds new discount tier
get_price_for_quantity: Calculates best price for given quantity
get_prices_by_service/country: Gets all pricing for service or country
sync_base_prices: Updates base prices across all entries for a service
Example Usage:

# Create pricing entry
pricing_data = {
    "country_id": "507f1f77bcf86cd799439011",
    "service_id": "507f1f77bcf86cd799439012",
    "base_price": 0.10,
    "current_price": 0.15,
    "bulk_discounts": [
        {"min_quantity": 100, "price_per": 0.08},
        {"min_quantity": 500, "price_per": 0.06}
    ]
}
pricing_id = Pricing.create_pricing(pricing_data)

# Get price for quantity
best_price = Pricing.get_price_for_quantity(
    country_id="507f1f77bcf86cd799439011",
    service_id="507f1f77bcf86cd799439012",
    quantity=150
)  # Returns 0.08

# Update current price
Pricing.update_current_price(
    country_id="507f1f77bcf86cd799439011",
    service_id="507f1f77bcf86cd799439012",
    new_price=0.12
)

# Add bulk discount
Pricing.add_bulk_discount(
    country_id="507f1f77bcf86cd799439011",
    service_id="507f1f77bcf86cd799439012",
    discount={"min_quantity": 1000, "price_per": 0.05}
)
'''


from typing import List, Optional, Dict
from bson import ObjectId
from pydantic import BaseModel, Field, validator
from datetime import datetime
from app.config.database import db

class BulkDiscount(BaseModel):
    min_quantity: int = Field(..., gt=0)
    price_per: float = Field(..., gt=0)

    class Config:
        json_schema_extra = {
            "example": {
                "min_quantity": 100,
                "price_per": 0.08
            }
        }

class PricingSchema(BaseModel):
    id: Optional[str] = Field(None, alias='_id')
    country_id: str
    service_id: str
    base_price: float = Field(..., gt=0)
    current_price: float = Field(..., gt=0)
    bulk_discounts: List[BulkDiscount] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.now)

    class Config:
        json_encoders = {
            ObjectId: str,
            datetime: lambda dt: dt.isoformat()
        }
        json_schema_extra = {
            "example": {
                "country_id": "507f1f77bcf86cd799439011",
                "service_id": "507f1f77bcf86cd799439012",
                "base_price": 0.10,
                "current_price": 0.15,
                "bulk_discounts": [
                    {"min_quantity": 100, "price_per": 0.08},
                    {"min_quantity": 500, "price_per": 0.06}
                ]
            }
        }

    @validator('current_price')
    def validate_current_price(cls, v, values):
        if 'base_price' in values and v < values['base_price']:
            raise ValueError('Current price cannot be less than base price')
        return v

    @validator('bulk_discounts')
    def validate_bulk_discounts(cls, v):
        # Ensure discounts are sorted by min_quantity ascending
        v.sort(key=lambda x: x.min_quantity)
        
        # Validate no overlapping quantities and proper discount progression
        for i in range(1, len(v)):
            if v[i].min_quantity <= v[i-1].min_quantity:
                raise ValueError('Bulk discounts must have increasing min_quantity')
            if v[i].price_per >= v[i-1].price_per:
                raise ValueError('Bulk discounts must have decreasing prices')
        return v

class Pricing:
    collection = db['pricing']

    @staticmethod
    def create_pricing(pricing_data: dict) -> str:
        """Create new pricing entry"""
        pricing_data['last_updated'] = datetime.now()
        result = Pricing.collection.insert_one(pricing_data)
        return str(result.inserted_id)

    @staticmethod
    def get_pricing_by_ids(country_id: str, service_id: str) -> Optional[dict]:
        """Get pricing for specific country and service"""
        return Pricing.collection.find_one({
            'country_id': ObjectId(country_id),
            'service_id': ObjectId(service_id)
        })

    @staticmethod
    def update_pricing(pricing_id: str, update_data: dict) -> bool:
        """Update pricing information"""
        update_data['last_updated'] = datetime.now()
        result = Pricing.collection.update_one(
            {'_id': ObjectId(pricing_id)},
            {'$set': update_data}
        )
        return result.modified_count > 0

    @staticmethod
    def update_current_price(country_id: str, service_id: str, new_price: float) -> bool:
        """Update current price for a pricing entry"""
        result = Pricing.collection.update_one(
            {
                'country_id': ObjectId(country_id),
                'service_id': ObjectId(service_id)
            },
            {
                '$set': {
                    'current_price': new_price,
                    'last_updated': datetime.now()
                }
            }
        )
        return result.modified_count > 0

    @staticmethod
    def add_bulk_discount(country_id: str, service_id: str, discount: dict) -> bool:
        """Add a new bulk discount tier"""
        result = Pricing.collection.update_one(
            {
                'country_id': ObjectId(country_id),
                'service_id': ObjectId(service_id)
            },
            {
                '$push': {'bulk_discounts': discount},
                '$set': {'last_updated': datetime.now()}
            }
        )
        return result.modified_count > 0

    @staticmethod
    def get_price_for_quantity(country_id: str, service_id: str, quantity: int) -> Optional[float]:
        """Get the best available price for a given quantity"""
        pricing = Pricing.collection.find_one({
            'country_id': ObjectId(country_id),
            'service_id': ObjectId(service_id)
        })
        
        if not pricing:
            return None
        
        # Check bulk discounts (they should be pre-sorted)
        best_price = pricing['current_price']
        for discount in pricing.get('bulk_discounts', []):
            if quantity >= discount['min_quantity'] and discount['price_per'] < best_price:
                best_price = discount['price_per']
        
        return best_price

    @staticmethod
    def get_prices_by_service(service_id: str) -> List[dict]:
        """Get all pricing entries for a service"""
        return list(Pricing.collection.find({
            'service_id': ObjectId(service_id)
        }))

    @staticmethod
    def get_prices_by_country(country_id: str) -> List[dict]:
        """Get all pricing entries for a country"""
        return list(Pricing.collection.find({
            'country_id': ObjectId(country_id)
        }))

    @staticmethod
    def sync_base_prices(service_id: str, new_base_price: float) -> int:
        """Update base prices for all entries of a service"""
        result = Pricing.collection.update_many(
            {
                'service_id': ObjectId(service_id),
                'base_price': {'$ne': new_base_price}
            },
            {
                '$set': {
                    'base_price': new_base_price,
                    'current_price': {'$max': ['$current_price', new_base_price]},
                    'last_updated': datetime.now()
                }
            }
        )
        return result.modified_count