from __future__ import annotations

import math

import httpx
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.entities import DocumentTemplate


class RagService:
    def __init__(self) -> None:
        self.client = QdrantClient(url=settings.active_qdrant_url)
        self.collection = "sage_documents"

    async def embed(self, text: str) -> list[float]:
        payload = {"model": settings.ollama_embedding_model, "prompt": text}
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(f"{settings.active_ollama_base_url.rstrip('/')}/api/embeddings", json=payload)
            response.raise_for_status()
            data = response.json()
        return data.get("embedding", [])

    def ensure_collection(self, vector_size: int) -> None:
        collections = {item.name for item in self.client.get_collections().collections}
        if self.collection in collections:
            return
        self.client.create_collection(
            collection_name=self.collection,
            vectors_config=qmodels.VectorParams(size=vector_size, distance=qmodels.Distance.COSINE),
        )

    async def index_templates(self, db: Session) -> int:
        templates = db.query(DocumentTemplate).all()
        indexed = 0
        for template in templates:
            embedding = await self.embed(template.content_text)
            if not embedding:
                continue
            self.ensure_collection(len(embedding))
            self.client.upsert(
                collection_name=self.collection,
                points=[
                    qmodels.PointStruct(
                        id=template.id,
                        vector=embedding,
                        payload={"title": template.title, "content_text": template.content_text, "audit_type": template.audit_type.value},
                    )
                ],
            )
            indexed += 1
        return indexed

    async def search(self, query: str, top_k: int = 5) -> list[dict]:
        embedding = await self.embed(query)
        if not embedding:
            return []
        self.ensure_collection(len(embedding))
        results = self.client.search(collection_name=self.collection, query_vector=embedding, limit=top_k)
        hits: list[dict] = []
        for result in results:
            payload = result.payload or {}
            hits.append({"id": str(result.id), "title": payload.get("title", ""), "content_text": payload.get("content_text", ""), "score": float(result.score or 0.0)})
        return hits


rag_service = RagService()
