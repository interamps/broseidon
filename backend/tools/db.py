"""
tools/db.py — Database tool layer for Broseidon.

Backends:
  - Embedding : llama-cpp-python  (Qwen3-Embedding-0.6B-Q8_0, GPU-first)
  - Vector    : FAISS (GPU-first, hot-cache) + Qdrant (local embedded, persistent)
  - SQL       : SQLite  (database/broseidon.db)  — schema defined later
  - Markdown  : database/ (temporary) | soul/ (permanent)

Every public function in this file is registered as a Gemini tool automatically
by tools/__init__.py.
"""

from __future__ import annotations

import json
import logging
import shutil
import sqlite3
import warnings
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Paths — all derived from this file's location, never hardcoded strings
# ---------------------------------------------------------------------------
_TOOLS_DIR   = Path(__file__).resolve().parent          # backend/tools/
_BACKEND_DIR = _TOOLS_DIR.parent                        # backend/
_MODELS_DIR  = _BACKEND_DIR / "models"
_DB_DIR      = _BACKEND_DIR / "database"
_SOUL_DIR    = _BACKEND_DIR / "soul"

_EMBED_MODEL_PATH = _MODELS_DIR / "embed.gguf"
_SQLITE_PATH      = _DB_DIR / "broseidon.db"
_FAISS_INDEX_PATH = _DB_DIR / "faiss.index"
_FAISS_MAP_PATH   = _DB_DIR / "faiss_map.json"   # id→text mapping
_QDRANT_PATH      = _DB_DIR / "qdrant"

# Ensure runtime directories exist
_DB_DIR.mkdir(parents=True, exist_ok=True)
_SOUL_DIR.mkdir(parents=True, exist_ok=True)
_QDRANT_PATH.mkdir(parents=True, exist_ok=True)

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Embedding — llama-cpp-python only, embedding=True, NO inference
# ---------------------------------------------------------------------------
_llama_model: Any = None   # lazy singleton


def _get_llama() -> Any:
    """Return a cached Llama embedding model (GPU-first, CPU fallback)."""
    global _llama_model
    if _llama_model is not None:
        return _llama_model

    try:
        from llama_cpp import Llama  # type: ignore

        try:
            _llama_model = Llama(
                model_path=str(_EMBED_MODEL_PATH),
                embedding=True,
                n_gpu_layers=-1,   # offload everything to GPU
                verbose=False,
            )
            log.info("Embedding model loaded on GPU.")
        except Exception as gpu_err:
            warnings.warn(
                f"GPU loading failed ({gpu_err}); falling back to CPU for embeddings.",
                RuntimeWarning,
                stacklevel=2,
            )
            _llama_model = Llama(
                model_path=str(_EMBED_MODEL_PATH),
                embedding=True,
                n_gpu_layers=0,    # CPU only
                verbose=False,
            )
            log.warning("Embedding model loaded on CPU (fallback).")

    except ImportError as e:
        raise RuntimeError(
            "llama-cpp-python is required for embeddings. "
            "Install with: pip install llama-cpp-python"
        ) from e

    return _llama_model


def get_embedding(text: str) -> list[float]:
    """Generate a vector embedding for *text* using the local Qwen3 embedding model.

    Args:
        text: The input text to embed.

    Returns:
        A list of floats representing the embedding vector.
    """
    model = _get_llama()
    result = model.embed(text)
    # llama-cpp returns either a flat list or a list-of-lists
    if result and isinstance(result[0], list):
        return result[0]
    return list(result)


# ---------------------------------------------------------------------------
# FAISS — GPU-first, hot-cache for nearest-neighbour search
# ---------------------------------------------------------------------------
_faiss_index: Any = None
_faiss_map: dict[int, str] = {}   # internal_id → original text
_EMBED_DIM = 1024   # Qwen3-Embedding-0.6B output dimension


def _get_faiss_index() -> Any:
    """Return the FAISS index, loading from disk if it exists, else creating new."""
    global _faiss_index, _faiss_map
    if _faiss_index is not None:
        return _faiss_index

    try:
        import faiss  # type: ignore
    except ImportError as e:
        raise RuntimeError(
            "faiss is required. Install faiss-gpu or faiss-cpu."
        ) from e

    # Load persisted map
    if _FAISS_MAP_PATH.exists():
        with open(_FAISS_MAP_PATH, "r", encoding="utf-8") as f:
            raw = json.load(f)
            _faiss_map = {int(k): v for k, v in raw.items()}

    # Load or build index
    if _FAISS_INDEX_PATH.exists():
        idx = faiss.read_index(str(_FAISS_INDEX_PATH))
    else:
        idx = faiss.IndexFlatL2(_EMBED_DIM)

    # Prefer GPU
    try:
        if faiss.get_num_gpus() > 0:
            res = faiss.StandardGpuResources()
            idx = faiss.index_cpu_to_gpu(res, 0, idx)
            log.info("FAISS running on GPU.")
        else:
            log.warning("No FAISS GPUs found, using CPU.")
    except Exception as gpu_err:
        log.warning("FAISS GPU init failed (%s); using CPU.", gpu_err)

    _faiss_index = idx
    return _faiss_index


def _save_faiss() -> None:
    """Persist the FAISS index and id→text map to disk."""
    import faiss  # type: ignore

    idx = _faiss_index
    if idx is None:
        return
    # If on GPU, move back to CPU before saving
    try:
        idx = faiss.index_gpu_to_cpu(idx)
    except Exception:
        pass
    faiss.write_index(idx, str(_FAISS_INDEX_PATH))
    with open(_FAISS_MAP_PATH, "w", encoding="utf-8") as f:
        json.dump(_faiss_map, f)


def faiss_upsert(id: int, text: str) -> None:
    """Insert or update a vector in the FAISS hot-cache index.

    Args:
        id: Integer identifier for this vector entry.
        text: The text whose embedding will be stored.
    """
    import numpy as np  # type: ignore

    idx = _get_faiss_index()
    vec = get_embedding(text)
    arr = np.array([vec], dtype="float32")
    idx.add(arr)  # type: ignore[attr-defined]
    _faiss_map[id] = text
    _save_faiss()


def faiss_search(query: str, top_k: int = 5) -> list[dict]:
    """Search the FAISS index for the *top_k* nearest neighbours to *query*.

    Args:
        query: The query text to search for.
        top_k: Number of nearest results to return.

    Returns:
        List of dicts with keys 'id', 'text', 'distance'.
    """
    import numpy as np  # type: ignore

    idx = _get_faiss_index()
    vec = get_embedding(query)
    arr = np.array([vec], dtype="float32")
    distances, indices = idx.search(arr, top_k)  # type: ignore[attr-defined]

    results = []
    for dist, i in zip(distances[0], indices[0]):
        if i == -1:
            continue
        results.append({"id": int(i), "text": _faiss_map.get(int(i), ""), "distance": float(dist)})
    return results


# ---------------------------------------------------------------------------
# Qdrant — persistent, named-collection vector store (local embedded mode)
# ---------------------------------------------------------------------------
_qdrant_client: Any = None
_QDRANT_VECTOR_SIZE = 1024   # must match embedding dimension


def _get_qdrant() -> Any:
    """Return a cached Qdrant client in local/embedded mode."""
    global _qdrant_client
    if _qdrant_client is not None:
        return _qdrant_client

    try:
        from qdrant_client import QdrantClient  # type: ignore
    except ImportError as e:
        raise RuntimeError(
            "qdrant-client is required. Install with: pip install qdrant-client"
        ) from e

    _qdrant_client = QdrantClient(path=str(_QDRANT_PATH))
    log.info("Qdrant client initialised at %s", _QDRANT_PATH)
    return _qdrant_client


def _ensure_qdrant_collection(client: Any, collection: str) -> None:
    """Create a Qdrant collection if it does not already exist."""
    from qdrant_client.models import Distance, VectorParams  # type: ignore

    existing = [c.name for c in client.get_collections().collections]
    if collection not in existing:
        client.create_collection(
            collection_name=collection,
            vectors_config=VectorParams(size=_QDRANT_VECTOR_SIZE, distance=Distance.COSINE),
        )
        log.info("Qdrant collection '%s' created.", collection)


def qdrant_upsert(collection: str, id: str, text: str, metadata: dict | None = None) -> None:
    """Insert or update a vector in a Qdrant collection.

    Args:
        collection: Name of the Qdrant collection.
        id: Unique string identifier for this point.
        text: The text whose embedding will be stored.
        metadata: Optional extra key/value payload to attach.
    """
    from qdrant_client.models import PointStruct  # type: ignore

    client = _get_qdrant()
    _ensure_qdrant_collection(client, collection)
    vec = get_embedding(text)
    payload = {"text": text, **(metadata or {})}
    client.upsert(
        collection_name=collection,
        points=[PointStruct(id=id, vector=vec, payload=payload)],
    )


def qdrant_search(collection: str, query: str, top_k: int = 5) -> list[dict]:
    """Search a Qdrant collection for the nearest neighbours to *query*.

    Args:
        collection: Name of the Qdrant collection to search.
        query: The query text to search for.
        top_k: Number of nearest results to return.

    Returns:
        List of dicts with keys 'id', 'score', 'text', and any extra payload fields.
    """
    client = _get_qdrant()
    _ensure_qdrant_collection(client, collection)
    vec = get_embedding(query)
    hits = client.search(collection_name=collection, query_vector=vec, limit=top_k)
    return [
        {"id": h.id, "score": h.score, **h.payload}
        for h in hits
    ]


# ---------------------------------------------------------------------------
# SQL — SQLite, schema defined later
# ---------------------------------------------------------------------------
def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(_SQLITE_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initialise the SQLite database.

    Creates the database file and runs CREATE TABLE IF NOT EXISTS guards.
    Table schemas are not yet defined — add them below the TODO marker.
    """
    with _get_conn() as conn:
        # TODO: define tables here
        # Example:
        #   conn.execute('''
        #       CREATE TABLE IF NOT EXISTS my_table (
        #           id    INTEGER PRIMARY KEY AUTOINCREMENT,
        #           ...
        #       )
        #   ''')
        conn.commit()
    log.info("SQLite database initialised at %s", _SQLITE_PATH)


def sql_query(query: str, params: tuple = ()) -> list[dict]:
    """Execute a SELECT query and return all rows as a list of dicts.

    Args:
        query: SQL SELECT statement.
        params: Optional positional parameters for the query.

    Returns:
        List of row dicts.
    """
    with _get_conn() as conn:
        cur = conn.execute(query, params)
        return [dict(row) for row in cur.fetchall()]


def sql_execute(statement: str, params: tuple = ()) -> None:
    """Execute a non-SELECT SQL statement (INSERT, UPDATE, DELETE, etc.).

    Args:
        statement: SQL statement to execute.
        params: Optional positional parameters.
    """
    with _get_conn() as conn:
        conn.execute(statement, params)
        conn.commit()


# ---------------------------------------------------------------------------
# Markdown I/O
# ---------------------------------------------------------------------------
def save_markdown(content: str, filename: str, permanent: bool = False) -> str:
    """Save a markdown file to either the temporary or permanent store.

    Args:
        content: Markdown text to write.
        filename: Filename (e.g. 'notes.md'). Extension added if missing.
        permanent: If True, save to soul/ (permanent skills/persona store).
                   If False, save to database/ (temporary store).

    Returns:
        Absolute path of the saved file as a string.
    """
    if not filename.endswith(".md"):
        filename += ".md"
    target_dir = _SOUL_DIR if permanent else _DB_DIR
    path = target_dir / filename
    path.write_text(content, encoding="utf-8")
    log.info("Markdown saved: %s", path)
    return str(path)


def load_markdown(filename: str, permanent: bool = False) -> str:
    """Load a markdown file from the temporary or permanent store.

    Args:
        filename: Filename to load (e.g. 'notes.md').
        permanent: If True, load from soul/. If False, load from database/.

    Returns:
        The file contents as a string.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    if not filename.endswith(".md"):
        filename += ".md"
    target_dir = _SOUL_DIR if permanent else _DB_DIR
    path = target_dir / filename
    if not path.exists():
        raise FileNotFoundError(f"Markdown file not found: {path}")
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Hard Reset — Gemini tool  (deletes and recreates ALL databases)
# ---------------------------------------------------------------------------
def hard_reset_databases() -> str:
    """Delete and fully recreate ALL databases: FAISS index, Qdrant collections, and SQLite.

    ⚠️  This is destructive and irreversible.
    All stored vectors, SQL rows, and Qdrant collections will be permanently erased.
    Temporary markdowns in database/ are also removed.
    Permanent soul/ files are NOT touched.

    Returns:
        A status message describing what was reset.
    """
    global _faiss_index, _faiss_map, _qdrant_client, _llama_model

    report: list[str] = []

    # --- FAISS ---
    _faiss_index = None
    _faiss_map = {}
    if _FAISS_INDEX_PATH.exists():
        _FAISS_INDEX_PATH.unlink()
        report.append("FAISS index deleted.")
    if _FAISS_MAP_PATH.exists():
        _FAISS_MAP_PATH.unlink()
        report.append("FAISS map deleted.")

    # --- Qdrant ---
    if _qdrant_client is not None:
        try:
            for col in _qdrant_client.get_collections().collections:
                _qdrant_client.delete_collection(col.name)
                report.append(f"Qdrant collection '{col.name}' deleted.")
        except Exception as e:
            report.append(f"Qdrant cleanup error: {e}")
        _qdrant_client = None
    if _QDRANT_PATH.exists():
        shutil.rmtree(_QDRANT_PATH)
        _QDRANT_PATH.mkdir(parents=True, exist_ok=True)
        report.append("Qdrant storage directory reset.")

    # --- SQLite ---
    if _SQLITE_PATH.exists():
        _SQLITE_PATH.unlink()
        report.append("SQLite database deleted.")
    init_db()
    report.append("SQLite database recreated (empty).")

    # --- Temporary markdowns in database/ ---
    for md_file in _DB_DIR.glob("*.md"):
        md_file.unlink()
        report.append(f"Temporary markdown '{md_file.name}' deleted.")

    status = "Hard reset complete. " + " ".join(report)
    log.warning(status)
    return status
