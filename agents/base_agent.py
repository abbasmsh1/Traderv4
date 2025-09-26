import os
from typing import Optional
from mistralai import Mistral
from langchain.schema import SystemMessage
import dotenv
dotenv.load_dotenv()

class BaseAgent:
    """
    Base class for all agents.
    Provides a connection to the Mistral API and a generic method for generating responses.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "mistral-large-latest"):
        # Allow passing API key or fallback to environment; if missing, run in disabled mode
        api_key = api_key or os.getenv('MISTRAL_API_KEY')
        self.client = Mistral(api_key=api_key) if api_key else None
        self.model = model
        self.system_message: Optional[SystemMessage] = None

    def get_response(self, prompt: str, temperature: float = 0.7, max_tokens: int = 1024) -> str:
        """
        Send a prompt to the Mistral API and return the model response.
        """
        if self.client is None:
            return "LLM disabled: missing Mistral API key. Set MISTRAL_API_KEY to enable this agent."
        try:
            response = self.client.chat.complete(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_message.content if self.system_message else ""},
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating response: {e}"
