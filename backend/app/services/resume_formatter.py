def format_resume_as_text(resume: dict) -> str:
    lines = [resume["name"], resume["contact"], "", "SUMMARY", resume["summary"], "", "SKILLS"]
    lines.append(", ".join(resume["skills"]))
    lines.append("")

    for section in resume["sections"]:
        lines.append(section["title"].upper())
        for bullet in section["bullets"]:
            lines.append(f"- {bullet}")
        lines.append("")

    return "\n".join(lines)