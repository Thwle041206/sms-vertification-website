from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from datetime import datetime
import httpx
import asyncio
from typing import Optional
import aiomysql
import uvicorn
import logging
from functools import wraps
from motor.motor_asyncio import AsyncIOMotorClient
from app.models.phone_number import PhoneNumber


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app initialization
app = FastAPI()


# Configuration
class Settings:
    API_BASE_URL = "http://www.jisu366.com/jk"
    API_KEY = "TSClw5LXhp"
    DB_HOST = "208.110.95.234"
    DB_USER = "smscode"
    DB_PASSWORD = "K63xNNy53KLprMz2"
    DB_NAME = "smscode"
    DB_POOL_SIZE = 20
    HTTP_TIMEOUT = 30
    HTTP_RETRIES = 3
    HTTP_POOL_SIZE = 100
    MONGO_URI = "mongodb://localhost:27017"
    MONGO_DB_NAME = "sms_verification_db"


settings = Settings()

# Database pool configuration
db_pool = None

# MongoDB client and database
mongo_client = AsyncIOMotorClient(settings.MONGO_URI)
mongo_db = mongo_client[settings.MONGO_DB_NAME]

# Inject mongo_db into PhoneNumber class
PhoneNumber.collection = mongo_db['phone_numbers']

async def init_db_pool():
    global db_pool
    try:
        db_pool = await aiomysql.create_pool(
            host=settings.DB_HOST,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            db=settings.DB_NAME,
            maxsize=settings.DB_POOL_SIZE,
            autocommit=True,
            cursorclass=aiomysql.cursors.DictCursor
        )
        logger.info("Database pool initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database pool: {str(e)}")
        raise


# HTTP client pool
http_client = httpx.AsyncClient(
    timeout=settings.HTTP_TIMEOUT,
    limits=httpx.Limits(
        max_keepalive_connections=settings.HTTP_POOL_SIZE,
        max_connections=settings.HTTP_POOL_SIZE
    )
)


# Custom exception for API timeouts
class APITimeoutError(Exception):
    pass


# API operations class with modified call_api method
class APIOperations:
    @staticmethod
    async def verify_token(token: str) -> dict:
        try:
            logger.info(f"Verifying token: {token}")
            async with db_pool.acquire() as conn:
                async with conn.cursor() as cur:
                    query = "SELECT * FROM user WHERE token = %s AND status = 1"
                    await cur.execute(query, (token,))
                    result = await cur.fetchone()
                    if not result:
                        logger.error(f"No user found for token: {token}")
                        raise HTTPException(status_code=401, detail="Invalid token")
                    return result
        except Exception as e:
            logger.error(f"Error in verify_token: {str(e)}")
            raise HTTPException(status_code=401, detail="Invalid token")
    @staticmethod
    async def get_number_result(data: dict):
        return {
            "errno": 0,
            "errmsg": "ok",
            "qhid": data["ret"]["qhid"],
            "quhao": data["ret"]["quhao"],
            "number": data["ret"]["number"]
        }
    @staticmethod
    async def get_new_number(quhao: str,number:str = None) -> dict:
        """Get new number from third-party API"""
        # 构造固定格式的URL
        url = f"{settings.API_BASE_URL}/getnumber"
        params = {
            "apikey": settings.API_KEY,
            "pid": "103",
            "quhao": quhao,
            "number": number
        }

        try:
            logger.info(f"Making request to: {url} with params: {params}")
            for attempt in range(settings.HTTP_RETRIES):
                try:
                    response = await http_client.get(url, params=params)
                    logger.info(f"Actual request URL: {response.url}")
                    response.raise_for_status()
                    return response.json()
                except asyncio.TimeoutError:
                    if attempt == settings.HTTP_RETRIES - 1:
                        raise HTTPException(status_code=504, detail="API request timed out")
                    await asyncio.sleep(1)
                except Exception as e:
                    if attempt == settings.HTTP_RETRIES - 1:
                        raise HTTPException(status_code=500, detail=str(e))
                    logger.error(f"API call attempt {attempt + 1} failed: {str(e)}")
                    await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"Error calling API: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))


    @staticmethod
    async def get_code(qid: str) -> dict:
        url = f"{settings.API_BASE_URL}/getcode"
        params = {
            "apikey": settings.API_KEY,
            "qhid": qid
        }
        try:
            logger.info(f"Making request to: {url} with params: {params}")
            for attempt in range(settings.HTTP_RETRIES):
                try:
                    response = await http_client.get(url, params=params)
                    logger.info(f"Actual request URL: {response.url}")
                    response.raise_for_status()
                    return response.json()
                except asyncio.TimeoutError:
                    if attempt == settings.HTTP_RETRIES - 1:
                        raise HTTPException(status_code=504, detail="API request timed out")
                    await asyncio.sleep(1)
                except Exception as e:
                    if attempt == settings.HTTP_RETRIES - 1:
                        raise HTTPException(status_code=500, detail=str(e))
                    logger.error(f"API call attempt {attempt + 1} failed: {str(e)}")
                    await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"Error calling API: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    @staticmethod
    async def release_number(qid: str) -> dict:
        url = f"{settings.API_BASE_URL}/shifang"
        params = {
            "apikey": settings.API_KEY,
            "qhid": qid
        }
        try:
            logger.info(f"Making request to: {url} with params: {params}")
            for attempt in range(settings.HTTP_RETRIES):
                try:
                    response = await http_client.get(url, params=params)
                    logger.info(f"Actual request URL: {response.url}")
                    response.raise_for_status()
                    return response.json()
                except asyncio.TimeoutError:
                    if attempt == settings.HTTP_RETRIES - 1:
                        raise HTTPException(status_code=504, detail="API request timed out")
                    await asyncio.sleep(1)
                except Exception as e:
                    if attempt == settings.HTTP_RETRIES - 1:
                        raise HTTPException(status_code=500, detail=str(e))
                    logger.error(f"API call attempt {attempt + 1} failed: {str(e)}")
                    await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"Error calling API: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
@app.get("/api/get_number")
async def get_number(
        token: str,
        quhao: str,
        number: Optional[str] = None,
        background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    获取号码的GET接口
    必填参数:
        - token: 用户token
        - quhao: 区号，如 855
        -number:你要获取的特定的手机号，例如你想获取之前使用过的某一个号码，选填
    """
    try:
        logger.info(f"Received get_number request - token: {token}, quhao: {quhao}")

        # Verify token and check balance
        user = await APIOperations.verify_token(token)
        logger.info(f"Token verified successfully for user: {user.get('username')}")

        # Check if the user has sufficient balance
        user_balance = float(user["balance"])
        required_charge = 0.01

        if user_balance < required_charge:
            logger.error(f"Insufficient balance for user: {user['username']}")
            raise HTTPException(status_code=403, detail="Insufficient balance to request a new number")

        # Get new number
        data = await APIOperations.get_new_number(quhao, number)

        if not isinstance(data, dict) or "errno" not in data:
            logger.error(f"Unexpected API response format: {data}")
            raise HTTPException(status_code=500, detail="Invalid API response format")

        if data["errno"] != 0:
            logger.error(f"Third-party API error: {data}")
            raise HTTPException(status_code=400, detail=data["errmsg"])

        # Insert order record asynchronously
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        order_data = {
            "qid": data["ret"]["qhid"],
            "service": "103",  # Fixed service ID
            "number": data["ret"]["number"],
            "time": current_time,
            "apikey": user["apikey"],
            "charge": required_charge,
            "fetchtime": "1",
            "servicename": "google"
        }
        logger.info(f"Inserting order record: {order_data}")

        background_tasks.add_task(
            DatabaseOperations.execute_update,
            """
            INSERT INTO orders (qid, service, number, time, apikey, charge, fetchtime, servicename)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                order_data["qid"],
                order_data["service"],
                order_data["number"],
                order_data["time"],
                order_data["apikey"],
                order_data["charge"],
                order_data["fetchtime"],
                order_data["servicename"]
            )
        )

        # Save phone number to MongoDB if not exists
        phone_number = data["ret"]["number"]
        country_id = "some_country_id"  # You may need to map or get this value properly
        service_id = "some_service_id"  # You may need to map or get this value properly
        provider = "jisu366"  # Example provider name

        existing_phone = await PhoneNumber.collection.find_one({"number": phone_number})
        if not existing_phone:
            phone_data = {
                "number": phone_number,
                "country_id": country_id,
                "service_id": service_id,
                "provider": provider,
                "status": "active",
                "is_used": False,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            await PhoneNumber.collection.insert_one(phone_data)
            logger.info(f"Saved new phone number to MongoDB: {phone_number}")

        data = await APIOperations.get_number_result(data)
        return data

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error in get_number: {str(e)}")
        logger.exception("Detailed traceback:")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")



@app.get("/api/test_token")
async def test_token(token: str):
    """
    测试token是否有效,返回余额
    """
    try:
        user = await APIOperations.verify_token(token)
        return {
            "status": "success",
            "message": "Token is valid",
            "user_info": {
                "username": user["username"],
                "apikey": user["apikey"],
                "balance": float(user["balance"])
            }
        }
    except Exception as e:
        logger.error(f"Token test failed: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }

@app.get("/api/get_code")
async def get_code(
        qhid: int,
        token: str,
        background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    获取验证码的GET接口
    参数:
        - qhid: 订单ID
        - token: 用户token
    """
    try:
        # Verify token
        user = await APIOperations.verify_token(token)
        logger.info(f"Token verified for user: {user.get('username')}, requesting code for qhid: {qhid}")

        # Call API with retry and timeout
        data = await APIOperations.get_code( qhid)

        if not isinstance(data, dict) or "errno" not in data:
            logger.error(f"Unexpected API response format: {data}")
            raise HTTPException(status_code=500, detail="Invalid API response format")

        if data["errno"] != 0:
            logger.error(f"Third-party API error: {data}")
            raise HTTPException(status_code=400, detail=data["errmsg"])

        # Update order and user balance asynchronously
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        background_tasks.add_task(
            DatabaseOperations.execute_update,
            """
            UPDATE orders 
            SET smscode = %s, fetchtime = %s 
            WHERE qid = %s
            """,
            (
                data["ret"]["cnt"],
                current_time,
                qhid
            )
        )

        background_tasks.add_task(
            DatabaseOperations.execute_update,
            "UPDATE user SET balance = balance - 0.01 WHERE id = %s",
            (user['id'],)
        )

        return data

    except APITimeoutError:
        raise HTTPException(status_code=504, detail="API request timed out")
    except Exception as e:
        logger.error(f"Error in get_code: {str(e)}")
        logger.exception("Detailed traceback:")
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/api/release_number")
async def release_number(qhid: int, token: str):
    """
    释放号码的GET接口
    参数通过查询字符串传递：/api/release_number?token=xxx&qhid=12
    """
    try:
        # Verify token
        await APIOperations.verify_token(token)

        # Call API with retry and timeout
        data = await APIOperations.release_number(qhid)
        return data

    except APITimeoutError:
        raise HTTPException(status_code=504, detail="API request timed out")
    except Exception as e:
        logger.error(f"Error in release_number: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")



# Database operations class
class DatabaseOperations:
    @staticmethod
    async def execute_query(query, params=None):
        async with db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, params or ())
                return await cur.fetchall()

    @staticmethod
    async def execute_update(query, params=None):
        async with db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, params or ())
                await conn.commit()


# Startup and shutdown events
@app.on_event("startup")
async def startup():
    await init_db_pool()
    logger.info("Application started, database pool initialized")


@app.on_event("shutdown")
async def shutdown():
    global db_pool, http_client
    if db_pool:
        db_pool.close()
        await db_pool.wait_closed()
    await http_client.aclose()
    logger.info("Application shutdown, connections closed")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)


