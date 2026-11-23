from app.services import llm_client


def rewrite_resume(resume_text: str, job_description: str) -> dict:
    prompt = f"""You are an expert resume writer optimizing resumes for ATS systems.

ORIGINAL RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

CRITICAL RULES:
- Identify EVERY section present in the original resume (e.g. Summary,
  Skills, Experience, Projects, Education, Achievements, Certifications —
  whatever actually appears). Do NOT drop, skip, or merge any section.
- Every bullet point, company, project, and achievement in the original
  MUST appear in your output — you may rewrite the WORDING, but never
  remove real content.
- Rewrite bullet points to include relevant keywords from the job
  description wherever truthfully applicable, and quantify impact where
  the original implies a metric.
- Keep companies, titles, dates, and project names EXACTLY as given.
- Education and Achievements are commonly forgotten — double check they
  are both included if present in the original.

Respond with ONLY valid JSON (no markdown, no code fences) matching EXACTLY:

{{
  "name": "...",
  "contact": "...",
  "summary": "...",
  "skills": ["...", "..."],
  "sections": [
    {{"title": "Experience", "bullets": ["...", "..."]}},
    {{"title": "Projects", "bullets": ["...", "..."]}},
    {{"title": "Education", "bullets": ["...", "..."]}},
    {{"title": "Achievements", "bullets": ["...", "..."]}}
  ]
}}

Include ALL sections that exist in the original resume above — the
example section list is illustrative, not exhaustive or exclusive.
"""

    return llm_client.complete_json(prompt, temperature=0.2)