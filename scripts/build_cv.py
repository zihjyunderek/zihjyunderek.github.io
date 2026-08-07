"""Generate the one-page CV PDF published at ``/cv/`` on the portfolio site.

The CV is a build artifact, not a hand-edited document: all wording lives in
the DATA block below, and the layout is applied by code. To update the CV,
edit the DATA block and re-run this script.

    python scripts/build_cv.py

Design contract:
  * One typeface, Lato (Google Fonts, OFL). Humanist sans with rounded
    terminals: smooth at small sizes and quiet on the page. The four faces
    live in ``scripts/fonts/``, subset to Latin, so the PDF renders
    identically on any machine and nothing needs installing.
  * Greyscale only. Near-black text, one grey for secondary lines, one light
    grey for rules. No accent color: on a CV, color is noise.
  * Structure comes from rules and whitespace, not from decoration. Each
    section is a label over a hairline; each entry is a two-line head
    (organization and date, then role and place) followed by plain bullets.
  * Sentence case only, matching the site. Date ranges use an en dash.
  * Body text is set ragged right. The site justifies with hyphenation;
    a PDF has none, so justifying this measure would open rivers.

One-page guarantee: the script renders from the largest scale down and keeps
the first result that fits on a single page, so the CV grows to fill the page
as well as shrinking to fit it. If even the tightest scale overflows, it fails
loudly instead of shipping a two-page CV, which means an over-long DATA block
is caught at build time rather than by a recruiter.

Requires: ``pip install reportlab``
"""

from __future__ import annotations

import io
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
    Frame,
    KeepTogether,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

# ==========================================================================
# [Config] Output location, page geometry, typography, palette
# ==========================================================================

REPO_ROOT = Path(__file__).resolve().parent.parent
FONT_DIR = Path(__file__).resolve().parent / "fonts"
OUTPUT_PATH = REPO_ROOT / "public" / "cv" / "ZihJyunHuang_CV_en.pdf"

PAGE_SIZE = LETTER
MARGIN_X = 0.68 * inch
MARGIN_Y = 0.48 * inch

FONT = "Lato"
FONT_BOLD = "Lato-Bold"
FONT_ITALIC = "Lato-Italic"

# Type scale measured off the reference CV: 11 pt body, 12 pt entry heads
# and section labels, 18 pt name. FIT_SCALES then shrinks the whole scale
# uniformly until the page fits, so these stay the proportions, not the
# final sizes; the script reports what it actually used.
BODY_PT = 11.0
HEAD_PT = 12.0

# Greyscale only. Anything more reads as decoration on a one-page CV.
INK = colors.HexColor("#1A1A1A")      # headings and body
INK_DIM = colors.HexColor("#565656")  # roles, dates, contact line
RULE = colors.HexColor("#7D7D7D")     # section hairlines

# Tried largest first; the first scale that renders on one page wins, so
# the CV grows to fill the page as well as shrinking to fit it. The step is
# small because entries are kept whole, so one step can move a whole block.
FIT_SCALES = tuple(round(1.14 - 0.01 * i, 2) for i in range(30))

# ==========================================================================
# [Data] CV content. Mirror of src/data/profile.ts: edit both together.
# ==========================================================================

NAME = "Zih-Jyun (Derek) Huang"
CONTACT = [
    "derek4953098@gmail.com",
    "zihjyunderek.github.io",
    "linkedin.com/in/derekhuang0426",
    "github.com/zihjyunderek",
]

EDUCATION = [
    {
        "org": "National Chengchi University",
        "role": "M.S. Money and Banking",
        "meta": "GPA 4.21 / 4.3",
        "when": "2024 – 2026",
        "bullets": [
            "Thesis: Forecasting FX spot Value-at-Risk using implied "
            "volatility, evidence from G7 currency pairs.",
        ],
    },
    {
        "org": "National Taiwan University",
        "role": "B.A. Economics",
        "meta": "GPA 3.6 / 4.3",
        "when": "2020 – 2024",
        "bullets": [],
    },
]

EXPERIENCE = [
    {
        "org": "CTBC Bank",
        "role": "Incoming Management Associate, Risk Management",
        "meta": "Taipei, Taiwan",
        "when": "2027/02 (expected)",
        "bullets": [],
    },
    {
        "org": "Republic of China Army",
        "role": "Compulsory Military Service",
        "meta": "Taiwan",
        "when": "2026/08 – 2026/12",
        "bullets": [],
    },
    {
        "org": "Gensler Research Institute",
        "role": "Data Analyst, Cities Research",
        "meta": "New York, United States (remote)",
        "when": "2025/02 – 2026/08",
        "bullets": [
            "Built geospatial regression models (MGWR, PyGRF) linking 137 "
            "urban indicators to city satisfaction across 31 major US cities.",
            "Flagship study: Decoding the City, Unveiling NYC's Geographical "
            "Phenomena with MGWR.",
        ],
    },
    {
        "org": "CTBC Bank",
        "role": "Intern, Market Risk Management (MRMD)",
        "meta": "Taipei, Taiwan",
        "when": "2025/10 – 2026/02",
        "bullets": [
            "Designed dealer risk-management mechanisms for stablecoins under "
            "Basel SCO60 capital standards.",
        ],
    },
    {
        "org": "Hon Hai Precision (Foxconn)",
        "role": "Summer Intern, Risk Management",
        "meta": "New Taipei, Taiwan",
        "when": "2025/08 – 2025/09",
        "bullets": [
            "Forecast FX around key macro events with the treasury 5+1 "
            "framework; reconciled trade records for AR/AP positions.",
        ],
    },
    {
        "org": "CTBC Bank",
        "role": "Summer Intern, Market Risk Management (MRMD)",
        "meta": "Taipei, Taiwan",
        "when": "2025/07 – 2025/08",
        "bullets": [
            "Forecast VaR for major FX pairs using quantile regression and "
            "implied volatility.",
        ],
    },
    {
        "org": "Chung-hua Institution for Economic Research (CIER)",
        "role": "Project Assistant, First Division",
        "meta": "Taipei, Taiwan",
        "when": "2023/06 – 2023/12",
        "bullets": [
            "Analyzed China's macroeconomy, wrote for the Trade Insight "
            "bi-weekly, and built an internal economic database.",
        ],
    },
]

HONORS = [
    {
        "org": "CFA Research Challenge, Taiwan Final",
        "role": "2nd Place, Best Written Report",
        "meta": "CFA Society Taiwan",
        "when": "2022/09 – 2023/05",
        "bullets": [],
    },
]

SKILLS = [
    (
        "Methods",
        "Spatial statistics (MGWR, GWPCA, PyGRF), clustering, composite "
        "indices, Value at Risk, machine learning.",
    ),
    (
        "Tools",
        "Python (primary), R, Stata, EViews, Power BI, LaTeX, Git, Docker, "
        "Asana, agentic LLM workflows.",
    ),
    (
        "Certificates",
        "Futures Specialist; Securities Investment Trust and Consulting "
        "Professional; Senior Securities Specialist.",
    ),
    (
        "Languages",
        "Traditional Chinese (native), English (proficient).",
    ),
]


# ==========================================================================
# [Core Logic] Fonts, flowables, and styles
# ==========================================================================


def register_fonts() -> None:
    """Register the bundled Lato faces, including the bold and italic map.

    Fails fast: a missing face would silently fall back to Helvetica and
    ship a CV that does not match the design.
    """
    faces = {
        FONT: "Lato-Regular.ttf",
        FONT_BOLD: "Lato-Bold.ttf",
        FONT_ITALIC: "Lato-Italic.ttf",
        "Lato-BoldItalic": "Lato-BoldItalic.ttf",
    }
    for name, filename in faces.items():
        path = FONT_DIR / filename
        if not path.exists():
            raise FileNotFoundError(
                f"Missing font face: {path}. The four Lato TTFs must be "
                f"present in {FONT_DIR.name}/ for the CV to render."
            )
        pdfmetrics.registerFont(TTFont(name, str(path)))

    pdfmetrics.registerFontFamily(
        FONT, normal=FONT, bold=FONT_BOLD,
        italic=FONT_ITALIC, boldItalic="Lato-BoldItalic",
    )


class HorizontalRule(Flowable):
    """A full-width hairline: the only structural device on the page."""

    def __init__(self, width: float, thickness: float = 0.5,
                 color: colors.Color = RULE) -> None:
        super().__init__()
        self.width = width
        self.thickness = thickness
        self.color = color
        self.height = thickness

    def draw(self) -> None:
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.thickness)
        self.canv.line(0, 0, self.width, 0)


def build_styles(scale: float) -> dict[str, ParagraphStyle]:
    """Return the paragraph styles for one render pass at a given scale."""
    def size(pt: float) -> float:
        return round(pt * scale, 2)

    body = size(BODY_PT)
    head = size(HEAD_PT)
    return {
        "name": ParagraphStyle(
            "name", fontName=FONT_BOLD, fontSize=size(19.5),
            leading=size(21.5), textColor=INK, alignment=TA_CENTER,
        ),
        "contact": ParagraphStyle(
            "contact", fontName=FONT, fontSize=size(10.0),
            leading=size(12.5), textColor=INK_DIM, alignment=TA_CENTER,
        ),
        "section": ParagraphStyle(
            "section", fontName=FONT_BOLD, fontSize=head,
            leading=size(HEAD_PT * 1.30), textColor=INK,
        ),
        "org": ParagraphStyle(
            "org", fontName=FONT_BOLD, fontSize=head,
            leading=size(HEAD_PT * 1.34), textColor=INK,
        ),
        "when": ParagraphStyle(
            "when", fontName=FONT_BOLD, fontSize=head,
            leading=size(HEAD_PT * 1.34), textColor=INK, alignment=TA_RIGHT,
        ),
        "role": ParagraphStyle(
            "role", fontName=FONT_ITALIC, fontSize=head,
            leading=size(HEAD_PT * 1.30), textColor=INK_DIM,
        ),
        "place": ParagraphStyle(
            "place", fontName=FONT_ITALIC, fontSize=head,
            leading=size(HEAD_PT * 1.30), textColor=INK_DIM, alignment=TA_RIGHT,
        ),
        "bullet": ParagraphStyle(
            "bullet", fontName=FONT, fontSize=body,
            leading=size(BODY_PT * 1.28), textColor=INK,
            leftIndent=size(15), bulletIndent=size(2),
            bulletFontName=FONT, bulletFontSize=body,
            spaceAfter=size(1.2),
        ),
        "skill_label": ParagraphStyle(
            "skill_label", fontName=FONT_BOLD, fontSize=body,
            leading=size(BODY_PT * 1.28), textColor=INK,
        ),
        "skill_body": ParagraphStyle(
            "skill_body", fontName=FONT, fontSize=body,
            leading=size(BODY_PT * 1.28), textColor=INK,
        ),
    }


def two_column_row(left: Paragraph, right: Paragraph, width: float,
                   split: float = 0.66) -> Table:
    """A flush left and flush right pair on one baseline, with no padding."""
    table = Table([[left, right]], colWidths=[width * split, width * (1 - split)])
    table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return table


def section_heading(text: str, styles: dict[str, ParagraphStyle],
                    width: float, scale: float) -> KeepTogether:
    """Section label over a hairline, kept with whatever follows it."""
    return KeepTogether([
        Spacer(1, 6.0 * scale),
        Paragraph(text, styles["section"]),
        Spacer(1, 2.2 * scale),
        HorizontalRule(width, thickness=0.7, color=RULE),
        Spacer(1, 3.5 * scale),
    ])


def entry_block(entry: dict, styles: dict[str, ParagraphStyle],
                width: float, scale: float) -> KeepTogether:
    """One entry: organization and date, then role and place, then bullets."""
    parts: list[Flowable] = [
        two_column_row(
            Paragraph(entry["org"], styles["org"]),
            Paragraph(entry["when"], styles["when"]),
            width,
        ),
        two_column_row(
            Paragraph(entry["role"], styles["role"]),
            Paragraph(entry.get("meta", ""), styles["place"]),
            width,
        ),
    ]
    if entry["bullets"]:
        parts.append(Spacer(1, 2.0 * scale))
        for text in entry["bullets"]:
            parts.append(Paragraph(text, styles["bullet"], bulletText="•"))
    parts.append(Spacer(1, 3.5 * scale))
    return KeepTogether(parts)


def skills_table(styles: dict[str, ParagraphStyle], width: float,
                 scale: float) -> Table:
    """Label and body in two columns, so wrapped lines stay left-aligned.

    The label column is sized from the widest label the DATA block declares,
    so adding a longer label re-aligns the whole block automatically.
    """
    label_width = 9 * scale + max(
        stringWidth(label, FONT_BOLD, styles["skill_label"].fontSize)
        for label, _ in SKILLS
    )
    table = Table(
        [[Paragraph(label, styles["skill_label"]),
          Paragraph(body, styles["skill_body"])] for label, body in SKILLS],
        colWidths=[label_width, width - label_width],
    )
    table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.4 * scale),
    ]))
    return table


def build_story(styles: dict[str, ParagraphStyle], width: float,
                scale: float) -> list[Flowable]:
    """Assemble the full flowable sequence for one render pass."""
    story: list[Flowable] = [
        Paragraph(NAME, styles["name"]),
        Spacer(1, 2.0 * scale),
        Paragraph("&nbsp;&nbsp;|&nbsp;&nbsp;".join(CONTACT), styles["contact"]),
    ]

    for label, entries in (
        ("Education", EDUCATION),
        ("Experience", EXPERIENCE),
        ("Honors", HONORS),
    ):
        story.append(section_heading(label, styles, width, scale))
        story.extend(entry_block(e, styles, width, scale) for e in entries)

    story.append(section_heading("Skills and certificates", styles, width, scale))
    story.append(skills_table(styles, width, scale))
    return story


def render(scale: float) -> tuple[bytes, int]:
    """Render the CV at one scale. Returns the PDF bytes and the page count."""
    buffer = io.BytesIO()
    doc = BaseDocTemplate(
        buffer,
        pagesize=PAGE_SIZE,
        leftMargin=MARGIN_X, rightMargin=MARGIN_X,
        topMargin=MARGIN_Y, bottomMargin=MARGIN_Y,
        title=f"{NAME} CV", author=NAME,
        subject="Curriculum vitae", creator="scripts/build_cv.py",
        # Freeze the embedded timestamp and document ID so an unchanged CV
        # rebuilds byte-identical, keeping the tracked binary out of diffs.
        invariant=1,
    )
    frame = Frame(
        doc.leftMargin, doc.bottomMargin, doc.width, doc.height,
        leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
    )
    doc.addPageTemplates([PageTemplate(id="cv", frames=[frame])])

    styles = build_styles(scale)
    doc.build(build_story(styles, doc.width, scale))
    return buffer.getvalue(), doc.page


def main() -> int:
    """Render at successively tighter scales and write the first one-pager."""
    print("\n--- Build CV ---")
    print(f"  > Target: {OUTPUT_PATH.relative_to(REPO_ROOT)}")
    register_fonts()
    print(f"  > Fonts: Lato, 4 faces from {FONT_DIR.name}/")

    for scale in FIT_SCALES:
        pdf_bytes, pages = render(scale)
        print(f"  > scale {scale:.2f} -> {pages} page(s)")
        if pages == 1:
            OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
            OUTPUT_PATH.write_bytes(pdf_bytes)
            styles = build_styles(scale)
            print(f"  > Written at scale {scale:.2f}: body "
                  f"{styles['bullet'].fontSize} pt, head "
                  f"{styles['org'].fontSize} pt, name "
                  f"{styles['name'].fontSize} pt "
                  f"({len(pdf_bytes) / 1024:.1f} KB)")
            return 0

    print("  ! No scale in FIT_SCALES fits on one page.", file=sys.stderr)
    print("  ! Cut content from the DATA block; do not loosen the limit.",
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
