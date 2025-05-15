from helpers import get_settings , Settings
from pydantic import BaseModel, Field

class BaseDataModel(BaseModel):
    def __init__(self,db_client : object):
        self.db_client = db_client
        self.app_settings = get_settings()