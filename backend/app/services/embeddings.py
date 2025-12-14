import math
import hashlib
from ..config import EMBEDDING_PROVIDER, GOOGLE_API_KEY, EMBEDDING_DIM, GEMINI_EMBEDDING_MODEL

# Lazy initialization function
def _get_genai_client():
    """Lazy initialization of Gemini client for embeddings"""
    if EMBEDDING_PROVIDER == "gemini" and GOOGLE_API_KEY:
        try:
            from google import genai
            client = genai.Client(api_key=GOOGLE_API_KEY)
            return client
        except Exception as e:
            print(f"Failed to initialize Gemini client for embeddings: {e}")
            return None
    return None

def embed_texts(texts):
    """
    Returns list[list[float]] embeddings.
    """
    def _fold_to_dim(vec, target_dim: int):
        """Deterministically fold a larger embedding down to target_dim.

        This preserves the configured Qdrant vector size even if the provider
        returns a higher-dimensional vector (e.g., 3072).
        """
        out = [0.0] * target_dim
        counts = [0] * target_dim
        for i, v in enumerate(vec):
            j = i % target_dim
            out[j] += float(v)
            counts[j] += 1
        for j in range(target_dim):
            if counts[j]:
                out[j] /= counts[j]
        return out

    def _enforce_dim(vec):
        if vec is None:
            return None
        if len(vec) != EMBEDDING_DIM:
            # If the provider returns a larger vector, fold it down to the configured size.
            # This keeps Qdrant schema stable (e.g., fixed at 768) across provider changes.
            if len(vec) > EMBEDDING_DIM:
                return _fold_to_dim(vec, EMBEDDING_DIM)
            raise ValueError(
                f"Embedding dimension mismatch: got {len(vec)}, expected {EMBEDDING_DIM}. "
                "Provider returned a smaller vector than configured; update EMBEDDING_DIM or the embedding model."
            )
        return vec

    def _deterministic_fallback(text: str):
        # Stable SHA256-based fallback; tile digest to required dimension and normalize to [0,1]
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        needed_bytes = EMBEDDING_DIM
        repeated = (digest * math.ceil(needed_bytes / len(digest)))[:needed_bytes]
        return [b / 255.0 for b in repeated]

    if EMBEDDING_PROVIDER == "gemini":
        client = _get_genai_client()
        if client is not None:
            embeddings = []
            for text in texts:
                try:
                    # Use the models.embed_content method
                    response = client.models.embed_content(
                        model=GEMINI_EMBEDDING_MODEL,
                        contents=text
                    )
                    # The response has an embeddings list, each with values
                    if response.embeddings and len(response.embeddings) > 0:
                        # Get the first embedding's values
                        embedding_values = response.embeddings[0].values
                        embeddings.append(_enforce_dim(embedding_values))
                    else:
                        raise ValueError("No embeddings in response")
                except Exception as e:
                    print(f"Error generating embedding: {e}")
                    embeddings.append(_deterministic_fallback(text))
            return embeddings
    
    # Local deterministic fallback embeddings (not production-grade)
    vectors = []
    for t in texts:
        vectors.append(_deterministic_fallback(t))
    return vectors
