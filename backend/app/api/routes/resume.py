from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import Response, PlainTextResponse
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.db.models import User, MatchResult
from app.Dtos.document import MatchAnalysis, MatchResponse, RewrittenResume
from app.services import (
    pdf_reader,
    match_service,
    match_repository,
    resume_service,
    resume_repository,
    resume_formatter,
    pdf_builder,
)

router = APIRouter()


def _to_response(record: MatchResult) -> MatchResponse:
    return MatchResponse(
        id=record.id,
        resume_filename=record.resume_filename,
        created_at=record.created_at,
        **record.result,
    )


# ---------------- match ----------------

@router.post("/match", response_model=MatchResponse)
def match_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not resume.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Resume must be a PDF file.")

    resume_text = pdf_reader.load_text_from_pdf(resume.file)
    raw = match_service.analyze_match(resume_text, job_description)

    try:
        analysis = MatchAnalysis(**raw)
    except ValidationError:
        raise HTTPException(status_code=502, detail="The AI returned an unexpected format. Please try again.")

    record = match_repository.save_match(db, current_user.id, resume.filename, job_description, analysis)
    return _to_response(record)


@router.get("/match/history")
def match_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    records = match_repository.list_matches(db, current_user.id)
    return [
        {"id": r.id, "resume_filename": r.resume_filename, "match_score": r.match_score, "created_at": r.created_at}
        for r in records
    ]


@router.get("/match/{match_id}", response_model=MatchResponse)
def get_match(
    match_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = match_repository.get_match(db, match_id, current_user.id)
    if record is None:
        raise HTTPException(status_code=404, detail="Match result not found.")
    return _to_response(record)


# ---------------- generated resumes ----------------

@router.post("/generate-resume")
def generate_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
    match_id: int | None = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not resume.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Resume must be a PDF file.")

    if match_id is not None and match_repository.get_match(db, match_id, current_user.id) is None:
        raise HTTPException(status_code=404, detail="Match result not found.")

    resume_text = pdf_reader.load_text_from_pdf(resume.file)
    raw = resume_service.rewrite_resume(resume_text, job_description)

    try:
        rewritten = RewrittenResume(**raw)
    except ValidationError:
        raise HTTPException(status_code=502, detail="The AI returned an unexpected format. Please try again.")

    content = rewritten.model_dump()
    pdf_bytes = pdf_builder.build_resume_pdf(content)

    record = resume_repository.save_generated_resume(
        db, current_user.id, match_id, job_description, content, pdf_bytes
    )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": 'attachment; filename="updated_resume.pdf"',
            "X-Resume-Id": str(record.id),
        },
    )


@router.get("/generated-resumes")
def list_generated(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    records = resume_repository.list_generated_resumes(db, current_user.id)
    return [
        {
            "id": r.id,
            "name": r.content.get("name"),
            "match_result_id": r.match_result_id,
            "created_at": r.created_at,
        }
        for r in records
    ]


@router.get("/generated-resumes/{resume_id}/pdf")
def download_generated_pdf(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = resume_repository.get_generated_resume(db, resume_id, current_user.id)
    if record is None:
        raise HTTPException(status_code=404, detail="Generated resume not found.")

    return Response(
        content=bytes(record.pdf_data),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="resume_{record.id}.pdf"'},
    )


@router.get("/generated-resumes/{resume_id}/text", response_class=PlainTextResponse)
def download_generated_text(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = resume_repository.get_generated_resume(db, resume_id, current_user.id)
    if record is None:
        raise HTTPException(status_code=404, detail="Generated resume not found.")

    return resume_formatter.format_resume_as_text(record.content)