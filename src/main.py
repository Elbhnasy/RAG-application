from fastapi import FastAPI
from contextlib import asynccontextmanager
from routes import base, data
from motor.motor_asyncio import AsyncIOMotorClient
from helpers import get_settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    try:
        # Initialize client and database
        app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
        app.db_client = app.mongo_conn[settings.MONGODB_DATABASE]
        
        # Verify connection
        await app.mongo_conn.admin.command("ping")
        logger.info("Connected to MongoDB (DB: %s)", settings.MONGODB_DATABASE)
    except Exception as e:
        logger.error("MongoDB connection failed: %s", e)
        raise
    yield
    app.mongo_conn.close()
    logger.info("MongoDB connection closed")

app = FastAPI(lifespan=lifespan)

app.include_router(base.base_router)
app.include_router(data.data_router)