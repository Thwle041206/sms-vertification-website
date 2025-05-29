from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Đổi tên biến để tránh xung đột
    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db_name: str = "sms_verification_db"
    
    class Config:
        env_file = ".env"
        # Thêm cấu hình này để cho phép thêm trường từ .env
        extra = "allow"

settings = Settings()