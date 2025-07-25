from time import time
from google import genai
from google.genai import types
import math

class GoogleModel:
    def __init__(self, model_name : str, api_key: str, **kwargs):
        try:
            self.client = genai.Client(api_key=api_key)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Google GenAI client: {e}")
        self.model_name = model_name

    def generate_response(self, prompt: str, **params) -> dict[str, str]:
        print(params)
        generation_config = types.GenerationConfig(**params)
        print(generation_config)
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=generation_config,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to generate content: {e}")
        
        if not response or not response.candidates:
            raise RuntimeError("No candidates returned from generation.")
        
        candidate_response = "".join(part.text for part in response.candidates[0].content.parts)
    
        return {
            "response" : candidate_response,
            "usage_metadata" : {
                "prompt_token_count" : response.usage_metadata.prompt_token_count,
                "candidates_token_count" : response.usage_metadata.candidates_token_count,
                "total_tokens_count" : response.usage_metadata.total_token_count,
            }
        }





