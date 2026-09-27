# db.py
import os
import uuid
import requests
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "qdrant")
EMBED_PORT = 8081  # separate llama-server instance running embed.gguf (qwen 0.6b)


def get_client(path: str = DB_PATH) -> QdrantClient:
    return QdrantClient(path=path)


def embed(text: str, port: int = EMBED_PORT) -> list[float]:
    resp = requests.post(
        f"http://localhost:{port}/v1/embeddings",
        json={"input": text},
        timeout=30,
    )
    return resp.json()["data"][0]["embedding"]


def ensure_collection(client: QdrantClient, name: str, dim: int) -> None:
    if not client.collection_exists(name):
        client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
        )


def store(
    client: QdrantClient,
    collection: str,
    texts: list[str],
    metadatas: list[dict] | None = None,
) -> list[str]:
    metadatas = metadatas or [{} for _ in texts]
    vectors = [embed(t) for t in texts]
    ensure_collection(client, collection, dim=len(vectors[0]))
    ids = [str(uuid.uuid4()) for _ in texts]
    points = [
        PointStruct(id=ids[i], vector=vectors[i], payload={"text": texts[i], **metadatas[i]})
        for i in range(len(texts))
    ]
    client.upsert(collection_name=collection, points=points)
    return ids


def retrieve(
    client: QdrantClient,
    collection: str,
    query: str,
    top_k: int = 5,
) -> list[dict]:
    vec = embed(query)
    result = client.query_points(collection_name=collection, query=vec, limit=top_k)
    return [
        {"text": p.payload.get("text"), "score": p.score, "metadata": p.payload}
        for p in result.points
    ]

# db.py — append only
_default_client = None

def get_default_client() -> QdrantClient:
    global _default_client
    if _default_client is None:
        _default_client = get_client()
    return _default_client

def store_default(collection: str, texts: list[str]) -> list[str]:
    return store(get_default_client(), collection, texts)

def retrieve_default(collection: str, query: str, top_k: int = 5) -> list[dict]:
    return retrieve(get_default_client(), collection, query, top_k)

from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue

def remember(client, collection, key, value):
    """Store one key-value memory pair. Key is embedded for fuzzy lookup; value is stored verbatim."""
    return store(client, collection, [key], [{"key": key, "text": value}])[0]

def recall_exact(client, collection, key):
    """Exact-string key match. Returns value or None."""
    if not client.collection_exists(collection):
        return None
    points, _ = client.scroll(
        collection_name=collection,
        scroll_filter=Filter(must=[FieldCondition(key="key", match=MatchValue(value=key))]),
        limit=1,
    )
    return points[0].payload.get("text") if points else None

def recall_fuzzy(client, collection, query, top_k=1):
    """Vector-similarity recall — matches by meaning, not exact string."""
    return retrieve(client, collection, query, top_k)

def forget(client, collection, key):
    """Delete all entries with exact key match. Returns count deleted."""
    if not client.collection_exists(collection):
        return 0
    points, _ = client.scroll(
        collection_name=collection,
        scroll_filter=Filter(must=[FieldCondition(key="key", match=MatchValue(value=key))]),
        limit=1000,
    )
    if not points:
        return 0
    ids = [p.id for p in points]
    client.delete(collection_name=collection, points_selector=ids)
    return len(ids)

def remember_default(key, value, collection="memory"):
    return remember(get_default_client(), collection, key, value)

def recall_exact_default(key, collection="memory"):
    return recall_exact(get_default_client(), collection, key)

def recall_fuzzy_default(query, collection="memory", top_k=1):
    return recall_fuzzy(get_default_client(), collection, query, top_k)

def forget_default(key, collection="memory"):
    return forget(get_default_client(), collection, key)