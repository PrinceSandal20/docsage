from fpdf import FPDF


def clean_text(text: str) -> str:
    replacements = {
        "\u202f": " ", "\u00a0": " ",
        "\u2018": "'", "\u2019": "'",
        "\u201c": '"', "\u201d": '"',
        "\u2013": "-", "\u2014": "-",
        "\u2026": "...",
        "\u2022": "-",  # bullet char: not in latin-1, would be silently dropped
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    return text.encode("latin-1", errors="ignore").decode("latin-1")


def safe_multicell(pdf: FPDF, text: str, line_height: float = 5, indent: float = 0):
    left_x = pdf.l_margin + indent
    pdf.set_x(left_x)
    max_width = pdf.w - left_x - pdf.r_margin

    safe_words = []
    for word in text.split(" "):
        while pdf.get_string_width(word) > max_width and len(word) > 1:
            cut = len(word)
            while cut > 1 and pdf.get_string_width(word[:cut]) > max_width:
                cut -= 1
            safe_words.append(word[:cut])
            word = word[cut:]
        safe_words.append(word)

    pdf.set_x(left_x)
    pdf.multi_cell(max_width, line_height, " ".join(safe_words))


def build_resume_pdf(resume_data: dict) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_margins(left=18, top=15, right=18)

    # ---- Header ----
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 10, clean_text(resume_data["name"]), ln=True, align="C")

    pdf.set_font("Helvetica", "", 9.5)
    pdf.set_text_color(90, 90, 90)
    contact = clean_text(resume_data["contact"])
    contact = "  |  ".join(part.strip() for part in contact.replace("|", ",").split(",") if part.strip())
    pdf.cell(0, 6, contact, ln=True, align="C")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(4)

    def section_header(title: str):
        pdf.set_x(pdf.l_margin)
        pdf.set_font("Helvetica", "B", 11.5)
        pdf.set_text_color(30, 60, 110)
        pdf.cell(0, 7, clean_text(title).upper(), ln=True)
        y = pdf.get_y()
        pdf.set_draw_color(30, 60, 110)
        pdf.set_line_width(0.4)
        pdf.line(pdf.l_margin, y, pdf.w - pdf.r_margin, y)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(2.5)

    def bullet_point(text: str):
        pdf.set_x(pdf.l_margin)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(4, 5, chr(149))
        safe_multicell(pdf, clean_text(text), indent=4)
        pdf.ln(0.5)

    # ---- Summary ----
    section_header("Summary")
    pdf.set_font("Helvetica", "", 10)
    safe_multicell(pdf, clean_text(resume_data["summary"]))
    pdf.ln(4)

    # ---- Skills ----
    section_header("Skills")
    pdf.set_font("Helvetica", "", 10)
    safe_multicell(pdf, clean_text(", ".join(resume_data["skills"])))
    pdf.ln(4)

    # ---- Remaining sections ----
    for section in resume_data["sections"]:
        section_header(section["title"])
        for bullet in section["bullets"]:
            bullet_point(bullet)
        pdf.ln(3)

    return bytes(pdf.output())