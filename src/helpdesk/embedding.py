from functools import lru_cache

from sentence_transformers import SentenceTransformer
import numpy as np

MODEL_NAME = "BAAI/bge-small-en-v1.5"

"""load the model from sentence-transformers"""
@lru_cache(maxsize=4)
def load_model(model_name: str = MODEL_NAME):
    return SentenceTransformer(model_name)



def embed(model: SentenceTransformer, texts: list[str])->np.ndarray:
    """embed the text using the model"""
    return model.encode(texts, convert_to_numpy=True, show_progress_bar=True)