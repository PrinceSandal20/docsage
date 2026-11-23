from pydantic import BaseModel
from datetime import datetime
from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    session_id: str
    question: str
    top_k: int = 4


class AskResponse(BaseModel):
    answer: str
    sources: list[str]


class SectionSuggestion(BaseModel):
    section: str
    additions: list[str]


class MatchAnalysis(BaseModel):
    match_score: int = Field(ge=0, le=100)
    score_justification: str
    matching_skills: list[str]
    missing_skills: list[str]
    suggestions: list[str]
    section_suggestions: list[SectionSuggestion]


class MatchResponse(MatchAnalysis):
    id: int
    resume_filename: str
    created_at: datetime


class ResumeSection(BaseModel):
    title: str
    bullets: list[str]


class RewrittenResume(BaseModel):
    name: str
    contact: str
    summary: str
    skills: list[str]
    sections: list[ResumeSection]   # Experience, Projects, Education, etc.