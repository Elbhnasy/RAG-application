from pydantic import BaseModel, Field , field_validator
from typing import Optional, List
from bson.objectid import ObjectId

class Project(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    Project_id : str = Field(..., min_length=1)

    @field_validator('Project_id')
    def validate_project_id(cls, value):
        if not value.isalnum():
            raise ValueError('Project_id must be alphanumeric')
        return value
    
    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def get_indexes(cls):
        return[
            {
                "key": [("Project_id", 1)],
                "name": "Project_id_index_1",
                "unique": True
            }
        ]