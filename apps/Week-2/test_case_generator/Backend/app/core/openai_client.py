from openai import OpenAI, OpenAIError
from typing import List, Dict
from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


class OpenAIClient:
    """Client for interacting with OpenAI API"""

    def __init__(self):
        """Initialize OpenAI client with API key from settings"""
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.temperature = settings.openai_temperature
        self.max_tokens = settings.openai_max_tokens
        logger.info(f"OpenAI client initialized with model: {self.model}")

    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = None,
        max_tokens: int = None,
    ) -> str:
        """
        Generate completion from OpenAI
        Args:
            messages: List of message dictionaries with role and content
            temperature: Sampling temperature (0-2). Higher = more random
            max_tokens: Maximum tokens to generate
        Returns:
            Generated text response
        Raises:
            Exception: If OpenAI API call fails
        """
        try:
            # Use provided parameters or fall back to defaults
            temp = temperature if temperature is not None else self.temperature
            tokens = max_tokens if max_tokens is not None else self.max_tokens

            logger.info(f"Sending request to OpenAI with {len(messages)} messages")
            logger.debug(
                f"Parameters: model={self.model}, temp={temp}, max_tokens={tokens}"
            )

            response = self.client.chat.completions.create(
                model=self.model, messages=messages, temperature=temp, max_tokens=tokens
            )

            content = response.choices[0].message.content

            # Log usage statistics
            if hasattr(response, "usage"):
                logger.info(
                    f"OpenAI usage - Prompt tokens: {response.usage.prompt_tokens}, "
                    f"Completion tokens: {response.usage.completion_tokens}, "
                    f"Total: {response.usage.total_tokens}"
                )

            logger.info("Successfully received response from OpenAI")
            return content

        except OpenAIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise Exception(f"OpenAI API error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error calling OpenAI: {str(e)}")
            raise Exception(f"Failed to generate completion: {str(e)}")


openai_client = OpenAIClient()
