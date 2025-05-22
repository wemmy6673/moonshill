from abc import ABC, abstractmethod
from typing import List, Optional
import openai
from google import genai
from google.genai import types
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import traceback
from services.logging import init_logger
from config.settings import get_settings
from schemas.generation import LLMProviderError

logger = init_logger()
settings = get_settings()


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""

    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from the LLM"""
        pass

    @abstractmethod
    async def get_embeddings(self, text: str) -> List[float]:
        """Get embeddings for text"""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI implementation of LLMProvider"""

    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview", system_instruction:  Optional[str] = None):
        try:
            self.api_key = api_key
            self.model = model
            self.system_instruction = system_instruction
            openai.api_key = api_key
            self.client = openai.AsyncOpenAI(api_key=api_key)
            logger.info(f"Initialized OpenAIProvider with model: {model}")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAIProvider: {str(e)}")
            raise LLMProviderError(f"OpenAI initialization failed: {str(e)}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((openai.APIError, openai.APITimeoutError))
    )
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from OpenAI"""
        try:
            logger.debug(f"Generating text with OpenAI model: {self.model}")
            logger.debug(f"Prompt: {prompt[:100]}...")  # Log first 100 chars of prompt

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_instruction},
                    {"role": "user", "content": prompt}
                ],
                temperature=kwargs.get('temperature', 0.7),
                max_tokens=kwargs.get('max_tokens', 500),
                top_p=kwargs.get('top_p', 1.0),
                frequency_penalty=kwargs.get('frequency_penalty', 0.0),
                presence_penalty=kwargs.get('presence_penalty', 0.0)
            )

            generated_text = response.choices[0].message.content
            logger.debug(f"Generated text: {generated_text[:100]}...")  # Log first 100 chars
            return generated_text

        except openai.APIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise LLMProviderError(f"OpenAI API error: {str(e)}")
        except openai.APITimeoutError as e:
            logger.error(f"OpenAI timeout error: {str(e)}")
            raise LLMProviderError(f"OpenAI timeout error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected OpenAI generation error: {str(e)}\n{traceback.format_exc()}")
            raise LLMProviderError(f"Unexpected error in OpenAI generation: {str(e)}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((openai.APIError, openai.APITimeoutError))
    )
    async def get_embeddings(self, text: str) -> List[float]:
        """Get embeddings from OpenAI"""
        try:
            logger.debug(f"Getting embeddings for text: {text[:100]}...")

            response = await self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )

            embeddings = response.data[0].embedding
            logger.debug(f"Generated embeddings of length: {len(embeddings)}")
            return embeddings

        except openai.APIError as e:
            logger.error(f"OpenAI API error in embeddings: {str(e)}")
            raise LLMProviderError(f"OpenAI API error in embeddings: {str(e)}")
        except openai.APITimeoutError as e:
            logger.error(f"OpenAI timeout error in embeddings: {str(e)}")
            raise LLMProviderError(f"OpenAI timeout error in embeddings: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected OpenAI embeddings error: {str(e)}\n{traceback.format_exc()}")
            raise LLMProviderError(f"Unexpected error in OpenAI embeddings: {str(e)}")


class GeminiProvider(LLMProvider):
    """Gemini implementation of LLMProvider"""

    def __init__(self, api_key: str, model: str = "gemini-pro", system_instruction:  Optional[str] = None):
        self.api_key = api_key
        self.model = model
        self.system_instruction = system_instruction
        genai.configure(api_key=api_key)
        self.client = genai.Client(api_key=self.api_key)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from Gemini"""
        try:
            messages = [
                types.UserContent(parts=[types.Part.from_text(prompt)])
            ]

            result = self.client.models.generate_content(
                model=self.model,
                contents=messages,
                generation_config=types.GenerationConfig(
                    temperature=kwargs.get('temperature', 0.7),
                    max_output_tokens=kwargs.get('max_tokens', 500),
                    top_p=kwargs.get('top_p', 1.0),
                    top_k=kwargs.get('top_k', 40),
                    candidate_count=1,
                    system_instruction=self.system_instruction
                )
            )
            return result.text
        except Exception as e:
            logger.error(f"Gemini generation error: {str(e)}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def get_embeddings(self, text: str) -> List[float]:
        """Get embeddings from Gemini"""
        try:
            result = self.client.models.embed_content(
                model="gemini-embedding-exp-03-07",
                content=text
            )
            return result.embeddings
        except Exception as e:
            logger.error(f"Gemini embeddings error: {str(e)}")
            raise
