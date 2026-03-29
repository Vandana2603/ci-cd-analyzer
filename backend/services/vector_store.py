import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
from typing import List, Optional, Dict, Any
import uuid
import json
from config import settings


class VectorStore:
    _instance = None

    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_or_create_collection(
            name="cicd_logs",
            metadata={"hnsw:space": "cosine"},
        )
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)

    @classmethod
    def get_instance(cls) -> "VectorStore":
        if cls._instance is None:
            cls._instance = VectorStore()
        return cls._instance

    def embed(self, text: str) -> List[float]:
        return self.model.encode(text, normalize_embeddings=True).tolist()

    def add_document(
        self,
        doc_id: str,
        text: str,
        metadata: Dict[str, Any],
    ) -> str:
        embedding = self.embed(text)
        # Flatten metadata values to strings/numbers/bools
        safe_meta = {k: (str(v) if not isinstance(v, (str, int, float, bool)) else v)
                     for k, v in metadata.items()}
        self.collection.upsert(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[safe_meta],
        )
        return doc_id

    def query_similar(
        self,
        query_text: str,
        top_k: int = None,
        where: Optional[Dict] = None,
    ) -> List[Dict[str, Any]]:
        if top_k is None:
            top_k = settings.TOP_K_SIMILAR

        count = self.collection.count()
        if count == 0:
            return []

        top_k = min(top_k, count)
        embedding = self.embed(query_text)

        kwargs: Dict[str, Any] = {
            "query_embeddings": [embedding],
            "n_results": top_k,
            "include": ["documents", "metadatas", "distances"],
        }
        if where:
            kwargs["where"] = where

        results = self.collection.query(**kwargs)

        output = []
        for i in range(len(results["ids"][0])):
            similarity = 1 - results["distances"][0][i]  # cosine → similarity
            output.append({
                "id": results["ids"][0][i],
                "document": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "similarity": round(similarity, 4),
            })
        return output

    def update_feedback_score(self, doc_id: str, delta: float):
        """Bump or lower the stored feedback_score for a document."""
        try:
            result = self.collection.get(ids=[doc_id], include=["metadatas"])
            if not result["ids"]:
                return
            meta = result["metadatas"][0]
            current = float(meta.get("feedback_score", 0.0))
            meta["feedback_score"] = round(current + delta, 4)
            self.collection.update(ids=[doc_id], metadatas=[meta])
        except Exception:
            pass


def get_vector_store() -> VectorStore:
    return VectorStore.get_instance()
