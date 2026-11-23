import numpy as np
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Document, Chunk


def save_document(
    db: Session,
    owner_id: int,
    filename: str,
    chunks: list[str],
    embeddings: np.ndarray,
) -> Document:
    document = Document(owner_id=owner_id, filename=filename)
    document.chunks = [
        Chunk(chunk_index=i, content=text, embedding=vector.tolist())
        for i, (text, vector) in enumerate(zip(chunks, embeddings))
    ]
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def search_chunks(
    db: Session,
    document_id: str,
    query_vector: np.ndarray,
    top_k: int = 4,
) -> list[str]:
    stmt = (
        select(Chunk.content)
        .where(Chunk.document_id == document_id)
        .order_by(Chunk.embedding.cosine_distance(query_vector.tolist()))
        .limit(top_k)
    )
    return list(db.scalars(stmt).all())