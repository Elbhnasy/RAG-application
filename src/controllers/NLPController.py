from .BaseController import BaseController
from models.db_schemes import Project, DataChunk
from stores.llm.LLMEnums import DocumentTypeEnum
from typing import List, Optional, Tuple
import logging
import json

logger = logging.getLogger(__name__)

class NLPController(BaseController):
    def __init__(self, vectordb_client, generation_client, embedding_client, template_parser):
        super().__init__()
        self.vectordb_client = vectordb_client
        self.generation_client = generation_client
        self.embedding_client = embedding_client
        self.template_parser = template_parser

    def create_collection_name(self, project_id: str) -> str:
        """Create a collection name for the project."""
        return f"collection_{project_id}"
    
    def reset_vector_db_collection(self, project: Project) -> bool:
        """Reset the vector db collection for the project."""
        collection_name = self.create_collection_name(project_id=project.project_id)
        return self.vectordb_client.delete_collection(collection_name=collection_name)
    
    def get_vector_db_collection_info(self, project: Project) -> dict:
        """Get the vector db collection info for the project."""
        collection_name = self.create_collection_name(project_id=project.project_id)
        collection_info = self.vectordb_client.get_collection_info(collection_name=collection_name)
        return json.loads(
            json.dumps(
                collection_info, 
                default=lambda o: o.__dict__ if hasattr(o, '__dict__') else str(o)
            )
        )
     
    
    def index_into_vector_db(self, project: Project, chunks: List[DataChunk],
                           chunks_ids: List[int], do_reset: bool = False) -> bool:
        """Index the chunks into the vector db."""
        try:
            collection_name = self.create_collection_name(project_id=project.project_id)

            texts = [chunk.chunk_text for chunk in chunks]
            metadata = [chunk.chunk_metadata for chunk in chunks]
            vectors = [
                self.embedding_client.embed_text(text=text, document_type=DocumentTypeEnum.DOCUMENT.value)
                for text in texts
            ]

            self.vectordb_client.create_collection(
                collection_name=collection_name,
                embedding_size=self.embedding_client.embedding_size,
                do_reset=do_reset
            )

            self.vectordb_client.insert_many(
                collection_name=collection_name,
                texts=texts,
                vectors=vectors,
                metadata=metadata,
                record_ids=chunks_ids
            )
            return True
        except Exception as e:
            logger.error(f"Failed to index chunks into vector DB: {e}")
            return False
    
    def search_vector_db_collection(self, project: Project, text: str, limit: int = 10) -> Optional[List]:
        """Search the vector db collection for the project."""
        try:
            collection_name = self.create_collection_name(project_id=project.project_id)
            
            vector = self.embedding_client.embed_text(
                text=text,
                document_type=DocumentTypeEnum.QUERY.value
            )

            if not vector:
                return None
            
            results = self.vectordb_client.search_by_vector(
                collection_name=collection_name,
                vector=vector,
                limit=limit
            )
            return results if results else None
        except Exception as e:
            logger.error(f"Failed to search vector DB: {e}")
            return None
        
    def answer_rag_question(self, project: Project, query: str, limit: int = 10) -> Tuple[Optional[str], Optional[str], Optional[List]]:
        """Answer a question using the RAG model."""
        try:
            retrieved_documents = self.search_vector_db_collection(
                project=project,
                text=query,
                limit=limit
            )

            if not retrieved_documents:
                return None, None, None
            
            system_prompts = self.template_parser.get("rag", "system_prompt")
            
            documents_prompt = "\n".join([
                self.template_parser.get("rag", "document_prompt", {
                    "doc_num": idx + 1,
                    "chunk_text": self.generation_client.process_text(doc.text),
                })
                for idx, doc in enumerate(retrieved_documents)
            ])

            footer_prompt = self.template_parser.get("rag", "footer_prompt", {"query": query})

            chat_history = [
                self.generation_client.construct_prompt(
                    prompt=system_prompts,
                    role=self.generation_client.enums.SYSTEM.value,
                )
            ]

            full_prompt = "\n\n".join([documents_prompt, footer_prompt])

            answer = self.generation_client.generate_text(
                prompt=full_prompt,
                chat_history=chat_history
            )
            return answer, full_prompt, chat_history
        except Exception as e:
            logger.error(f"Failed to answer RAG question: {e}")
            return None, None, None
