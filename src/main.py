from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
from routes import base, data, nlp
from motor.motor_asyncio import AsyncIOMotorClient
from helpers import get_settings
import logging
from stores.llm.LLMProviderFactory import LLMProviderFactory
from stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory
from stores.llm.templates.template_parser import TemplateParser
import time
import uuid


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    
    # Validate critical settings
    required_settings = ['MONGODB_URL', 'MONGODB_DATABASE', 'GENERATION_BACKEND', 'EMBEDDING_BACKEND']
    for setting in required_settings:
        if not getattr(settings, setting, None):
            raise ValueError(f"Missing required setting: {setting}")
    
    try:
        # MongoDB connection
        app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
        app.db_client = app.mongo_conn[settings.MONGODB_DATABASE]
        await app.mongo_conn.admin.command("ping")
        logger.info("MongoDB connection established (DB: %s)", settings.MONGODB_DATABASE)
        
        # Initialize factories
        llm_provider_factory = LLMProviderFactory(settings)
        vector_db_provider_factory = VectorDBProviderFactory(settings)

        # Initialize LLM clients with validation
        try:
            app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
            app.generation_client.set_generation_model(model_id=settings.GENERATION_MODEL_ID)
            logger.info("Generation client initialized: %s", settings.GENERATION_BACKEND)
        except Exception as e:
            logger.error("Failed to initialize generation client: %s", e)
            raise

        try:
            app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
            app.embedding_client.set_embedding_model(
                model_id=settings.EMBEDDING_MODEL_ID,
                embedding_size=settings.EMBEDDING_MODEL_SIZE
            )
            logger.info("Embedding client initialized: %s", settings.EMBEDDING_BACKEND)
        except Exception as e:
            logger.error("Failed to initialize embedding client: %s", e)
            raise
        
        try:
            app.vectordb_client = vector_db_provider_factory.create(providr=settings.VECTOR_DB_BACKEND)
            app.vectordb_client.connect()
            logger.info("Vector DB client initialized: %s", settings.VECTOR_DB_BACKEND)
        except Exception as e:
            logger.error("Failed to initialize vector DB client: %s", e)
            raise

        app.template_parser = TemplateParser(
            language=settings.PRIMARY_LANG,
            default_language=settings.DEFAULT_LANG
        )
        logger.info("Template parser initialized")

        logger.info("All services initialized successfully")
        yield
        
    except Exception as e:
        logger.error("Service initialization failed: %s", e)
        raise
    finally:
        # Graceful shutdown
        logger.info("Shutting down services...")
        
        if hasattr(app, 'mongo_conn') and app.mongo_conn:
            app.mongo_conn.close()
            logger.info("MongoDB connection closed")
            
        if hasattr(app, 'vectordb_client') and app.vectordb_client:
            try:
                app.vectordb_client.disconnect()
                logger.info("Vector DB connection closed")
            except Exception as e:
                logger.error("Error closing vector DB connection: %s", e)

app = FastAPI(
    title="RAG Application API",
    description="A Retrieval-Augmented Generation application",
    version="1.0.0",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    logger.info(
        "Request started - ID: %s, Method: %s, URL: %s",
        request_id, request.method, str(request.url)
    )
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(
        "Request completed - ID: %s, Status: %s, Time: %.3fs",
        request_id, response.status_code, process_time
    )
    
    return response

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint to verify service status"""
    try:
        # Check MongoDB
        await app.mongo_conn.admin.command("ping")
        
        # Check Vector DB (if it has a health check method)
        vector_db_status = "connected" if hasattr(app, 'vectordb_client') else "not_initialized"
        
        return {
            "status": "healthy",
            "services": {
                "mongodb": "connected",
                "vector_db": vector_db_status,
                "generation_client": "initialized" if hasattr(app, 'generation_client') else "not_initialized",
                "embedding_client": "initialized" if hasattr(app, 'embedding_client') else "not_initialized"
            }
        }
    except Exception as e:
        logger.error("Health check failed: %s", e)
        raise HTTPException(status_code=503, detail="Service unhealthy")

app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)


