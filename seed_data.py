import os
from datetime import datetime, timedelta
from bson import ObjectId
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Connect to MongoDB
client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("MONGO_DB_NAME")]

def seed_data():
    print("Starting data seeding...")
    
    # Clear existing collections
    db.users.delete_many({})
    db.countries.delete_many({})
    db.services.delete_many({})
    db.phone_numbers.delete_many({})
    db.orders.delete_many({})
    db.projects.delete_many({})
    db.transactions.delete_many({})
    db.pricing.delete_many({})
    
    # 1. Seed Users
    users = [
        {
            "username": "admin_user",
            "email": "admin@example.com",
            "password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
            "phone": "+1234567890",
            "balance": 1000.00,
            "api_key": "admin_api_key_123",
            "registration_date": datetime.utcnow(),
            "last_login": datetime.utcnow(),
            "status": "active",
            "ip_history": ["192.168.1.1", "10.0.0.1"],
            "verification_level": 3
        },
        {
            "username": "test_user",
            "email": "user@example.com",
            "password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
            "phone": "+9876543210",
            "balance": 500.00,
            "api_key": "user_api_key_456",
            "registration_date": datetime.utcnow(),
            "last_login": datetime.utcnow(),
            "status": "active",
            "ip_history": ["172.16.0.1"],
            "verification_level": 1
        }
    ]
    user_ids = [str(db.users.insert_one(user).inserted_id) for user in users]
    print(f"Inserted {len(user_ids)} users")

    # 2. Seed Countries
    countries = [
        {
            "name": "United States",
            "code": "US",
            "flag_icon": "https://flagcdn.com/us.svg",
            "is_active": True,
            "phone_code": "+1"
        },
        {
            "name": "Vietnam",
            "code": "VN",
            "flag_icon": "https://flagcdn.com/vn.svg",
            "is_active": True,
            "phone_code": "+84"
        },
        {
            "name": "United Kingdom",
            "code": "UK",
            "flag_icon": "https://flagcdn.com/gb.svg",
            "is_active": True,
            "phone_code": "+44"
        },
        {
            "name": "Campuchia",
            "code": "US",
            "flag_icon": "https://flagcdn.com/us.svg",
            "is_active": True,
            "phone_code": "+1"
        },
        {
            "name": "China",
            "code": "VN",
            "flag_icon": "https://flagcdn.com/vn.svg",
            "is_active": True,
            "phone_code": "+84"
        },
        {
            "name": "Korean",
            "code": "UK",
            "flag_icon": "https://flagcdn.com/gb.svg",
            "is_active": True,
            "phone_code": "+44"
        },
        {
            "name": "Russia",
            "code": "UK",
            "flag_icon": "https://flagcdn.com/gb.svg",
            "is_active": True,
            "phone_code": "+44"
        }

    ]
    country_ids = [str(db.countries.insert_one(country).inserted_id) for country in countries]
    print(f"Inserted {len(country_ids)} countries")

    # 3. Seed Services
    services = [
        {
            "name": "Telegram",
            "icon": "https://example.com/icons/telegram.png",
            "base_price": 0.10,
            "current_price": 0.15,
            "success_rate": 0.95,
            "popularity": 4.8,
            "is_free_allowed": True,
            "free_daily_limit": 2
        },
        {
            "name": "WhatsApp",
            "icon": "https://example.com/icons/whatsapp.png",
            "base_price": 0.20,
            "current_price": 0.25,
            "success_rate": 0.90,
            "popularity": 4.5,
            "is_free_allowed": False,
            "free_daily_limit": 0
        },
        {
            "name": "Amazon",
            "icon": "https://example.com/icons/facebook.png",
            "base_price": 0.15,
            "current_price": 0.18,
            "success_rate": 0.85,
            "popularity": 4.2,
            "is_free_allowed": True,
            "free_daily_limit": 1
        },
        {
            "name": "Alibaba",
            "icon": "https://example.com/icons/whatsapp.png",
            "base_price": 0.20,
            "current_price": 0.25,
            "success_rate": 0.90,
            "popularity": 4.5,
            "is_free_allowed": False,
            "free_daily_limit": 0
        },
        {
            "name": "Facebook",
            "icon": "https://example.com/icons/facebook.png",
            "base_price": 0.15,
            "current_price": 0.18,
            "success_rate": 0.85,
            "popularity": 4.2,
            "is_free_allowed": True,
            "free_daily_limit": 1
        },
        {
            "name": "Shoppee",
            "icon": "https://example.com/icons/facebook.png",
            "base_price": 0.15,
            "current_price": 0.18,
            "success_rate": 0.85,
            "popularity": 4.2,
            "is_free_allowed": True,
            "free_daily_limit": 1
        }
    ]
    service_ids = [str(db.services.insert_one(service).inserted_id) for service in services]
    print(f"Inserted {len(service_ids)} services")

    # Update countries with available services
    db.countries.update_many(
        {},
        {"$set": {"available_services": [ObjectId(service_ids[0]), ObjectId(service_ids[1])]}}
    )

    # 4. Seed Phone Numbers
    phone_numbers = [
        {
            "number": "+1234567890",
            "country_id": ObjectId(country_ids[0]),
            "service_id": ObjectId(service_ids[0]),
            "provider": "Twilio",
            "is_active": True,
            "is_used": False,
            "current_user": None,
            "expiration_time": datetime.utcnow() + timedelta(days=30),
            "last_used": None
        },
        {
            "number": "+84987654321",
            "country_id": ObjectId(country_ids[1]),
            "service_id": ObjectId(service_ids[1]),
            "provider": "Vonage",
            "is_active": True,
            "is_used": True,
            "current_user": ObjectId(user_ids[0]),
            "expiration_time": datetime.utcnow() + timedelta(days=15),
            "last_used": datetime.utcnow()
        },
        {
            "number": "+447987654321",
            "country_id": ObjectId(country_ids[2]),
            "service_id": ObjectId(service_ids[2]),
            "provider": "Plivo",
            "is_active": True,
            "is_used": False,
            "current_user": None,
            "expiration_time": datetime.utcnow() + timedelta(days=60),
            "last_used": None,
            "sms_received": [{
                "content": "Your verification code is 123456",
                "timestamp": datetime.utcnow(),
                "from": "+123456789"
            }]
        }
    ]
    phone_number_ids = [str(db.phone_numbers.insert_one(num).inserted_id) for num in phone_numbers]
    print(f"Inserted {len(phone_number_ids)} phone numbers")

    # 5. Seed Orders
    orders = [
        {
            "user_id": ObjectId(user_ids[0]),
            "service_id": ObjectId(service_ids[0]),
            "country_id": ObjectId(country_ids[0]),
            "phone_number_id": ObjectId(phone_number_ids[0]),
            "price": 0.15,
            "status": "completed",
            "start_time": datetime.utcnow() - timedelta(hours=2),
            "end_time": datetime.utcnow() - timedelta(hours=1),
            "verification_code": "123456",
            "ip_address": "192.168.1.100"
        },
        {
            "user_id": ObjectId(user_ids[1]),
            "service_id": ObjectId(service_ids[1]),
            "country_id": ObjectId(country_ids[1]),
            "phone_number_id": ObjectId(phone_number_ids[1]),
            "price": 0.25,
            "status": "active",
            "start_time": datetime.utcnow() - timedelta(minutes=30),
            "end_time": None,
            "verification_code": "654321",
            "ip_address": "10.0.0.100"
        }
    ]
    order_ids = [str(db.orders.insert_one(order).inserted_id) for order in orders]
    print(f"Inserted {len(order_ids)} orders")

    # 6. Seed Projects
    projects = [
        {
            "user_id": ObjectId(user_ids[0]),
            "name": "Marketing Campaign",
            "description": "Project for marketing team verification needs",
            "default_country": ObjectId(country_ids[0]),
            "default_service": ObjectId(service_ids[0]),
            "area_code": "800",
            "created_at": datetime.utcnow(),
            "api_calls": 42
        },
        {
            "user_id": ObjectId(user_ids[1]),
            "name": "User Verification",
            "description": "Project for user account verification",
            "default_country": ObjectId(country_ids[1]),
            "default_service": ObjectId(service_ids[1]),
            "area_code": None,
            "created_at": datetime.utcnow(),
            "api_calls": 15
        }
    ]
    project_ids = [str(db.projects.insert_one(project).inserted_id) for project in projects]
    print(f"Inserted {len(project_ids)} projects")

    # 7. Seed Transactions
    transactions = [
        {
            "user_id": ObjectId(user_ids[0]),
            "amount": 100.00,
            "type": "deposit",
            "status": "completed",
            "payment_method": "credit_card",
            "payment_details": {
                "card_last4": "4242",
                "processor": "stripe"
            },
            "timestamp": datetime.utcnow() - timedelta(days=3),
            "order_id": None
        },
        {
            "user_id": ObjectId(user_ids[0]),
            "amount": 0.15,
            "type": "purchase",
            "status": "completed",
            "payment_method": "account_balance",
            "payment_details": {},
            "timestamp": datetime.utcnow() - timedelta(hours=2),
            "order_id": ObjectId(order_ids[0])
        },
        {
            "user_id": ObjectId(user_ids[1]),
            "amount": 50.00,
            "type": "deposit",
            "status": "completed",
            "payment_method": "paypal",
            "payment_details": {
                "transaction_id": "PAYPAL12345"
            },
            "timestamp": datetime.utcnow() - timedelta(days=1),
            "order_id": None
        }
    ]
    transaction_ids = [str(db.transactions.insert_one(tx).inserted_id) for tx in transactions]
    print(f"Inserted {len(transaction_ids)} transactions")

    # 8. Seed Pricing
    pricing = [
        {
            "country_id": ObjectId(country_ids[0]),
            "service_id": ObjectId(service_ids[0]),
            "base_price": 0.10,
            "current_price": 0.15,
            "bulk_discounts": [
                {"min_quantity": 100, "price_per": 0.08},
                {"min_quantity": 500, "price_per": 0.06}
            ],
            "last_updated": datetime.utcnow()
        },
        {
            "country_id": ObjectId(country_ids[1]),
            "service_id": ObjectId(service_ids[1]),
            "base_price": 0.20,
            "current_price": 0.25,
            "bulk_discounts": [
                {"min_quantity": 50, "price_per": 0.18},
                {"min_quantity": 200, "price_per": 0.15}
            ],
            "last_updated": datetime.utcnow()
        }
    ]
    pricing_ids = [str(db.pricing.insert_one(price).inserted_id) for price in pricing]
    print(f"Inserted {len(pricing_ids)} pricing entries")

    print("Data seeding completed successfully!")
    print("\nSample IDs for testing:")
    print(f"User IDs: {user_ids}")
    print(f"Country IDs: {country_ids}")
    print(f"Service IDs: {service_ids}")
    print(f"Phone Number IDs: {phone_number_ids}")
    print(f"Order IDs: {order_ids}")
    print(f"Project IDs: {project_ids}")
    print(f"Transaction IDs: {transaction_ids}")
    print(f"Pricing IDs: {pricing_ids}")

if __name__ == "__main__":
    seed_data()