from qdrant_client import QdrantClient, models
from ..VectorDBInterface import VectorDBInterface
from ..VectorDBEnums import VectorDBEnums, DistanceMethodEnums
from typing import List, Dict, Any
import logging


class QdrantDBProvider(VectorDBInterface):
    def __init__(self, db_bath: str, distance_method: str):
        """
        Initialize the QdrantDBProvider.

        Args:
            db_bath (str): The path to the Qdrant database.
            distance_method (str): The distance method to use (e.g., "cosine", "dot").
        """
        self.client = None
        self.db_bath = db_bath
        self.distance_method = None

        if distance_method == DistanceMethodEnums.COSINE.value:
            self.distance_method = models.Distance.COSINE
        elif distance_method == DistanceMethodEnums.DOT.value:
            self.distance_method = models.Distance.DOT

        self.logger = logging.getLogger(__name__)

    def connect(self) -> None:
        """Connect to the Qdrant database."""
        self.client = QdrantClient(path=self.db_bath)
        self.logger.info(f"Connected to Qdrant database at {self.db_bath}")
        
    def disconnect(self) -> None:
        """Disconnect from the Qdrant database."""
        self.client.close()
        self.logger.info("Disconnected from Qdrant database")
    
    def is_collection_existed(self, collection_name: str) -> bool:
        """Check if a collection exists in the Qdrant database.

        Args:
            collection_name (str): The name of the collection to check.

        Returns:
            bool: True if the collection exists, False otherwise.
        """
        return self.client.collection_exists(collection_name=collection_name)
    
    def list_all_collections(self) -> List[str]:
        """List all collections in the Qdrant database.

        Returns:
            List[str]: A list of collection names.
        """
        return self.client.get_collections()
    
    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get information about a specific collection.

        Args:
            collection_name (str): The name of the collection.

        Returns:
            Dict[str, Any]: A dictionary containing collection information.
        """
        return self.client.get_collection(collection_name=collection_name)