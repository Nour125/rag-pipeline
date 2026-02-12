from __future__ import annotations

from dataclasses import dataclass
from typing import List

import numpy as np
from openai import OpenAI


EMBED_MODEL_ID = "text-embedding-nomic-embed-text-v1.5" # LM Studio embedding model


def get_lmstudio_client() -> OpenAI:
    """
    Creates and returns an OpenAI client configured to connect to the LM Studio API.
    """
    client = OpenAI(
        base_url="http://localhost:1234/v1",
        api_key="lm-studio",  # LM 
    )
    return client


@dataclass
class EmbeddingConfig:
    model: str = EMBED_MODEL_ID


class LMStudioEmbedder:
    """
    Wrapper for LM Studio Embeddings endpoint.
    Uses the model 'text-embedding-nomic-embed-text-v1.5'.
    """

    def __init__(self, config: EmbeddingConfig | None = None) -> None:
        self.config = config or EmbeddingConfig()
        self.client = get_lmstudio_client()

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Embeds a list of texts and returns a NumPy array of shape (n_texts, dim).
        """
        if not texts:
            return np.zeros((0, 0), dtype="float32")

        response = self.client.embeddings.create(
            model=self.config.model,
            input=texts,
        )

        # 
        vectors = [item.embedding for item in response.data]
        return np.array(vectors, dtype="float32")

    def embed_text(self, text: str) -> np.ndarray:
        """
        Embeds a single text and returns a NumPy array of shape (dim,).
        """
        arr = self.embed_texts([text])
        return arr[0]
