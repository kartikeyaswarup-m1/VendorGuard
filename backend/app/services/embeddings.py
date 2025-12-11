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
                    embeddings.append(embedding_values)
                else:
                    raise ValueError("No embeddings in response")
            except Exception as e:
                print(f"Error generating embedding: {e}")
                # Fallback to hash-based embedding on error
                h = abs(hash(text)) % (10**8)
                v = [((h >> (i*8)) & 255) / 255.0 for i in range(EMBEDDING_DIM)]
                embeddings.append(v)
        return embeddings
    else:
        # Local deterministic fallback embeddings (not production-grade)
        vectors = []
        for t in texts:
            h = abs(hash(t)) % (10**8)
            v = [((h >> (i*8)) & 255) / 255.0 for i in range(EMBEDDING_DIM)]
            vectors.append(v)
        return vectors
