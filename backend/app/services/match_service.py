from app.services import llm_client


def analyze_match(resume_text: str, job_description: str) -> dict:
    prompt = f"""You are an expert technical recruiter and ATS evaluator.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Respond with ONLY valid JSON (no markdown, no code fences, no extra text)
matching EXACTLY this structure:

{{
  "match_score": <integer 0-100>,
  "score_justification": "<one sentence>",
  "matching_skills": ["<skill>", "<skill>", ...],
  "missing_skills": ["<skill>", "<skill>", ...],
  "suggestions": ["<general suggestion>", "<general suggestion>", "<general suggestion>"],
  "section_suggestions": [
    {{
      "section": "<exact section name as it appears/should appear in the resume, e.g. Skills, Experience, Certifications, Projects>",
      "additions": ["<specific detail, keyword, or bullet point to add to THIS section>", "..."]
    }}
  ]
}}

For section_suggestions:
- Only include sections where something concrete should genuinely be added.
- Each addition must be specific and directly tied to a requirement in the
  job description (e.g. "Add 'ISO 13485' to Skills" not "add relevant skills").
- If a needed section doesn't exist in the resume at all (e.g. no
  Certifications section but the JD wants one), still include it here with
  a note that it should be newly added.
- Do not repeat the same advice in both "suggestions" and "section_suggestions" —
  keep "suggestions" for general resume-writing advice (formatting, quantifying
  impact, tone), and "section_suggestions" strictly for concrete content additions.
"""

    return llm_client.complete_json(prompt, temperature=0.3)