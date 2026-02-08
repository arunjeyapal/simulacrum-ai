# src/simulacrum/core/llm.py

import os
from typing import List, Dict, Any, Optional
import litellm
from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class LLMEngine:
    def __init__(self, model_name: str = "openai/gpt-3.5-turbo"):
        """
        Initialize the engine.
        
        :param model_name: The model identifier.
                           Examples: 
                           - "gemini/gemini-1.5-flash" (Fast/Cheap)
                           - "gpt-4o" (High Intelligence)
                           - "ollama/llama3" (Local/Privacy)
        """
        self.model_name = model_name

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
        """
        A robust wrapper around litellm.completion with retries.
        """
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            response = litellm.completion(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                # Safety settings for Gemini to prevent blocking valid simulation scenarios
                safety_settings=[
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                ] if "gemini" in self.model_name else None
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            # As an Architect, we want detailed logs when the 'Brain' fails
            print(f"Error generating response from {self.model_name}: {e}")
            raise e
