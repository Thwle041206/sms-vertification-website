from fastapi import APIRouter, Request, Form, status, Response, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from app.models.service import Service
from app.models.country import Country
from app.models.project import Project
from typing import List
from app.core.security import hash_password, create_access_token
from app.models.user import User
import secrets
import os
import hashlib
import hmac
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config

router = APIRouter()
templates = Jinja2Templates(directory="app/views")

# Cấu hình OAuth
config = Config('.env')
oauth = OAuth(config)

oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)

oauth.register(
    name='discord',
    client_id=os.getenv('DISCORD_CLIENT_ID'),
    client_secret=os.getenv('DISCORD_CLIENT_SECRET'),
    authorize_url='https://discord.com/api/oauth2/authorize',
    authorize_params=None,
    access_token_url='https://discord.com/api/oauth2/token',
    access_token_params=None,
    refresh_token_url=None,
    client_kwargs={'scope': 'identify email'},
)

oauth.register(
    name='twitter',
    client_id=os.getenv('TWITTER_CLIENT_ID'),
    client_secret=os.getenv('TWITTER_CLIENT_SECRET'),
    authorize_url='https://twitter.com/i/oauth2/authorize',
    access_token_url='https://api.twitter.com/2/oauth2/token',
    client_kwargs={'scope': 'users.read tweet.read'},
)

@router.get("/", include_in_schema=False)
@router.get("/homepage")
async def homepage(request: Request):
    try:
        # Verify database connection
        from app.config.database import db
        await db.client.admin.command('ping')
        
        # Get services with error handling for missing fields
        services = []
        cursor = Service.collection.find().sort("popularity", -1).limit(20)
        async for service in cursor:
            # Ensure required fields exist
            service.setdefault("name", "Unknown Service")
            service.setdefault("popularity", 0)
            service.setdefault("current_price", 0)
            service.setdefault("success_rate", 0.9)
            services.append(service)

        # Get active countries asynchronously
        countries = await Country.get_active_countries()

        # Hardcoded user_id for demonstration
        from bson import ObjectId
        user_id = ObjectId("507f1f77bcf86cd799439011")
        user_projects = await Project.get_user_projects(user_id)
        selected_project_name = "My Verification Project"
        if user_projects:
            selected_project_name = user_projects[0].name
        
        return templates.TemplateResponse(
            "user/account/homepage.html",
            {
                "request": request,
                "services": services,
                "total_services": len(services),
                "countries": countries,
                "total_countries": len(countries),
                "selected_project_name": selected_project_name
            }
        )
    except Exception as e:
        import traceback
        error_detail = {
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": error_detail}
        )
@router.get("/view_profile")
async def view_profile(request: Request):
    try:
        # Verify database connection app\views\user\account\view_profile.html
        from app.config.database import db
        await db.client.admin.command('ping')
        
        # Get services with error handling for missing fields
        services = []
        cursor = Service.collection.find().sort("popularity", -1).limit(20)
        async for service in cursor:
            # Ensure required fields exist
            service.setdefault("name", "Unknown Service")
            service.setdefault("popularity", 0)
            service.setdefault("current_price", 0)
            service.setdefault("success_rate", 0.9)
            services.append(service)

        # Get active countries asynchronously
        countries = await Country.get_active_countries()

        # Hardcoded user_id for demonstration
        from bson import ObjectId
        user_id = ObjectId("507f1f77bcf86cd799439011")
        user_projects = await Project.get_user_projects(user_id)
        selected_project_name = "My Verification Project"
        if user_projects:
            selected_project_name = user_projects[0].name
        
        return templates.TemplateResponse(
            "user/account/view_profile.html",
            {
                "request": request,
                "services": services,
                "total_services": len(services),
                "countries": countries,
                "total_countries": len(countries),
                "selected_project_name": selected_project_name
            }
        )
    except Exception as e:
        import traceback
        error_detail = {
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": error_detail}
        )
@router.get("/edit_profile")
async def edit_profile(request: Request):
    try:
        # Verify database connection app\views\user\account\edit_profile.html
        from app.config.database import db
        await db.client.admin.command('ping')
        
        # Get services with error handling for missing fields
        services = []
        cursor = Service.collection.find().sort("popularity", -1).limit(20)
        async for service in cursor:
            # Ensure required fields exist
            service.setdefault("name", "Unknown Service")
            service.setdefault("popularity", 0)
            service.setdefault("current_price", 0)
            service.setdefault("success_rate", 0.9)
            services.append(service)

        # Get active countries asynchronously
        countries = await Country.get_active_countries()

        # Hardcoded user_id for demonstration
        from bson import ObjectId
        user_id = ObjectId("507f1f77bcf86cd799439011")
        user_projects = await Project.get_user_projects(user_id)
        selected_project_name = "My Verification Project"
        if user_projects:
            selected_project_name = user_projects[0].name
        
        return templates.TemplateResponse(
            "user/account/edit_profile.html",
            {
                "request": request,
                "services": services,
                "total_services": len(services),
                "countries": countries,
                "total_countries": len(countries),
                "selected_project_name": selected_project_name
            }
        )
    except Exception as e:
        import traceback
        error_detail = {
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": error_detail}
        )

@router.get("/faq")
async def faq_page(request: Request):
    """FAQ page route"""
    try:
        # Verify database connection
        from app.config.database import db
        await db.client.admin.command('ping')
        
        # Get services with error handling for missing fields
        services = []
        cursor = Service.collection.find().sort("popularity", -1).limit(20)
        async for service in cursor:
            # Ensure required fields exist
            service.setdefault("name", "Unknown Service")
            service.setdefault("popularity", 0)
            service.setdefault("current_price", 0)
            service.setdefault("success_rate", 0.9)
            services.append(service)

        # Get active countries asynchronously
        countries = await Country.get_active_countries()

        # Hardcoded user_id for demonstration
        from bson import ObjectId
        user_id = ObjectId("507f1f77bcf86cd799439011")
        user_projects = await Project.get_user_projects(user_id)
        selected_project_name = "My Verification Project"
        if user_projects:
            selected_project_name = user_projects[0].name
        
        return templates.TemplateResponse(
            "user/support/faq.html",
            {
                "request": request,
                "services": services,
                "total_services": len(services),
                "countries": countries,
                "total_countries": len(countries),
                "selected_project_name": selected_project_name
            }
        )
    except Exception as e:
        import traceback
        error_detail = {
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": error_detail}
        )


@router.get("/faq_sub_category")
async def faq_sub_category(request: Request):

    try:
        # Verify database connection
        from app.config.database import db
        await db.client.admin.command('ping')
        
        # Get services with error handling for missing fields
        services = []
        cursor = Service.collection.find().sort("popularity", -1).limit(20)
        async for service in cursor:
            # Ensure required fields exist
            service.setdefault("name", "Unknown Service")
            service.setdefault("popularity", 0)
            service.setdefault("current_price", 0)
            service.setdefault("success_rate", 0.9)
            services.append(service)

        # Get active countries asynchronously
        countries = await Country.get_active_countries()

        # Hardcoded user_id for demonstration
        from bson import ObjectId
        user_id = ObjectId("507f1f77bcf86cd799439011")
        user_projects = await Project.get_user_projects(user_id)
        selected_project_name = "My Verification Project"
        if user_projects:
            selected_project_name = user_projects[0].name
        
        return templates.TemplateResponse(
            "user/support/faq_sub_category.html",
            {
                "request": request,
                "services": services,
                "total_services": len(services),
                "countries": countries,
                "total_countries": len(countries),
                "selected_project_name": selected_project_name
            }
        )
    except Exception as e:
        import traceback
        error_detail = {
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": error_detail}
        )

         
@router.get("/how_to_use")
async def faq_page(request: Request):
    """how_to_use page route"""
    try:
        # Verify database connection
        from app.config.database import db
        await db.client.admin.command('ping')
        
        # Get services with error handling for missing fields
        services = []
        cursor = Service.collection.find().sort("popularity", -1).limit(20)
        async for service in cursor:
            # Ensure required fields exist
            service.setdefault("name", "Unknown Service")
            service.setdefault("popularity", 0)
            service.setdefault("current_price", 0)
            service.setdefault("success_rate", 0.9)
            services.append(service)

        # Get active countries asynchronously
        countries = await Country.get_active_countries()

        # Hardcoded user_id for demonstration
        from bson import ObjectId
        user_id = ObjectId("507f1f77bcf86cd799439011")
        user_projects = await Project.get_user_projects(user_id)
        selected_project_name = "My Verification Project"
        if user_projects:
            selected_project_name = user_projects[0].name
        
        return templates.TemplateResponse(
            "user/support/how_to_use.html ",
            {
                "request": request,
                "services": services,
                "total_services": len(services),
                "countries": countries,
                "total_countries": len(countries),
                "selected_project_name": selected_project_name
            }
        )
    except Exception as e:
        import traceback
        error_detail = {
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": error_detail}
        )
@router.get("/purchase")
async def purchase(request: Request):
    try:
        # Verify database connection
        from app.config.database import db
        await db.client.admin.command('ping')
        
        # Get services with error handling for missing fields
        services = []
        cursor = Service.collection.find().sort("popularity", -1).limit(20)
        async for service in cursor:
            # Ensure required fields exist
            service.setdefault("name", "Unknown Service")
            service.setdefault("popularity", 0)
            service.setdefault("current_price", 0)
            service.setdefault("success_rate", 0.9)
            services.append(service)

        # Get active countries asynchronously
        countries = await Country.get_active_countries()

        # Hardcoded user_id for demonstration
        from bson import ObjectId
        user_id = ObjectId("507f1f77bcf86cd799439011")
        user_projects = await Project.get_user_projects(user_id)
        selected_project_name = "My Verification Project"
        if user_projects:
            selected_project_name = user_projects[0].name
        
        return templates.TemplateResponse(
            "user/orders/purchase.html ",
            {
                "request": request,
                "services": services,
                "total_services": len(services),
                "countries": countries,
                "total_countries": len(countries),
                "selected_project_name": selected_project_name
            }
        )
    except Exception as e:
        import traceback
        error_detail = {
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": error_detail}
        )
@router.get("/recharge")
async def recharge(request: Request):
    try:
        # Verify database connection
        from app.config.database import db
        await db.client.admin.command('ping')
        
        # Get services with error handling for missing fields
        services = []
        cursor = Service.collection.find().sort("popularity", -1).limit(20)
        async for service in cursor:
            # Ensure required fields exist
            service.setdefault("name", "Unknown Service")
            service.setdefault("popularity", 0)
            service.setdefault("current_price", 0)
            service.setdefault("success_rate", 0.9)
            services.append(service)

        # Get active countries asynchronously
        countries = await Country.get_active_countries()

        # Hardcoded user_id for demonstration
        from bson import ObjectId
        user_id = ObjectId("507f1f77bcf86cd799439011")
        user_projects = await Project.get_user_projects(user_id)
        selected_project_name = "My Verification Project"
        if user_projects:
            selected_project_name = user_projects[0].name
        
        return templates.TemplateResponse(
            "user/orders/recharge.html ",
            {
                "request": request,
                "services": services,
                "total_services": len(services),
                "countries": countries,
                "total_countries": len(countries),
                "selected_project_name": selected_project_name
            }
        )
    except Exception as e:
        import traceback
        error_detail = {
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": error_detail}
        )

@router.get("/free_phone_list")
async def free_phone_list(request: Request):
    try:
        # Verify database connection
        from app.config.database import db
        await db.client.admin.command('ping')
        
        # Get services with error handling for missing fields
        services = []
        cursor = Service.collection.find().sort("popularity", -1).limit(20)
        async for service in cursor:
            # Ensure required fields exist
            service.setdefault("name", "Unknown Service")
            service.setdefault("popularity", 0)
            service.setdefault("current_price", 0)
            service.setdefault("success_rate", 0.9)
            services.append(service)

        # Get active countries asynchronously
        countries = await Country.get_active_countries()

        # Hardcoded user_id for demonstration
        from bson import ObjectId
        user_id = ObjectId("507f1f77bcf86cd799439011")
        user_projects = await Project.get_user_projects(user_id)
        selected_project_name = "My Verification Project"
        if user_projects:
            selected_project_name = user_projects[0].name
        
        return templates.TemplateResponse(
            "user/orders/free_phone_list.html ",
            {
                "request": request,
                "services": services,
                "total_services": len(services),
                "countries": countries,
                "total_countries": len(countries),
                "selected_project_name": selected_project_name
            }
        )
    except Exception as e:
        import traceback
        error_detail = {
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": error_detail}
        )
    

@router.get("/api/services") 
async def get_services_api(sort_by: str = "popularity"):
    """API endpoint để lấy danh sách dịch vụ"""
    try:
        if sort_by == "price_asc":
            services = list(Service.collection.find().sort("current_price", 1))
        elif sort_by == "price_desc":
            services = list(Service.collection.find().sort("current_price", -1))
        else:
            services = list(Service.collection.find().sort("popularity", -1))
            
        return services
    except Exception as e:
        return {"error": str(e)}

@router.get("/login")
async def login(request: Request):
    try:
        # Verify database connection
        from app.config.database import db
        await db.client.admin.command('ping')
        
        # Get services with error handling for missing fields
        services = []
        cursor = Service.collection.find().sort("popularity", -1).limit(20)
        async for service in cursor:
            # Ensure required fields exist
            service.setdefault("name", "Unknown Service")
            service.setdefault("popularity", 0)
            service.setdefault("current_price", 0)
            service.setdefault("success_rate", 0.9)
            services.append(service)

        # Get active countries asynchronously
        countries = await Country.get_active_countries()

        # Hardcoded user_id for demonstration
        from bson import ObjectId
        user_id = ObjectId("507f1f77bcf86cd799439011")
        user_projects = await Project.get_user_projects(user_id)
        selected_project_name = "My Verification Project"
        if user_projects:
            selected_project_name = user_projects[0].name
        
        return templates.TemplateResponse(
            "user/auth/login.html",
            {
                "request": request,
                "services": services,
                "total_services": len(services),
                "countries": countries,
                "total_countries": len(countries),
                "selected_project_name": selected_project_name
            }
        )
    except Exception as e:
        import traceback
        error_detail = {
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": error_detail}
        )

@router.post("/login")
async def login_post(
    request: Request,
    response: Response,
    email: str = Form(...),
    password: str = Form(...)
):
    try:
        # Verify database connection
        from app.config.database import db
        await db.client.admin.command('ping')

        # Find user by email
        user = await User.collection.find_one({"email": email})
        if not user:
            return templates.TemplateResponse(
                "user/auth/login.html",
                {
                    "request": request,
                    "error": "Invalid email or password"
                }
            )
        # Verify password
        hashed_input_password = hash_password(password)
        if hashed_input_password != user.get("password"):
            return templates.TemplateResponse(
                "user/auth/login.html",
                {
                    "request": request,
                    "error": "Invalid email or password"
                }
            )
        # Create access token and set cookie
        access_token = create_access_token(email)
        redirect_response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
        redirect_response.set_cookie(key="user_token", value=access_token, httponly=True)
        return redirect_response
    except Exception as e:
        import traceback
        error_detail = {
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        return templates.TemplateResponse(
            "user/auth/login.html",
            {"request": request, "error": error_detail}
        )

from fastapi import Form, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2AuthorizationCodeBearer
from app.core.security import hash_password
from app.models.user import User
from fastapi import HTTPException

import secrets
from fastapi import Response

@router.get("/register")
async def register(request: Request):
    csrf_token = secrets.token_urlsafe(32)
    response = templates.TemplateResponse("user/auth/register.html", {"request": request, "csrf_token": csrf_token})
    response.set_cookie(key="csrf_token", value=csrf_token, httponly=True)
    return response

@router.post("/register")
async def register_post(
    request: Request,
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    terms: bool = Form(...),
    csrf_token: str = Form(...)
):
    # Validate CSRF token
    cookie_token = request.cookies.get("csrf_token")
    if not cookie_token or cookie_token != csrf_token:
        return templates.TemplateResponse("user/auth/register.html", {
            "request": request,
            "error": "Invalid CSRF token"
        })
    # Validate form inputs
    if password != confirm_password:
        return templates.TemplateResponse("user/auth/register.html", {
            "request": request,
            "error": "Passwords do not match"
        })
    if not terms:
        return templates.TemplateResponse("user/auth/register.html", {
            "request": request,
            "error": "You must agree to the terms and privacy policies"
        })
    # Check if user already exists
    existing_user = await User.collection.find_one({"email": email})
    if existing_user:
        return templates.TemplateResponse("user/auth/register.html", {
            "request": request,
            "error": "Email already registered"
        })
    # Hash password
    hashed_password = hash_password(password)
    # Create user
    user_data = {
        "email": email,
        "password": hashed_password,
        "username": email.split("@")[0],
        "phone": "",
        "balance": 0,
        "status": "active",
        "verification_level": 0,
        "registration_date": None,
        "ip_history": []
    }
    try:
        user_id = await User.create_user(user_data)
        print(f"User created with ID: {user_id}")
    except Exception as e:
        print(f"Error creating user: {str(e)}")
        return templates.TemplateResponse("user/auth/register.html", {
            "request": request,
            "error": f"Failed to create user: {str(e)}"
        })
    # Redirect to login or verification page
    redirect_response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    return redirect_response

@router.get("/auth/google")
async def auth_google(request: Request):
    redirect_uri = request.url_for('auth_google_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/auth/google/callback")
async def auth_google_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get('userinfo')
    
    if not user_info or not user_info.get('email'):
        return RedirectResponse(url="/register?error=google_auth_failed")
    
    # Kiểm tra hoặc tạo user
    existing_user = await User.collection.find_one({"email": user_info['email']})
    if not existing_user:
        user_data = {
            "email": user_info['email'],
            "password": None,  # Không có password khi đăng ký bằng social
            "username": user_info.get('name', user_info['email'].split('@')[0]),
            "auth_provider": "google",
            "status": "active",
        }
        await User.create_user(user_data)
    
    # Tạo session và chuyển hướng
    response = RedirectResponse(url="/dashboard")
    response.set_cookie(key="user_token", value=create_access_token(user_info['email']))
    return response

@router.get("/auth/discord")
async def auth_discord(request: Request):
    redirect_uri = request.url_for('auth_discord_callback')
    return await oauth.discord.authorize_redirect(request, redirect_uri)

@router.get("/auth/discord/callback")
async def auth_discord_callback(request: Request):
    discord = oauth.create_client('discord')
    token = await discord.authorize_access_token(request)
    resp = await discord.get('https://discord.com/api/users/@me', token=token)
    user_info = resp.json()
    
    if not user_info or not user_info.get('email'):
        return RedirectResponse(url="/register?error=discord_auth_failed")
    
    # Kiểm tra hoặc tạo user
    existing_user = await User.collection.find_one({"email": user_info['email']})
    if not existing_user:
        user_data = {
            "email": user_info['email'],
            "password": None,  # Không có password khi đăng ký bằng social
            "username": user_info.get('name', user_info['email'].split('@')[0]),
            "auth_provider": "discord",
            "status": "active",
        }
        await User.create_user(user_data)
    
    # Tạo session và chuyển hướng
    response = RedirectResponse(url="/dashboard")
    response.set_cookie(key="user_token", value=create_access_token(user_info['email']))
    return response

@router.get("/auth/twitter")
async def auth_twitter(request: Request):
    redirect_uri = request.url_for('auth_twitter_callback')
    return await oauth.twitter.authorize_redirect(request, redirect_uri)

@router.get("/auth/twitter/callback")
async def auth_twitter_callback(request: Request):
    twitter = oauth.create_client('twitter')
    token = await twitter.authorize_access_token(request)
    resp = await twitter.get('https://api.twitter.com/2/users/me', token=token)
    user_info = resp.json()
    
    # Twitter có thể không trả về email, cần xử lý riêng
    # TODO: Handle missing email case here
    
    # Kiểm tra hoặc tạo user
    existing_user = await User.collection.find_one({"email": user_info.get('email')})
    if not existing_user and user_info.get('email'):
        user_data = {
            "email": user_info['email'],
            "password": None,  # Không có password khi đăng ký bằng social
            "username": user_info.get('name', user_info['email'].split('@')[0]),
            "auth_provider": "twitter",
            "status": "active",
        }
        await User.create_user(user_data)
    
    # Tạo session và chuyển hướng
    response = RedirectResponse(url="/dashboard")
    response.set_cookie(key="user_token", value=create_access_token(user_info.get('email')))
    return response

@router.get("/auth/telegram")
async def auth_telegram(request: Request):
    # Telegram sử dụng widget login, không phải OAuth thông thường
    # Bạn cần triển khai frontend trước
    return {"message": "Use Telegram login widget on frontend"}

@router.post("/auth/telegram/callback")
async def auth_telegram_callback(request: Request, data: dict):
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    secret_key = hashlib.sha256(bot_token.encode()).digest()
    
    # Xác minh dữ liệu
    check_string = '\n'.join(f"{k}={v}" for k, v in sorted(data.items()) if k != 'hash')
    computed_hash = hmac.new(secret_key, check_string.encode(), hashlib.sha256).hexdigest()
    
    if computed_hash != data.get('hash'):
        return {"error": "Invalid Telegram data"}
    
    # Lưu thông tin user
    user_data = {
        "auth_provider": "telegram",
        "telegram_id": data.get('id'),
        "username": data.get('username'),
        "first_name": data.get('first_name'),
        "last_name": data.get('last_name'),
    }
    
    # Xử lý tạo user hoặc đăng nhập
    # TODO: Implement user creation or login for Telegram
