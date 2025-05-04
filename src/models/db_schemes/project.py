from pydantic import BaseModel, Field , field_validator
from typing import Optional, List
from bson.objectid import ObjectId

class Project(BaseModel):
    _id : Optional[ObjectId]
    Project_id : str = Field(..., min_length=1)

    @field_validator('Project_id')
    def validate_project_id(cls, value):
        if not value.isalnum():
            raise ValueError('Project_id must be alphanumeric')
        return value
    
    class Config:
        arbitrary_types_allowed = True