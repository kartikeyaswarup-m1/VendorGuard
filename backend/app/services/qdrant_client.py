from qdrant_client import QdrantClient
from ..config import QDRANT_URL, QDRANT_API_KEY, EMBEDDING_DIM

class QdrantClientWrapper:
    def __init__(self, collection_name="vendor_chunks"):
        self.client = None
        self.collection_name = collection_name
        self._initialized = False

    def _get_client(self):
        """Lazy initialization of Qdrant client"""
        if self.client is None:
            try:
                self.client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
                self._ensure_collection()
                self._initialized = True
            except Exception as e:
                raise RuntimeError(f"Failed to connect to Qdrant: {str(e)}")
        return self.client

    def _ensure_collection(self):
        try:
            info = self.client.get_collection(self.collection_name)
            current_size = getattr(getattr(info.config, "params", None), "vectors", None)
            current_size = getattr(current_size, "size", None)
            if current_size and current_size != EMBEDDING_DIM:
                # Dimension drift detected; recreate with the expected dimension
                self.client.recreate_collection(
                    collection_name=self.collection_name,
                    vectors_config={"size": EMBEDDING_DIM, "distance": "Cosine"}
                )
                return
        except Exception:
            pass

        try:
            existing = [c.name for c in self.client.get_collections().collections]
        except Exception:
            existing = []
        if self.collection_name not in existing:
            self.client.recreate_collection(
                collection_name=self.collection_name,
                vectors_config={"size": EMBEDDING_DIM, "distance": "Cosine"}
            )

    def upsert_points(self, points):
        client = self._get_client()
        client.upsert(collection_name=self.collection_name, points=points)

    def search(self, query_vector, limit=10, with_payload=True, vendor_id=None, score_threshold=0.3):
        """
        Search for similar vectors with optional filtering.
        
        Args:
            query_vector: The query vector to search for
            limit: Maximum number of results
            with_payload: Whether to include payload
            vendor_id: Filter by vendor_id
            score_threshold: Minimum similarity score (0.0-1.0 for cosine similarity)
                            Higher values = more strict (only very similar results)
        """
        client = self._get_client()
        query_filter = None
        if vendor_id:
            from qdrant_client.models import Filter, FieldCondition, MatchValue
            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="vendor_id",
                        match=MatchValue(value=vendor_id)
                    )
                ]
            )
        res = client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=limit,
            with_payload=with_payload,
            query_filter=query_filter,
            score_threshold=score_threshold
        )
        return res.points

    def get_point(self, point_id):
        client = self._get_client()
        return client.retrieve(collection_name=self.collection_name, ids=[point_id])
