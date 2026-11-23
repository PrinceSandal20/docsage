from sqlalchemy.orm import Session

from app.db.models import GeneratedResume


def save_generated_resume(
    db: Session,
    owner_id: int,
    match_result_id: int | None,
    job_description: str,
    content: dict,
    pdf_data: bytes,
) -> GeneratedResume:
    record = GeneratedResume(
        owner_id=owner_id,
        match_result_id=match_result_id,
        job_description=job_description,
        content=content,
        pdf_data=pdf_data,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_generated_resume(db: Session, resume_id: int, owner_id: int) -> GeneratedResume | None:
    record = db.get(GeneratedResume, resume_id)
    if record is None or record.owner_id != owner_id:
        return None
    return record


def list_generated_resumes(db: Session, owner_id: int, limit: int = 20) -> list[GeneratedResume]:
    return (
        db.query(GeneratedResume)
        .filter(GeneratedResume.owner_id == owner_id)
        .order_by(GeneratedResume.created_at.desc())
        .limit(limit)
        .all()
    )