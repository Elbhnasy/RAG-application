from fastapi import FastAPI, APIRouter, Depends
from helpers import get_settings, Settings
import os

base_router = APIRouter(
    prefix="/api/v1",
    tags=["api_v1"],
)

@base_router.get("/")
async def welcome(app_settings: Settings = Depends(get_settings)):
    app_name = app_settings.APP_NAME
    app_version = app_settings.APP_VERSION
    app_description = app_settings.APP_DESCRIPTION
    return {
        "message": f"Welcome to {app_name} API",
        "version": app_version,
        "description": app_description
    }