from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, Table, TableStyle,
    KeepTogether, HRFlowable
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets"

GOLD = colors.HexColor("#9b731d")
INK = colors.HexColor("#171717")
MUTED = colors.HexColor("#5d5d5d")
LIGHT = colors.HexColor("#e4d19a")
PAGE_W, PAGE_H = A4
LEFT = 16 * mm
RIGHT = 16 * mm
TOP = 13 * mm
BOTTOM = 12 * mm
CONTENT_W = PAGE_W - LEFT - RIGHT


def esc(text):
    return (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def link(text, url):
    return f'<link href="{url}" color="#7a5a12"><u>{esc(text)}</u></link>'


def make_styles():
    return {
        "name": ParagraphStyle("Name", fontName="Helvetica-Bold", fontSize=23, leading=25, textColor=INK, spaceAfter=2),
        "headline": ParagraphStyle("Headline", fontName="Helvetica-Bold", fontSize=9.4, leading=11.5, textColor=GOLD, spaceAfter=2),
        "contact": ParagraphStyle("Contact", fontName="Helvetica", fontSize=8.0, leading=10.0, textColor=MUTED, spaceAfter=6),
        "section": ParagraphStyle("Section", fontName="Helvetica-Bold", fontSize=8.8, leading=10.5, textColor=GOLD, spaceBefore=5, spaceAfter=2, uppercase=True),
        "body": ParagraphStyle("Body", fontName="Helvetica", fontSize=8.2, leading=10.5, textColor=INK, spaceAfter=1),
        "muted": ParagraphStyle("Muted", fontName="Helvetica", fontSize=7.8, leading=9.8, textColor=MUTED, spaceAfter=1),
        "role": ParagraphStyle("Role", fontName="Helvetica-Bold", fontSize=8.6, leading=10.5, textColor=INK),
        "date": ParagraphStyle("Date", fontName="Helvetica", fontSize=7.8, leading=9.8, textColor=MUTED, alignment=2),
        "small": ParagraphStyle("Small", fontName="Helvetica", fontSize=7.4, leading=9.2, textColor=MUTED),
        "bullet": ParagraphStyle("Bullet", fontName="Helvetica", fontSize=7.9, leading=10.0, leftIndent=7, firstLineIndent=-5, textColor=INK, spaceAfter=1),
        "project": ParagraphStyle("Project", fontName="Helvetica-Bold", fontSize=8.4, leading=10.0, textColor=INK),
    }


class CVDoc(BaseDocTemplate):
    def __init__(self, filename, **kwargs):
        super().__init__(filename, pagesize=A4, leftMargin=LEFT, rightMargin=RIGHT, topMargin=TOP, bottomMargin=BOTTOM, **kwargs)
        frame = Frame(LEFT, BOTTOM, CONTENT_W, PAGE_H - TOP - BOTTOM, id="normal", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        self.addPageTemplates([PageTemplate(id="cv", frames=[frame], onPage=self._page)])

    def _page(self, canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(LIGHT)
        canvas.setLineWidth(0.4)
        canvas.line(LEFT, 8.5 * mm, PAGE_W - RIGHT, 8.5 * mm)
        canvas.setFont("Helvetica", 6.8)
        canvas.setFillColor(MUTED)
        canvas.drawString(LEFT, 5.5 * mm, "Khalil Khalil")
        canvas.drawRightString(PAGE_W - RIGHT, 5.5 * mm, "Page 1 of 1")
        canvas.restoreState()


def section(story, title, styles):
    story.append(Paragraph(title.upper(), styles["section"]))
    story.append(HRFlowable(width="100%", thickness=0.45, color=LIGHT, spaceBefore=0, spaceAfter=4))


def bullet(text, styles):
    return Paragraph(f"- {text}", styles["bullet"])


def role_block(role, company, dates, bullets, styles):
    head = Table([[Paragraph(f"{esc(role)}<br/><font color='#5d5d5d'>{esc(company)}</font>", styles["role"]), Paragraph(esc(dates), styles["date"])]], colWidths=[CONTENT_W * 0.77, CONTENT_W * 0.23])
    head.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 1)]))
    content = [head] + [bullet(b, styles) for b in bullets]
    return KeepTogether(content)


def education_row(degree, institution, dates, styles):
    t = Table([[Paragraph(f"<b>{esc(degree)}</b><br/><font color='#5d5d5d'>{esc(institution)}</font>", styles["body"]), Paragraph(esc(dates), styles["date"])]], colWidths=[CONTENT_W * 0.77, CONTENT_W * 0.23])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]))
    return t


def project_row(name, kind, description, url, styles):
    left = Paragraph(f"<b>{esc(name)}</b> - <font color='#5d5d5d'>{esc(description)}</font>", styles["body"])
    right = Paragraph(esc(kind), styles["date"])
    t = Table([[left, right]], colWidths=[CONTENT_W * 0.77, CONTENT_W * 0.23])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 1)]))
    if url:
        t2 = Paragraph(link(url.replace("https://", ""), url), styles["small"])
        return [t, t2]
    return [t]


def header(story, headline, styles):
    story.extend([
        Paragraph("Khalil Khalil", styles["name"]),
        Paragraph(esc(headline), styles["headline"]),
        Paragraph(
            "Homs, Syria &nbsp;|&nbsp; "
            + link("khalilmkhalil0937@gmail.com", "mailto:khalilmkhalil0937@gmail.com")
            + " &nbsp;|&nbsp; "
            + link("+963 960 955 844", "https://wa.me/963960955844")
            + " &nbsp;|&nbsp; "
            + link("khalil-m-khalil.github.io", "https://khalil-m-khalil.github.io/"),
            styles["contact"],
        ),
    ])


def build_creative():
    s = make_styles(); story = []
    header(story, "Brand Architecture | AI-Driven Content & Growth Systems | Visual Identity", s)
    
    section(story, "Profile", s)
    story.append(Paragraph("Brand architect and creative strategist based in Syria, working with Arab-market and international clients. I develop distinct visual identities, kinetic motion systems, and AI-driven 30-day content and growth engines that combine audience psychology with rapid execution.", s["body"]))

    section(story, "Experience", s)
    story.append(role_block("Brand Designer & AI Growth Strategist", "Freelance, remote", "2021 - Present", [
        "Architected end-to-end brand identities, logos, and design systems for Arab and Gulf-market businesses.",
        "Engineered 30-day AI-driven content engines: mining competitor friction, defining visual directions, and drafting bilingual copy.",
        "Produced kinetic motion graphics, packaging, and digital campaign assets using modern compositing tools.",
        "Delivered strategic brand collateral and social media visual guidelines across Instagram, Facebook, and TikTok.",
    ], s))
    story.append(Spacer(1, 2))
    story.append(role_block("Content Strategy & Digital Mentorship", "Independent, remote", "Ongoing", [
        "Mentored and guided 100+ learners across visual design, branding hierarchy, copywriting, and AI-assisted production workflows.",
        "Authored structured design roadmaps and practical curriculum blueprints for digital creators.",
    ], s))

    section(story, "Selected Work", s)
    for item in [
        ("Almira", "Visual Identity", "Arabic calligraphic logo system and campaign artwork in a deep green and gold palette.", "https://khalil-m-khalil.github.io/#work"),
        ("WHY Z", "Brand Identity", "Complete logo concept, color and typographic system, and stationery for a creative agency.", "https://khalil-m-khalil.github.io/#work"),
        ("Take Car Taxi", "Campaign System", "High-visibility social media campaign post and vehicle branding system in yellow and black.", "https://khalil-m-khalil.github.io/#work"),
    ]:
        story.extend(project_row(*item, s)); story.append(Spacer(1, 1))

    section(story, "Education", s)
    story.append(education_row("BSc Computer Science (in progress)", "University of the People (UoPeople), online", "2023 - Present", s))
    story.append(education_row("Bachelor of Law", "Hawash Private University (HPU), Homs, Syria", "Graduated", s))

    section(story, "Core Skills & Tools", s)
    story.append(Paragraph("<b>Creative & Strategy:</b> Brand Architecture &amp; Logo Systems | 30-Day AI Content Engines | Kinetic Motion | Audience Friction Mining | Packaging &amp; Print | Bilingual Copywriting", s["body"]))
    story.append(Paragraph("<b>Software & Toolchain:</b> Adobe Illustrator | Adobe Photoshop | Adobe Premiere Pro | Figma | Remotion | AI Generative Pipelines", s["body"]))

    section(story, "Links & Languages", s)
    story.append(Paragraph(
        link("Portfolio", "https://khalil-m-khalil.github.io/") + " &nbsp;|&nbsp; "
        + link("Design Archive", "https://drive.google.com/drive/folders/1rTo1E-fPrPY6pIhvT161_SrQnGuniPov?usp=sharing") + " &nbsp;|&nbsp; "
        + link("Training Proof", "https://drive.google.com/drive/folders/13GqGvguyTr6kWKUW5x6vtzwh6g4zrEBA?usp=drive_link") + " &nbsp;|&nbsp; "
        + link("Instagram @khalil_m_khalil09", "https://www.instagram.com/khalil_m_khalil09/"), s["small"]))
    story.append(Paragraph("<b>Languages:</b> Arabic (Native) | English (Professional)", s["body"]))
    
    CVDoc(str(OUT / "Khalil_Khalil_CV_Creative.pdf")).build(story)


def build_technical():
    s = make_styles(); story = []
    header(story, "AI Solutions Architecture | Vulnerability Research | Full-Stack Systems", s)
    
    section(story, "Profile", s)
    story.append(Paragraph("AI-native solutions architect and cybersecurity researcher combining legal analytical rigor (Bachelor of Law, HPU) with Computer Science studies (University of the People). Proven track record discovering critical logic vulnerabilities (Meta race condition recognized by OffSec), building local forensics utilities, and directing advanced LLMs to engineer deterministic prompt architectures, browser automation workflows, and production software.", s["body"]))

    section(story, "Experience", s)
    story.append(role_block("AI Solutions Architect & Systems Prototyper", "Freelance, remote", "2022 - Present", [
        "Directed LLMs to engineer functioning Python, WebGL, and SQLite applications (Phoenix dashboard, Nabra keyboard utility, Sada noise calibrator).",
        "Designed automated browser execution workflows, high-volume data ingestion pipelines, and structured document synthesis.",
        "Authored open-source prompt architectures utilizing Chain-of-Thought (CoT) and structured JSON/XML schemas to eliminate hallucinations.",
    ], s))
    story.append(Spacer(1, 2))
    story.append(role_block("Independent Security Researcher", "Self-directed research", "2024 - Present", [
        "Discovered and documented a critical race condition in Meta's OAuth/email confirmation workflow; highlighted by OffSec in March 2026.",
        "Conducted logic flaw testing via Burp Suite, open redirect evaluations, and OSINT digital forensics investigations.",
        "Provided confidential incident triage, unauthorized account takedowns, and digital extortion mitigation for individuals and creators.",
    ], s))
    story.append(Spacer(1, 2))
    story.append(role_block("Technical Training & Open-Source Protocols", "Independent, remote", "Ongoing", [
        "Engineered the open-source Career Roadmap and App Validation Protocols on GitHub, establishing reproducible AI evaluation gates.",
        "Mentored 100+ learners across cybersecurity fundamentals, web development, and applied AI workflows.",
    ], s))

    section(story, "Recognition & Key Projects", s)
    for item in [
        ("OffSec Highlight", "Recognition", "Race condition research on a Meta platform highlighted in March 2026.", "https://drive.google.com/drive/folders/1HXxHzGPUjzUS0UELDB2VLeCQS-KJ0T_A?usp=drive_link"),
        ("Horizon Lab", "Forensics", "Ranked #1 in Syria and #177 worldwide with 93% score in digital forensics using Phoenix.", "https://drive.google.com/drive/folders/1fVV4dVbT0LvDbXnkb4AqCLJVFaOdKqos?usp=drive_link"),
        ("Phoenix & Nabra", "Software", "Local digital forensics verification dashboard and offline Windows bilingual keyboard utility.", "https://khalil-m-khalil.github.io/Phoenix/"),
        ("AI Protocols", "Open Source", "Deterministic prompt architectures and agentic pipelines with 100+ research roadmaps.", "https://github.com/Khalil-M-Khalil"),
    ]:
        story.extend(project_row(*item, s)); story.append(Spacer(1, 1))

    section(story, "Education", s)
    story.append(education_row("BSc Computer Science (in progress)", "University of the People (UoPeople), online", "2023 - Present", s))
    story.append(education_row("Bachelor of Law", "Hawash Private University (HPU), Homs, Syria", "Graduated", s))

    section(story, "Technical Skills & Toolchain", s)
    story.append(Paragraph("<b>AI & Automation:</b> Prompt Architecture | Chain-of-Thought (CoT) | Few-Shot Calibration | LLM Orchestration (Claude, GPT-4) | Structured Outputs (JSON/XML) | Browser &amp; Data Automation", s["body"]))
    story.append(Paragraph("<b>Security & Forensics:</b> Vulnerability Research | Logic Flaws &amp; Race Conditions | Burp Suite | Wireshark | Nmap | Sleuth Kit | Autopsy | Volatility 3 | Incident Triage", s["body"]))
    story.append(Paragraph("<b>Development & Systems:</b> Python | HTML5 | CSS3 | JavaScript | SQLite | WebGL | Linux / Debian | Git / GitHub", s["body"]))

    section(story, "Links & Languages", s)
    story.append(Paragraph(
        link("Portfolio", "https://khalil-m-khalil.github.io/") + " &nbsp;|&nbsp; "
        + link("GitHub", "https://github.com/Khalil-M-Khalil") + " &nbsp;|&nbsp; "
        + link("Training Proof", "https://drive.google.com/drive/folders/13GqGvguyTr6kWKUW5x6vtzwh6g4zrEBA?usp=drive_link") + " &nbsp;|&nbsp; "
        + link("Research Archive", "https://drive.google.com/drive/folders/1HXxHzGPUjzUS0UELDB2VLeCQS-KJ0T_A?usp=drive_link"), s["small"]))
    story.append(Paragraph("<b>Languages:</b> Arabic (Native) | English (Professional)", s["body"]))
    
    CVDoc(str(OUT / "Khalil_Khalil_CV_Technical.pdf")).build(story)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    build_creative()
    build_technical()
    print("Generated:")
    print(OUT / "Khalil_Khalil_CV_Creative.pdf")
    print(OUT / "Khalil_Khalil_CV_Technical.pdf")
