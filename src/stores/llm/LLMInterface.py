from abc import ABC, abstractmethod

class LLMInterface(ABC):
    """
    Abstract base class for LLM (Large Language Model) interfaces.
    This class defines the methods that any LLM interface should implement.
    """

    @abstractmethod
    def set_generation_model(self, model_id: str):
        """
        Set the generation model to be used.
        
        :param model_id: The ID of the model to be set.
        """
        pass

    @abstractmethod
    def set_embedding_model(self, model_id: str, embeding_size: int):
        """
        Set the embedding model to be used.
        
        :param model_id: The ID of the model to be set.
        :param embeding_size: The size of the embedding.
        """
        pass

    @abstractmethod
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
        pass
    
    @abstractmethod
    def embed_text(self, text: str, document_type: str = None):
        """
        Embed the provided text into a vector representation.

        :param text: The input text to be embedded.
        :param document_type: The type of document (optional).
        :return: The embedded vector representation of the text.
        """
        pass

    @abstractmethod
    def construct_prompt(self, prompt: str, role: str):
        """
        Construct a prompt based on the provided input and role.

        :param prompt: The input prompt.
        :param role: The role of the user (e.g., 'user', 'assistant').
        :return: The constructed prompt.
        """
        pass