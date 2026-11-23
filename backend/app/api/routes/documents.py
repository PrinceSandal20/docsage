from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.db.models import Document, User
from app.Dtos.document import AskRequest, AskResponse
from app.services import pdf_reader, chunker, embedder, vector_store, qa_service

router = APIRouter()


@router.post("/upload")
def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    text = pdf_reader.load_text_from_pdf(file.file)
    chunks = chunker.chunk_text(text)
    if not chunks:
        raise HTTPException(
            status_code=400,
            detail="No extractable text found. Scanned PDFs aren't supported yet.",
        )

    embeddings = embedder.embed_texts(chunks)
    document = vector_store.save_document(db, current_user.id, file.filename, chunks, embeddings)

    return {"session_id": document.id, "filename": document.filename, "chunks_indexed": len(chunks)}


@router.get("/documents")
def list_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    docs = (
        db.query(Document)
        .filter(Document.owner_id == current_user.id)
        .order_by(Document.created_at.desc())
        .all()
    )
    return [{"id": d.id, "filename": d.filename, "created_at": d.created_at} for d in docs]


@router.post("/ask", response_model=AskResponse)
def ask_question(
    request: AskRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document = db.get(Document, request.session_id)
    if document is None or document.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Document not found.")

    query_vector = embedder.embed_query(request.question)
    relevant_chunks = vector_store.search_chunks(db, document.id, query_vector, request.top_k)
    answer = qa_service.answer_question(request.question, relevant_chunks)

    return AskResponse(answer=answer, sources=relevant_chunks)