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
    
    def delete_collection(self, collection_name: str) :
        """Delete a collection from the Qdrant database.

        Args:
            collection_name (str): The name of the collection to delete.
        """
        if self.is_collection_existed(collection_name=collection_name):
            self.logger.info(f"Deleted collection: {collection_name}")
            return self.client.delete_collection(collection_name=collection_name)

    def create_collection(self, collection_name: str,embedding_size: int, do_reset: bool = False) -> bool:
        """Create a new collection in the Qdrant database.

        Args:
            collection_name (str): The name of the collection to create.
            embedding_size (int): The size of the embeddings.
            do_reset (bool): Whether to reset the collection if it already exists.

        Returns:
            bool: True if the collection was created successfully, False otherwise.
        """
        if do_reset:
            _=self.delete_collection(collection_name=collection_name)
        
        if not self.is_collection_existed(collection_name=collection_name):
            _= self.client.create_collection(
                collection_name= collection_name,
                vectors_config= models.VectorParams(
                    size= embedding_size,
                    distance= self.distance_method
                )
            )
            self.logger.info(f"Created collection: {collection_name}")
            return True
        self.logger.warning(f"Collection {collection_name} already exists.")
        return False
    
    def insert_one(self, collection_name: str, text: str, vector: list,
                    metadata: Dict[str, Any] = None) -> bool:
        """Insert a single document into the Qdrant database.

        Args:
            collection_name (str): The name of the collection.
            text (str): The text to insert.
            vector (list): The vector representation of the text.
            metadata (Dict[str, Any], optional): Additional metadata for the document.

        Returns:
            bool: True if the insertion was successful, False otherwise.
        """
        if not self.is_collection_existed(collection_name=collection_name):
            self.logger.error(f"Collection {collection_name} does not exist.")
            return False
        
        try:
            _= self.client.upload_records(
                collection_name = collection_name,
                records= [models.Record(
                    vector= vector,
                    payload= {"text":text, "metadata": metadata},
                )]
            )

        except Exception as e:
            self.logger.error(f"Error inserting document: {e}")
            return False
        
        self.logger.info(f"Inserted document into collection {collection_name}")
        return True
    
    def insert_many(self, collection_name: str, texts: List[str], vectors: List[list],
                    metadata: List[Dict[str, Any]] = None,record_ids:List[str]=None, 
                    batch_size:int = 50) -> bool:
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
        if metadata is None:
            metadata = [None] * len(texts)
        if record_ids is None:
            record_ids = [None] * len(texts)
        
        for i in range(0, len(texts), batch_size):
            batch_end = i+batch_size
            batch_texts = texts[i:batch_end]
            batch_vectors = vectors[i:batch_end]
            batch_metadata = metadata[i:batch_end]
            batch_records = [
                models.Record(
                    vector= batch_vectors[x],
                    payload= {"text": batch_texts[x], "metadata": batch_metadata[x]},
                )
                for x in range(len(batch_texts))
            ]
            try:
                _= self.client.upload_records(
                    collection_name= collection_name,
                    records= batch_records
                )
            except Exception as e:
                self.logger.error(f"Error inserting documents: {e}")
                return False
            
        self.logger.info(f"Inserted {len(texts)} documents into collection {collection_name}")
        return True
    
    def  search_by_vector(self, collection_name: str, vector: list,
                        limit: int = 5) -> List[Dict[str, Any]]:
        """Search for documents in the Qdrant database using a vector.

        Args:
            collection_name (str): The name of the collection.
            vector (list): The vector to search for.
            limit (int): The maximum number of results to return.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing the search results.
        """

        return self.client.search(
            collection_name= collection_name,
            query_vector= vector,
            limit= limit
        )