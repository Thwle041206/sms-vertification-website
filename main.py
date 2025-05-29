from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.routes import user_routes
import uvicorn

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    from app.config.database import connect_to_mongo
    if not await connect_to_mongo():
        raise RuntimeError("Failed to connect to MongoDB")
    yield
    # Shutdown logic
    from app.config.database import close_mongo_connection
    await close_mongo_connection()

app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/views")
app.include_router(user_routes.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
