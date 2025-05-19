from ..LLMInterface import LLMInterface
from ..LLMEnums import CoHereEnums, DocumentTypeEnum
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

        self.client = cohere.Client(api_key=self.api_key)

        self.logger = logging.getLogger(__name__)
        
    