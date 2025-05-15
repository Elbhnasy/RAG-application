from .BaseDataModel import BaseDataModel
from .db_schemes import Project
from .enums.DataBaseEnum import DataBaseEnum

class ProjectModel(BaseDataModel):
    def __init__(self, db_client = db_client):
        super().__init__(db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]

    async def create_project(self, project: Project):
        result = await self.collection.insert_one(project.model_dump(by_alias=True, exclude_unset=True))
        project._id = result.inserted_id
        return project
    
    async def get_project_or_create_one(self, project_id: str):
        record = await self.collection.find_one({"Project_id": project_id})
        if record is None:
            project = Project(Project_id=project_id)
            project = await self.create_project(project=project)
            return project
        
        return Project(**record)