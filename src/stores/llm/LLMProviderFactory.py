from .LLMEnums import LLMEnums
from providers import OpenAIProvider, CoHereProvider

class LLMProviderFactory:
    def __init__(self, config: dict):
        """
        Initializes the LLMProviderFactory with a configuration dictionary.

        :param config: A dictionary containing configuration settings for the LLM provider.
        """
        self.config = config

    def create(self, provider: str):
        """
        Creates an instance of the specified LLM provider.

        :param provider: The name of the LLM provider to create.
        :return: An instance of the specified LLM provider.
        :raises ValueError: If the provider is not recognized.
        """
        if provider == LLMEnums.OPENAI.value:
            return OpenAIProvider(
                api_key = self.config.OPENAI_API_KEY,
                api_url = self.config.OPENAI_API_URL,
                default_input_max_characters=self.config.INPUT_DAFAULT_MAX_CHARACTERS,
                default_generation_max_output_tokens=self.config.GENERATION_DAFAULT_MAX_TOKENS,
                default_generation_temperature=self.config.GENERATION_DAFAULT_TEMPERATURE
            
            )
        if provider == LLMEnums.COHERE.value:
            return CoHereProvider(
                api_key = self.config.COHERE_API_KEY,
                api_url = self.config.COHERE_API_URL,
                default_input_max_characters=self.config.INPUT_DAFAULT_MAX_CHARACTERS,
                default_generation_max_output_tokens=self.config.GENERATION_DAFAULT_MAX_TOKENS,
                default_generation_temperature=self.config.GENERATION_DAFAULT_TEMPERATURE
            )
        
        return None
        