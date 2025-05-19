from ..LLMInterface import LLMInterface
from ..LLMEnums import CoHereEnums, DocumentTypeEnum
import cohere
import logging

class CoHereProvider(LLMInterface):
    def __init__(self,api_key: str,api_url: str,
                    default_input_max_characters: int=1000,
                    default_generation_max_output_tokens: int=1000,
                    default_generation_temperature: float=0.1):
        """
        Initialize the CoHereProvider with the given API key and default parameters.
        
        :param api_key: The API key for CoHere.
        :param api_url: The API URL for CoHere.
        :param default_input_max_characters: The maximum number of characters for input text.
        :param default_generation_max_output_tokens: The maximum number of tokens for text generation.
        :param default_generation_temperature: The temperature for text generation.
        """

        self.api_key = api_key
        self.api_url = api_url

        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature

        self.generation_model_id = None

        self.embedding_model_id = None
        self.embedding_size = None

        self.client = cohere.ClientV2(
            api_key=self.api_key,
            api_url=self.api_url
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

    