from fastapi import FastAPI
from contextlib import asynccontextmanager
from routes import base, data, nlp
from motor.motor_asyncio import AsyncIOMotorClient
from helpers import get_settings
import logging
from stores.llm.LLMProviderFactory import LLMProviderFactory
from stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    try:
        app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
        app.db_client = app.mongo_conn[settings.MONGODB_DATABASE]
        logger.info("MongoDB connection established")
        
        llm_provider_factory = LLMProviderFactory(settings)
        vector_db_provider_factory = VectorDBProviderFactory(settings)

        # generation client
        app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
        app.generation_client.set_generation_model(model_id = settings.GENERATION_MODEL_ID)

        # embedding client
        app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
        app.embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID,
                                                embedding_size=settings.EMBEDDING_MODEL_SIZE)
        
        # vector db client
        app.vectordb_client = vector_db_provider_factory.create(provider=settings.VECTOR_DB_BACKEND)
        app.vectordb_client.connect()


        await app.mongo_conn.admin.command("ping")
        logger.info("Connected to MongoDB (DB: %s)", settings.MONGODB_DATABASE)
        yield
    except Exception as e:
        logger.error("MongoDB connection failed: %s", e)
        raise
    finally:
        app.mongo_conn.close()
        app.vectordb_client.disconnect()
        logger.info("MongoDB connection closed")

app = FastAPI(lifespan=lifespan)

app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)


