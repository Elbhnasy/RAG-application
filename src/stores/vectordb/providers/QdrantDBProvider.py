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
        
    