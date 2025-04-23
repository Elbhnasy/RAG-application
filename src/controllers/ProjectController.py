from .BaseController import BaseController
from models import ResponseSignal
from fastapi import UploadFile
import os

class ProjectController(BaseController):
    def __init__(self):
        super().__init__()

    def get_project_path(self, project_id: str) -> str:
        """
        Get the path of the project with the given ID.
        """
        project_dir = os.path.join(self.files_dir, project_id)
        if not os.path.exists(project_dir):
            os.makedirs(project_dir)

        return project_dir