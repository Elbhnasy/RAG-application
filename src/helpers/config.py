from pydantic_settings import BaseSettings
from typing import Optional,List

class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    APP_DESCRIPTION: str
    OPENAI_API_KEY: Optional[str] = None
    FILE_ALLOWED_TYPES: str
    FILE_MAX_SIZE: int
    FILE_DEFULT_CHUNK_SIZE: int
    MONGODB_URL: str
    MONGODB_DATABASE: str
    POSTGRES_USERNAME: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_MAIN_DATABASE: str

    GENERATION_BACKEND: str
    EMBEDDING_BACKEND: str

    OPENAI_API_KEY: str = None
    OPENAI_API_URL: str = None
    COHERE_API_KEY: str = None
    COHERE_API_URL: str = None

    GENERATION_MODEL_ID_LITERAL: List[str] = None
    GENERATION_MODEL_ID: str = None
    EMBEDDING_MODEL_ID: str = None
    EMBEDDING_MODEL_SIZE: int = None
    INPUT_DAFAULT_MAX_CHARACTERS: int = None
    GENERATION_DAFAULT_MAX_TOKENS: int = None
    GENERATION_DAFAULT_TEMPERATURE: float = None
    VECTOR_DB_PGVEC_INDEX_THRESHOLD: int = 100
    VECTOR_DB_BACKEND_LITERAL: List[str] = None
    VECTOR_DB_BACKEND: str
    VECTOR_DB_PATH: str
    VECTOR_DB_DISTANCE_METHOD: str = None


    PRIMARY_LANG: str = "en"
    DEFAULT_LANG: str = "en"
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

def get_settings() -> Settings:
    return Settings()