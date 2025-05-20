from .providers import QdrantDBProvider
from VectorDBEnums import VectorDBEnums
from controllers.BaseController import BaseController

class VectorDBProviderFactory:
    def __init__(self,config):
        self.config = config
        self.controller = BaseController()

    def create (self, providr:str) -> object:
        """
        Create a vector database provider based on the provider name
        """
        if providr == VectorDBEnums.QDRANT.value:
            db_path = self.controller.get_database_path(db_name=self.config.VECTOR_DB_PATH)
            return QdrantDBProvider(
                path=db_path,
                distance_method=self.config.VECTOR_DB_DISTANCE_METHOD
            )
        return None