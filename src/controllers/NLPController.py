from BaseController import BaseController
from models.db_schemes import Project, DataChunk
from stores.llm.LLMEnums import DocumentTypeEnum
from typing import List
import json


class NLPController(BaseController):
    def __init__(self, vectordb_client, generation_client, embedding_client, template_parser):
        super().__init__()

        self.vectordb_client = vectordb_client
        self.generation_client = generation_client
        self.embedding_client = embedding_client
        self.template_parser = template_parser

    def create_collection_name(self, project_id: str):
        """
        Create a collection name for the project.
        """
        return f"collection_{project_id}".strip()
    
    def reset_vector_db_collection(self, project : Project):
        """
        Reset the vector db collection for the project.
        """
        collection_name = self.create_collection_name(project_id=project.id)
        return self.vectordb_client.delete_collection(collection_name=collection_name)
    
    def get_vector_db_collection_info(self, project : Project):
        """
        Get the vector db collection info for the project.
        """
        collection_name = self.create_collection_name(project_id=project.id)
        collection_info = self.vectordb_client.get_collection_info(collection_name=collection_name)
        return json.loads(
            json.dumps(
                collection_info,
                default=lambda o: o.__dict__,
            )
        )
    
    def index_into_vector_db(self, project: Project, chunks: List[DataChunk],
                                chunks_ids: List[int], do_reset: bool = False):
        """
        Index the chunks into the vector db.
        """

        collection_name = self.create_collection_name(project_id=project.id)