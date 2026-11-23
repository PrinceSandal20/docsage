from sqlalchemy.orm import Session

from app.db.models import MatchResult
from app.Dtos.document import MatchAnalysis


def save_match(
    db: Session,
    owner_id: int,
    resume_filename: str,
    job_description: str,
    analysis: MatchAnalysis,
) -> MatchResult:
    record = MatchResult(
        owner_id=owner_id,
        resume_filename=resume_filename,
        job_description=job_description,
        match_score=analysis.match_score,
        result=analysis.model_dump(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_match(db: Session, match_id: int, owner_id: int) -> MatchResult | None:
    record = db.get(MatchResult, match_id)
    if record is None or record.owner_id != owner_id:
        return None
    return record


def list_matches(db: Session, owner_id: int, limit: int = 20) -> list[MatchResult]:
    return (
        db.query(MatchResult)
        .filter(MatchResult.owner_id == owner_id)
        .order_by(MatchResult.created_at.desc())
        .limit(limit)
        .all()
    )