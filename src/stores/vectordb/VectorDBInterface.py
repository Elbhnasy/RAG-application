from abc import ABC, abstractmethod
from models.db_schemes.data_chunk import RetrievedDocument
from typing import List, Dict, Any, Optional

class VectorDBInterface(ABC):

    @abstractmethod
    def connect(self) -> None:
        """Connect to the vector database."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from the vector database."""
        pass

    @abstractmethod
    def is_collection_existed(self, collection_name: str) -> bool:
        """Check if a collection exists in the vector database.

        Args:
            collection_name (str): The name of the collection to check.

        Returns:
            bool: True if the collection exists, False otherwise.
        """
        pass
    
    @abstractmethod
    def list_all_collections(self) -> List[str]:
        """List all collections in the vector database.

        Returns:
            List[str]: A list of collection names.
        """
        pass

    @abstractmethod
    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get information about a specific collection.

        Args:
            collection_name (str): The name of the collection.

        Returns:
            Dict[str, Any]: A dictionary containing collection information.
        """
        pass

    @abstractmethod
    def delete_collection(self, collection_name: str) :
        """Delete a collection from the vector database.

        Args:
            collection_name (str): The name of the collection to delete.
        """
        pass

    @abstractmethod
    def create_collection(self, collection_name: str, 
                                embedding_size: int,
                                do_reset: bool = False) -> bool:
        """Create a new collection in the vector database.

        Args:
            collection_name (str): The name of the collection to create.
            embedding_size (int): The size of the embeddings.
            do_reset (bool): Whether to reset the collection if it already exists.
        Returns:
            bool: True if the collection was created successfully, False otherwise.
        """
        pass

    @abstractmethod
    def insert_one(self, collection_name: str, text: str, vector: list,
                        metadata: Optional[dict] = None, record_id: Optional[str] = None) -> bool:
        """Insert a single record into the collection.

        Args:
            collection_name (str): The name of the collection.
            text (str): The text to insert.
            vector (list): The vector representation of the text.
            metadata (dict, optional): Additional metadata for the record.
            record_id (str, optional): The ID of the record.

        Returns:
            bool: True if the record was inserted successfully, False otherwise.
        """ 
        pass

    @abstractmethod
    def insert_many(self, collection_name: str, texts: List[str], vectors: List[list],
                        metadatas: List[dict] = None, record_ids: List[str] = None, batch_size : int  = 50 ) -> List[str]:
        """Insert multiple records into the collection.

        Args:
            collection_name (str): The name of the collection.
            texts (List[str]): The texts to insert.
            vectors (List[list]): The vector representations of the texts.
            metadatas (List[dict], optional): Additional metadata for the records.
            record_ids (List[str], optional): The IDs of the records.
            batch_size (int, optional): The number of records to insert in each batch.
        Returns:
            List[str]: A list of IDs of the inserted records.
        """
        pass

    @abstractmethod
    def search_by_vector(self, collection_name: str, vector: list,
                        limit: int = 10) -> List[RetrievedDocument]:
        """Search for records in the collection based on a vector.

        Args:
            collection_name (str): The name of the collection.
            vector (list): The vector to search for.
            limit (int): The maximum number of records to return.

        Returns:
            List[Dict[str, Any]]: A list of matching records.
        """
        pass