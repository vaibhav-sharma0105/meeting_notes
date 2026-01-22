from typing import List, Dict, Any
import numpy as np
from litellm import embedding
from sklearn.cluster import AgglomerativeClustering
from core.config import settings

def generate_embedding(text: str) -> List[float]:
    """
    Generates an embedding vector for the given text using LiteLLM.
    """
    # In a real scenario, we get the specific embedding model from config
    # For now, we assume the user might have defined it or we default
    config = settings.get_llm_config()
    # Explicitly reload to get latest runtime updates if needed, though settings object usually caches
    # For MVP, accessing _config directly is fine as it's updated in settings router
    model_name = settings._config.get("embedding_model", "openai/text-embedding-3-small")

    try:
        response = embedding(
            model=model_name,
            input=[text],
            api_key=config.get("api_key"),
            api_base=config.get("api_base")
        )
        return response['data'][0]['embedding']
    except Exception as e:
        print(f"Error generating embedding: {e}")
        # Return a dummy vector for dev/test if strictly needed, or re-raise
        # For now, re-raise so the user knows configuration is wrong
        raise e

def cluster_meetings(embeddings: List[List[float]], distance_threshold: float = 0.5) -> List[int]:
    """
    Clusters embeddings to identify common projects/topics.
    Returns a list of cluster labels corresponding to the input list.
    -1 indicates noise or unclustered (if using DBSCAN, but Agglomerative forces clusters or distance).
    """
    if not embeddings:
        return []

    X = np.array(embeddings)
    if len(X) < 2:
        return [0] * len(X)

    # Agglomerative Clustering with distance threshold
    # n_clusters=None means we rely on distance_threshold
    clustering = AgglomerativeClustering(
        n_clusters=None,
        distance_threshold=distance_threshold,
        metric='cosine',
        linkage='average'
    )

    labels = clustering.fit_predict(X)
    return labels.tolist()
