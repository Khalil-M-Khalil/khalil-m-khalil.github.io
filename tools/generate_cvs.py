from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, Table, TableStyle,
    KeepTogether, HRFlowable, PageBreak
)
from reportlab.pdfbase.pdfmetrics import stringWidth

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets"

GOLD = colors.HexColor("#9b731d")
INK = colors.HexColor("#171717")
MUTED = colors.HexColor("#5d5d5d")
LIGHT = colors.HexColor("#e4d19a")
PAGE_W, PAGE_H = A4
LEFT = 18 * mm
RIGHT = 18 * mm
TOP = 15 * mm
BOTTOM = 14 * mm
CONTENT_W = PAGE_W - LEFT - RIGHT


def esc(text):
    return (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def link(text, url):
    return f'<link href="{url}" color="#7a5a12"><u>{esc(text)}</u></link>'


def make_styles():
    return {
        "name": ParagraphStyle("Name", fontName="Helvetica-Bold", fontSize=25, leading=27, textColor=INK, spaceAfter=2),
        "headline": ParagraphStyle("Headline", fontName="Helvetica-Bold", fontSize=9.7, leading=12, textColor=GOLD, spaceAfter=3),
        "contact": ParagraphStyle("Contact", fontName="Helvetica", fontSize=8.1, leading=10.2, textColor=MUTED, spaceAfter=8),
        "section": ParagraphStyle("Section", fontName="Helvetica-Bold", fontSize=9.2, leading=11, textColor=GOLD, spaceBefore=7, spaceAfter=3, uppercase=True),
        "body": ParagraphStyle("Body", fontName="Helvetica", fontSize=8.8, leading=11.3, textColor=INK, spaceAfter=2),
        "muted": ParagraphStyle("Muted", fontName="Helvetica", fontSize=8.25, leading=10.7, textColor=MUTED, spaceAfter=1),
        "role": ParagraphStyle("Role", fontName="Helvetica-Bold", fontSize=9.1, leading=11, textColor=INK),
        "date": ParagraphStyle("Date", fontName="Helvetica", fontSize=8.2, leading=10, textColor=MUTED, alignment=2),
        "small": ParagraphStyle("Small", fontName="Helvetica", fontSize=7.8, leading=10, textColor=MUTED),
        "bullet": ParagraphStyle("Bullet", fontName="Helvetica", fontSize=8.25, leading=10.5, leftIndent=8, firstLineIndent=-6, textColor=INK, spaceAfter=1),
        "project": ParagraphStyle("Project", fontName="Helvetica-Bold", fontSize=8.8, leading=10.5, textColor=INK),
    }


class CVDoc(BaseDocTemplate):
    def __init__(self, filename, **kwargs):
        super().__init__(filename, pagesize=A4, leftMargin=LEFT, rightMargin=RIGHT, topMargin=TOP, bottomMargin=BOTTOM, **kwargs)
        frame = Frame(LEFT, BOTTOM, CONTENT_W, PAGE_H - TOP - BOTTOM, id="normal", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        self.addPageTemplates([PageTemplate(id="cv", frames=[frame], onPage=self._page)])

    def _page(self, canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(LIGHT)
        canvas.setLineWidth(0.45)
        canvas.line(LEFT, 9.5 * mm, PAGE_W - RIGHT, 9.5 * mm)
        canvas.setFont("Helvetica", 6.8)
        canvas.setFillColor(MUTED)
        canvas.drawString(LEFT, 6.2 * mm, "Khalil Khalil")
        canvas.drawRightString(PAGE_W - RIGHT, 6.2 * mm, f"{doc.page}")
        canvas.restoreState()


def section(story, title, styles):
    story.append(Paragraph(title.upper(), styles["section"]))
    story.append(HRFlowable(width="100%", thickness=0.55, color=LIGHT, spaceBefore=0, spaceAfter=5))


def bullet(text, styles):
    return Paragraph(f"• {text}", styles["bullet"])


def role_block(role, company, dates, bullets, styles):
    head = Table([[Paragraph(f"{esc(role)}<br/><font color='#5d5d5d'>{esc(company)}</font>", styles["role"]), Paragraph(esc(dates), styles["date"])]], colWidths=[CONTENT_W * 0.76, CONTENT_W * 0.24])
    head.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]))
    content = [head] + [bullet(b, styles) for b in bullets]
    return KeepTogether(content)


def education_row(degree, institution, dates, styles):
    t = Table([[Paragraph(f"<b>{esc(degree)}</b><br/><font color='#5d5d5d'>{esc(institution)}</font>", styles["body"]), Paragraph(esc(dates), styles["date"])]], colWidths=[CONTENT_W * 0.76, CONTENT_W * 0.24])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    return t


def project_row(name, kind, description, url, styles):
    left = Paragraph(f"<b>{esc(name)}</b><br/><font color='#5d5d5d'>{esc(description)}</font>", styles["body"])
    right = Paragraph(esc(kind), styles["date"])
    t = Table([[left, right]], colWidths=[CONTENT_W * 0.76, CONTENT_W * 0.24])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    if url:
        # Add a linked project name in a separate, compact line below the description.
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
    header(story, "Brand Identity | Logo & Social Media Design | Content Creation", s)
    section(story, "Profile", s)
    story.append(Paragraph("Creative designer and visual storyteller based in Syria, specialising in brand identity, logo design, social media design and bilingual content. I develop clear visual systems for Arab-market clients and work remotely in Arabic and English.", s["body"]))

    section(story, "Experience", s)
    story.append(role_block("Freelance Graphic Designer & Content Creator", "Self-employed, remote", "2021 – Present", [
        "Developed brand identities, logos and visual systems for Gulf and Arab-market clients.",
        "Created social media content and campaigns for Instagram, Facebook and Snapchat.",
        "Produced packaging, print materials and campaign artwork for food and beverage brands.",
        "Wrote and adapted bilingual Arabic/English marketing content.",
    ], s))
    story.append(Spacer(1, 3))
    story.append(role_block("Training & Career Guidance", "Independent, remote", "Ongoing", [
        "Trained and supported 100+ learners across programming, web development, cybersecurity, design, data and career readiness.",
        "Prepared course files, study roadmaps, practice plans and career research for different learning goals.",
    ], s))

    section(story, "Selected Work", s)
    for item in [
        ("Almira", "Visual identity", "Arabic calligraphic logo and campaign artwork in a deep green and gold palette.", "https://khalil-m-khalil.github.io/#work"),
        ("WHY Z", "Logo & brand identity", "Logo concept, colour and type system, business cards and stationery for a creative marketing agency.", "https://khalil-m-khalil.github.io/#work"),
        ("Take Car Taxi", "Social media design", "Campaign post built on a yellow and black identity, with the logo applied to the vehicle.", "https://khalil-m-khalil.github.io/#work"),
    ]:
        story.extend(project_row(*item, s)); story.append(Spacer(1, 2))

    section(story, "Education", s)
    story.append(education_row("BSc Computer Science (in progress)", "University of the People (UoPeople), online", "2023 – Present", s))
    story.append(education_row("Bachelor of Law", "Hawash Private University (HPU), Homs, Syria", "Graduated", s))

    section(story, "Core Skills &amp; Tools", s)
    story.append(Paragraph("<b>Skills:</b> Brand identity &amp; logo design | Social media design | Packaging &amp; print | Photography &amp; editing | Content strategy &amp; copywriting | AI-assisted workflows", s["body"]))
    story.append(Paragraph("<b>Tools:</b> Adobe Illustrator | Adobe Photoshop | Adobe Lightroom | Figma", s["body"]))

    section(story, "Selected Links", s)
    story.append(Paragraph(
        link("Portfolio", "https://khalil-m-khalil.github.io/") + " &nbsp;|&nbsp; "
        + link("Work archive", "https://drive.google.com/drive/folders/1rTo1E-fPrPY6pIhvT161_SrQnGuniPov?usp=sharing") + " &nbsp;|&nbsp; "
        + link("Training evidence", "https://drive.google.com/drive/folders/13GqGvguyTr6kWKUW5x6vtzwh6g4zrEBA?usp=drive_link") + " &nbsp;|&nbsp; "
        + link("Instagram @khalil_m_khalil09", "https://www.instagram.com/khalil_m_khalil09/"), s["body"]))
    story.append(Paragraph("<b>Languages:</b> Arabic (native) | English (professional)", s["body"]))
    CVDoc(str(OUT / "Khalil_Khalil_CV_Creative.pdf")).build(story)


def build_technical():
    s = make_styles(); story = []
    header(story, "Security Research | Web Development | Digital Forensics (Learning)", s)
    section(story, "Profile", s)
    story.append(Paragraph("Computer Science student at the University of the People and independent security researcher. I am also a law graduate from Hawash Private University in Syria. I document vulnerabilities, build web tools, and practise digital forensics and Linux-based analysis as a learning-focused technical track.", s["body"]))

    section(story, "Experience", s)
    story.append(role_block("Web Developer & Technical Content Writer", "Freelance, remote", "2022 – Present", [
        "Built responsive portfolio and landing-page websites using HTML, CSS and JavaScript.",
        "Developed local-first tools and interfaces, including the Phoenix verification dashboard and Nabra keyboard-layout utility.",
        "Authored Arabic-language technical training materials on Linux and cybersecurity.",
    ], s))
    story.append(Spacer(1, 3))
    story.append(role_block("Independent Security Researcher", "Self-directed research", "2024 – Present", [
        "Documented a race-condition vulnerability in an email-confirmation workflow and produced a technical report covering methodology and impact.",
        "The research was highlighted by OffSec in March 2026; additional open-redirect research is documented in the research archive.",
    ], s))
    story.append(Spacer(1, 3))
    story.append(role_block("Technical Training & Career Guidance", "Independent, remote", "Ongoing", [
        "Trained and supported 100+ learners across programming, web development, cybersecurity and career readiness.",
        "Prepared structured course files, study roadmaps, practice plans and field research for learners.",
    ], s))

    section(story, "Recognition &amp; Selected Projects", s)
    for item in [
        ("OffSec highlight", "Recognition", "Race-condition research on a Meta platform highlighted in March 2026.", "https://drive.google.com/drive/folders/1HXxHzGPUjzUS0UELDB2VLeCQS-KJ0T_A?usp=drive_link"),
        ("Horizon Lab", "Digital forensics", "Ranked #1 in Syria and #177 worldwide with a 93% score using Phoenix.", "https://drive.google.com/drive/folders/1fVV4dVbT0LvDbXnkb4AqCLJVFaOdKqos?usp=drive_link"),
        ("Phoenix", "Local verification dashboard", "A local analysis and digital-forensics tool used in the Horizon Lab competition.", "https://khalil-m-khalil.github.io/Phoenix/"),
        ("Nabra", "Windows utility", "Local Arabic/English keyboard-layout conversion without translation or cloud processing.", "https://drive.google.com/drive/folders/1CDHuI3SuQ9POROOW8RtkNexvn0x_kEOS?usp=drive_link"),
    ]:
        story.extend(project_row(*item, s)); story.append(Spacer(1, 1))

    section(story, "Education", s)
    story.append(education_row("BSc Computer Science (in progress)", "University of the People (UoPeople), online", "2023 – Present", s))
    story.append(education_row("Bachelor of Law", "Hawash Private University (HPU), Homs, Syria", "Graduated", s))

    section(story, "Technical Skills", s)
    story.append(Paragraph("<b>Web:</b> HTML | CSS | JavaScript | responsive interfaces &amp; local-first tools", s["body"]))
    story.append(Paragraph("<b>Security &amp; systems:</b> Vulnerability research | Linux &amp; command line | security awareness &amp; GRC (learning) | digital forensics (learning)", s["body"]))
    story.append(Paragraph("<b>Hands-on practice:</b> Wireshark | tcpdump | Nmap | UFW | Sleuth Kit | Autopsy | Plaso | Foremost | TestDisk | ExifTool | Volatility 3 | Debian", s["body"]))

    section(story, "Links &amp; Languages", s)
    story.append(Paragraph(
        link("Portfolio", "https://khalil-m-khalil.github.io/") + " &nbsp;|&nbsp; "
        + link("GitHub", "https://github.com/Khalil-M-Khalil") + " &nbsp;|&nbsp; "
        + link("Training evidence", "https://drive.google.com/drive/folders/13GqGvguyTr6kWKUW5x6vtzwh6g4zrEBA?usp=drive_link") + " &nbsp;|&nbsp; "
        + link("Research archive", "https://drive.google.com/drive/folders/1HXxHzGPUjzUS0UELDB2VLeCQS-KJ0T_A?usp=drive_link"), s["small"]))
    story.append(Paragraph("<b>Languages:</b> Arabic (native) | English (professional)", s["body"]))
    CVDoc(str(OUT / "Khalil_Khalil_CV_Technical.pdf")).build(story)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    build_creative()
    build_technical()
    print("Generated:")
    print(OUT / "Khalil_Khalil_CV_Creative.pdf")
    print(OUT / "Khalil_Khalil_CV_Technical.pdf")
