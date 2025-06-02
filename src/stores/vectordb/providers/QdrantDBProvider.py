from qdrant_client import QdrantClient, models
from ..VectorDBInterface import VectorDBInterface
from ..VectorDBEnums import VectorDBEnums, DistanceMethodEnums
from models.db_schemes import RetrievedDocument
from typing import List, Dict, Any
import logging


class QdrantDBProvider(VectorDBInterface):
    def __init__(self, db_path: str, distance_method: str):
        """
        Initialize the QdrantDBProvider.

        Args:
            db_path (str): The path to the Qdrant database.
            distance_method (str): The distance method to use (e.g., "cosine", "dot").
        """
        self.client = None
        self.db_path = db_path
        self.distance_method = None

        if distance_method == DistanceMethodEnums.COSINE.value:
            self.distance_method = models.Distance.COSINE
        elif distance_method == DistanceMethodEnums.DOT.value:
            self.distance_method = models.Distance.DOT

        self.logger = logging.getLogger(__name__)

    async def connect(self) -> None:
        """Connect to the Qdrant database."""
        self.client = QdrantClient(path=self.db_path)
        self.logger.info(f"Connected to Qdrant database at {self.db_path}")
        
    async def disconnect(self) -> None:
        """Disconnect from the Qdrant database."""
        if self.client:
            self.client.close()
            self.logger.info("Disconnected from Qdrant database")
    
    async def is_collection_existed(self, collection_name: str) -> bool:
        """Check if a collection exists in the Qdrant database.

        Args:
            collection_name (str): The name of the collection to check.

        Returns:
            bool: True if the collection exists, False otherwise.
        """
        return self.client.collection_exists(collection_name=collection_name)
    
    async def list_all_collections(self) -> List[str]:
        """List all collections in the Qdrant database.

        Returns:
            List[str]: A list of collection names.
        """
        collections = self.client.get_collections()
        return [collection.name for collection in collections.collections]
    
    async def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get information about a specific collection.

        Args:
            collection_name (str): The name of the collection.

        Returns:
            Dict[str, Any]: A dictionary containing collection information.
        """
        return self.client.get_collection(collection_name=collection_name)
    
    async def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection from the Qdrant database.

        Args:
            collection_name (str): The name of the collection to delete.
            
        Returns:
            bool: True if the collection was deleted successfully, False otherwise.
        """
        if await self.is_collection_existed(collection_name=collection_name):
            self.logger.info(f"Deleting collection: {collection_name}")
            result = self.client.delete_collection(collection_name=collection_name)
            self.logger.info(f"Deleted collection: {collection_name}")
            return True
        else:
            self.logger.warning(f"Collection {collection_name} does not exist.")
            return False

    async def create_collection(self, collection_name: str, embedding_size: int, do_reset: bool = False) -> bool:
        """Create a new collection in the Qdrant database.

        Args:
            collection_name (str): The name of the collection to create.
            embedding_size (int): The size of the embeddings.
            do_reset (bool): Whether to reset the collection if it already exists.

        Returns:
            bool: True if the collection was created successfully, False otherwise.
        """
        if do_reset:
            await self.delete_collection(collection_name=collection_name)
        
        if not await self.is_collection_existed(collection_name=collection_name):
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=embedding_size,
                    distance=self.distance_method
                )
            )
            self.logger.info(f"Created collection: {collection_name}")
            return True
        
        self.logger.warning(f"Collection {collection_name} already exists.")
        return False
    
    async def insert_one(self, collection_name: str, text: str, vector: list,
                    metadata: Dict[str, Any] = None, record_id: str = None) -> bool:
        """Insert a single document into the Qdrant database.

        Args:
            collection_name (str): The name of the collection.
            text (str): The text to insert.
            vector (list): The vector representation of the text.
            metadata (Dict[str, Any], optional): Additional metadata for the document.
            record_id (str, optional): The ID of the record.

        Returns:
            bool: True if the insertion was successful, False otherwise.
        """
        if not await self.is_collection_existed(collection_name=collection_name):
            self.logger.error(f"Collection {collection_name} does not exist.")
            return False
        
        try:
            record = models.Record(
                id=record_id,
                vector=vector,
                payload={"text": text, "metadata": metadata},
            )
            
            self.client.upload_records(
                collection_name=collection_name,
                records=[record]
            )

        except Exception as e:
            self.logger.error(f"Error inserting document: {e}")
            return False
        
        self.logger.info(f"Inserted document into collection {collection_name}")
        return True
    
    async def insert_many(self, collection_name: str, texts: List[str], vectors: List[list],
                    metadata: List[Dict[str, Any]] = None, record_ids: List[str] = None, 
                    batch_size: int = 50) -> bool:
        """Insert multiple documents into the Qdrant database.

        Args:
            collection_name (str): The name of the collection.
            texts (List[str]): The texts to insert.
            vectors (List[list]): The vector representations of the texts.
            metadata (List[Dict[str, Any]], optional): Additional metadata for the documents.
            record_ids (List[str], optional): The IDs of the records.
            batch_size (int): The number of documents to insert in each batch.

        Returns:
            bool: True if the insertion was successful, False otherwise.
        """
        if not await self.is_collection_existed(collection_name=collection_name):
            self.logger.error(f"Collection {collection_name} does not exist.")
            return False
            
        if metadata is None:
            metadata = [None] * len(texts)
        if record_ids is None:
            record_ids = list(range(len(texts)))
        
        for i in range(0, len(texts), batch_size):
            batch_end = min(i + batch_size, len(texts))
            batch_texts = texts[i:batch_end]
            batch_vectors = vectors[i:batch_end]
            batch_metadata = metadata[i:batch_end]
            batch_record_ids = record_ids[i:batch_end]
            
            batch_records = [
                models.Record(
                    id=batch_record_ids[x],
                    vector=batch_vectors[x],
                    payload={"text": batch_texts[x], "metadata": batch_metadata[x]},
                )
                for x in range(len(batch_texts))
            ]
            
            try:
                self.client.upload_records(
                    collection_name=collection_name,
                    records=batch_records
                )
            except Exception as e:
                self.logger.error(f"Error inserting documents: {e}")
                return False
            
        self.logger.info(f"Inserted {len(texts)} documents into collection {collection_name}")
        return True
    
    async def search_by_vector(self, collection_name: str, vector: list,
                        limit: int = 5) -> List[RetrievedDocument]:
        """Search for documents in the Qdrant database using a vector.

        Args:
            collection_name (str): The name of the collection.
            vector (list): The vector to search for.
            limit (int): The maximum number of results to return.

        Returns:
            List[RetrievedDocument]: A list of RetrievedDocument objects containing the search results.
        """
        if not await self.is_collection_existed(collection_name=collection_name):
            self.logger.error(f"Collection {collection_name} does not exist.")
            return []
            
        try:
            results = self.client.search(
                collection_name=collection_name,
                query_vector=vector,
                limit=limit
            )
            
            if not results or len(results) == 0:
                self.logger.warning(f"No results found for vector search in collection {collection_name}")
                return []
            
            return [
                RetrievedDocument(
                    score=result.score,
                    text=result.payload["text"],
                )
                for result in results
            ]
            
        except Exception as e:
            self.logger.error(f"Error searching in collection {collection_name}: {e}")
            return []