from time import time
from google import genai
from google.genai import types
import dotenv
import time
import pandas as pd
from reasoning.task import Task
class Model:
    def __init__(self, name: str, **kwargs):
        self.name = name
        self.__dict__.update(kwargs)

    def generate_response(self, prompt: str, **params) -> dict[str, str]:
        raise NotImplementedError("This method should be implemented by subclasses.")


class GoogleModel(Model):
    def __init__(self, name : str, **kwargs):
        super().__init__(name, metadata_columns=["template", "domain", "instance", "num_requests", "prompt_token_count", "candidates_token_count", "total_tokens_count"], **kwargs)
        try:
            dotenv.load_dotenv()
            api_key = dotenv.get_key(dotenv.find_dotenv(), "GOOGLE_API_KEY")
            if api_key is None:
                raise ValueError("GOOGLE_API_KEY not found in environment variables.")
            self.client = genai.Client(api_key=api_key)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Google GenAI client: {e}")

    def generate_response(self, prompt: str, wait_time: int = 0, **params) -> dict[str, str]:
        generation_config = types.GenerateContentConfig(**params)
        chances = 3
        generated = False
        num_requests = 0
        metadata = {}
        text = ""
        thought = ""
        while chances > 0 and not generated:
            chances -= 1
            try:
                num_requests += 1
                response = self.client.models.generate_content(
                    model=self.name,
                    contents=prompt,
                    config=generation_config,
                )
                if  response and \
                    response.candidates and \
                    response.candidates[0] and \
                    response.candidates[0].content and \
                    response.candidates[0].content.parts:
                        for part in response.candidates[0].content.parts:
                            if not part.text:
                                continue
                            elif part.thought:
                                thought = part.text
                            else:
                                text += part.text
    
                        metadata = {            
                            "num_requests" : num_requests,
                            "prompt_token_count" : response.usage_metadata.prompt_token_count,
                            "candidates_token_count" : response.usage_metadata.candidates_token_count,
                            "total_tokens_count" : response.usage_metadata.total_token_count,
                        }
                        if text: generated = True

            except Exception as e:
                if wait_time == 0:
                    wait_time = 1
                # Exponential backoff
                wait_time *= 2
            finally:
                if wait_time > 0:
                    time.sleep(wait_time)

        if not generated:
            raise RuntimeError("Error generating response.")
        
        data = {
            "response": text,
            "metadata": metadata,
        }
        if thought:
            data["thought"] = thought
        return data

        # print(response)


# from transformers import (
#     AutoTokenizer,
#     AutoModelForCausalLM,
#     BitsAndBytesConfig,
#     TrainingArguments,
#     Trainer,
#     DataCollatorForLanguageModeling,
# )
# import torch
# class QwenModel(Model):
#     def __init__(self, name: str, **kwargs):
#         super().__init__(name, **kwargs)

#         dotenv.load_dotenv()
#         api_key = dotenv.get_key(dotenv.find_dotenv(), "HUGGINGFACE_TOKEN")
#         if api_key is None:
#             raise ValueError("HUGGINGFACE_TOKEN not found in environment variables.")

#         # load tokenizer
#         try:
#             self.tokenizer = AutoTokenizer.from_pretrained(self.name, trust_remote_code=True, token=api_key)

#         except Exception as e:
#             raise RuntimeError(f"Failed to load tokenizer: {e}")
#         # load model
#         try:
#             self.model = AutoModelForCausalLM.from_pretrained(
#                 pretrained_model_name_or_path=self.name,
#                 trust_remote_code=True,
#                 token=api_key,
#                 **kwargs
#             )
#         except Exception as e:
#             raise RuntimeError(f"Failed to load model: {e}")

#     def generate_response(self, prompt: str, enable_thinking: bool, **params) -> dict[str, str]:
#         messages = [{"role": "user", "content": prompt}]
#         text = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True, enable_thinking=enable_thinking)
#         input_ids = self.tokenizer(text, return_tensors="pt")
#         generated_ids = self.model.generate(
#             **input_ids,
#             **params
#         )
#         output_ids = generated_ids[0][len(input_ids.input_ids[0]):].tolist()
#         try:
#             # rindex finding 151668 (</think>)
#             index = len(output_ids) - output_ids[::-1].index(151668)
#         except ValueError:
#             index = 0
        
#         thinking_content = self.tokenizer.decode(output_ids[:index], skip_special_tokens=True)
#         response_content = self.tokenizer.decode(output_ids[index:], skip_special_tokens=True)

#         return {
#             "response": response_content,
#             "metadata": {
#                 "input_tokens" : len(input_ids.input_ids[0]),
#                 "output_tokens" : len(output_ids),
#                 "thinking_tokens" : len(output_ids[:index]),
#                 "response_tokens" : len(output_ids[index:]),
#                 "enable_thinking": enable_thinking
#             }
#         }

def get_model_from_model_config(**model_config) -> Model:
    model_class = model_config.pop("class", None)
    if model_class is None:
        raise ValueError("class must be specified in model_config.")
    if model_class == "GoogleModel":
        return GoogleModel(**model_config)
    # elif model_class == "QwenModel":
    #     return QwenModel(**model_config)
    else:
        raise ValueError(f"Unknown class: {model_class}")

