from ..LLMInterface import LLMInterface
from ..LLMEnums import CoHereEnums, DocumentTypeEnum
from typing import List,Union
import cohere
import logging

class CoHereProvider(LLMInterface):
    def __init__(self,api_key: str,
                    default_input_max_characters: int=1000,
                    default_generation_max_output_tokens: int=1000,
                    default_generation_temperature: float=0.1):
        """
        Initialize the CoHereProvider with the given API key and default parameters.
        
        :param api_key: The API key for CoHere.
        :param default_input_max_characters: The maximum number of characters for input text.
        :param default_generation_max_output_tokens: The maximum number of tokens for text generation.
        :param default_generation_temperature: The temperature for text generation.
        """

        self.api_key = api_key

        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature

        self.generation_model_id = None

        self.embedding_model_id = None
        self.embedding_size = None

        self.enums = CoHereEnums
        
        self.client = cohere.ClientV2(
            api_key=self.api_key,
            )

        self.logger = logging.getLogger(__name__)
        
    def set_generation_model(self, model_id: str):
        """
        Set the generation model to be used.
        
        :param model_id: The ID of the model to be set.
        """
        self.generation_model_id = model_id
        self.logger.info(f"Generation model set to {model_id}")


    def set_embedding_model(self, model_id: str, embedding_size: int):
        """
        Set the embedding model to be used.
        
        :param model_id: The ID of the model to be set.
        :param embedding_size: The size of the embedding.
        """
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size
        self.logger.info(f"Embedding model set to {model_id} with size {embedding_size}")

    def process_text(self, text: str):
        """
        Process the input text to ensure it meets the requirements of the LLM.
        
        :param text: The input text to be processed.
        :return: The processed text.
        """
        return text[:self.default_input_max_characters].strip()
    

    def construct_prompt(self, prompt:str, role:str):
        """
        Construct a prompt based on the provided input and role.
        
        :param prompt: The input prompt.
        :param role: The role of the user (e.g., 'user', 'assistant').
        :return: The constructed prompt.
        """
        return {
            "role": role,
            "content": prompt
        }
    
    def generate_text(self, prompt: str, chat_history: list=[], max_output_tokens: int=None,
                        temperature: float = None):
        """
        Generate text based on the provided prompt and chat history.
        
        :param prompt: The input prompt for text generation.
        :param chat_history: The history of the chat (optional).
        :param max_output_tokens: The maximum number of tokens to generate (optional).
        :param temperature: The temperature for sampling (optional).
        :return: The generated text.
        """
        if not self.client:
            self.logger.error("CoHere client was not set")
            return None

        if not self.generation_model_id:
            self.logger.error("Generation model for CoHere was not set")
            return None
        

        max_output_tokens = max_output_tokens if max_output_tokens is not None else self.default_generation_max_output_tokens
        temperature = temperature if temperature is not None else self.default_generation_temperature

        chat_history.append(
            self.construct_prompt(prompt=prompt, role=CoHereEnums.USER.value)
            )

        response = self.client.chat(
            model=self.generation_model_id,
            messages=chat_history,
            max_tokens=max_output_tokens,
            temperature=temperature
        )

        if not response or not response.text:
            self.logger.error("Error while generating text with CoHere")
            return None

        return response.message.content[0].text
    

    def embed_text(self, text: Union[str,List[str]], document_type: str = None):
        """
        Embed the provided text into a vector representation.
        
        :param text: The input text to be embedded.
        :param document_type: The type of document (optional).
        :return: The embedded vector representation of the text.
        """
        if not self.client:
            self.logger.error("CoHere client was not set")
            return None
        
        if isinstance(text, str):
            text = [text]

        if not self.embedding_model_id:
            self.logger.error("Embedding model for CoHere was not set")
            return None

        input_type = CoHereEnums.DOCUMENT
        if document_type == CoHereEnums.QUERY:
            input_type = CoHereEnums.QUERY


        response = self.client.embed(
            model=self.embedding_model_id,
            texts=[self.process_text(t) for t in text],
            input_type= input_type,
            embedding_types=['float']
        )

        if not response or not response.embeddings or not response.embeddings.float:
            self.logger.error("Error while embedding text with CoHere")
            return None
        

        return [ f for f in response.embeddings.float ]
        