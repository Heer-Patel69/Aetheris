import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

MD_PATH = r"c:\AI\Agency owner\.aetheris\review\AETHERIS_MASTER_ARCHITECTURE_REVIEW.md"
PDF_PATH = r"c:\AI\Agency owner\.aetheris\review\ARB_Master_Report.pdf"

def generate_pdf():
    print("Generating PDF from Master Report...")
    if not os.path.exists(MD_PATH):
        print(f"MD file not found: {MD_PATH}")
        return
        
    with open(MD_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    doc = SimpleDocTemplate(PDF_PATH, pagesize=letter,
                            rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1A365D'),
        spaceAfter=15
    )
    h2_style = ParagraphStyle(
        'DocH2',
        parent=styles['Heading2'],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#2B6CB0'),
        spaceBefore=12,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#2D3748'),
        spaceAfter=8
    )
    code_style = ParagraphStyle(
        'DocCode',
        parent=styles['Code'],
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#1A202C'),
        backColor=colors.HexColor('#EDF2F7'),
        borderPadding=6,
        spaceAfter=8
    )

    in_code_block = False
    code_lines = []
    
    for line in lines:
        stripped = line.strip()
        
        # Code block handling
        if stripped.startswith("```"):
            if in_code_block:
                in_code_block = False
                code_text = "<br/>".join(code_lines)
                story.append(Paragraph(code_text, code_style))
                code_lines = []
            else:
                in_code_block = True
            continue
            
        if in_code_block:
            # Escape HTML characters for ReportLab Paragraph
            escaped = stripped.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            code_lines.append(escaped)
            continue
            
        if not stripped:
            continue
            
        # Headers
        if stripped.startswith("# "):
            text = stripped[2:]
            story.append(Paragraph(text, title_style))
            story.append(Spacer(1, 10))
        elif stripped.startswith("## "):
            text = stripped[3:]
            story.append(Paragraph(text, h2_style))
        elif stripped.startswith("### "):
            text = stripped[4:]
            story.append(Paragraph(text, h2_style))
        else:
            # Simple markdown cleanups (bullets, bold)
            text = stripped
            if text.startswith("* ") or text.startswith("- "):
                text = f"&bull; {text[2:]}"
            text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
            text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            story.append(Paragraph(text, body_style))
            
    doc.build(story)
    print(f"Successfully generated PDF at {PDF_PATH}")

if __name__ == "__main__":
    import re
    generate_pdf()
