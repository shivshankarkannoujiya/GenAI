from openai import OpenAI
from app.config import get_settings


class OpenAIClient:

    def __init__(self):
        settings = get_settings()
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = "gpt-4o-mini"

    async def generate_completion(
        self, messages: list, temperature: float = 0.7
    ) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=2000,
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")


openai_client = OpenAIClient()
