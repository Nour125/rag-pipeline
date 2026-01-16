from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from openai import OpenAI

def get_lmstudion_client() -> OpenAI:
    return OpenAI(base_url="http://localhost:1234/v1", api_key="")

@dataclass
class LLMConfig:
    model:str = "qwen/qwen3-vl-4b" # "openai/gpt-oss-20b" 
    temperature:float = 0.2
    max_tokens:int = 2048 

class LMStudioChatLLM:
    def __init__(self, config: Optional[LLMConfig] = None) -> None:
        self.client = get_lmstudion_client()
        self.config = config or LLMConfig()

    def chat(self, messages: List[Dict[str, str]]) -> str:
        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )
        return response.choices[0].message.content.strip()
    def getName(self) -> str:
        return self.config["model"]