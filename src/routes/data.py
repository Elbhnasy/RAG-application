from fastapi import APIRouter, Depends, UploadFile
from helpers import get_settings, Settings
from controllers import DataController


data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1","data"],
)


@data_router.post("/upload/{project_id}")
async def upload_data(project_id: str, file:UploadFile,
                    app_settings: Settings = Depends(get_settings)):
    is_valid, result_signals = DataController().validate_uploaded_file(file=file)
    return {
        "is_valid": is_valid,
        "result_signals": result_signals
    }