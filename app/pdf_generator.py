import io
from typing import Dict, Any
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.units import mm

class PDFGenerator:
    """Generates high-precision, elegant single-page A4 cover letters in PDF format."""

    THEMES = {
        "modern": {
            "primary": colors.HexColor("#0f172a"),    # Slate 900
            "accent": colors.HexColor("#2563eb"),     # Tech Blue
            "text": colors.HexColor("#334155"),       # Slate 700
            "muted": colors.HexColor("#64748b"),      # Slate 500
            "line": colors.HexColor("#cbd5e1")
        },
        "executive": {
            "primary": colors.HexColor("#09090b"),    # Jet Black
            "accent": colors.HexColor("#831843"),     # Wine / Burgundy
            "text": colors.HexColor("#1e293b"),
            "muted": colors.HexColor("#475569"),
            "line": colors.HexColor("#cbd5e1")
        },
        "minimal": {
            "primary": colors.HexColor("#18181b"),    # Zinc 900
            "accent": colors.HexColor("#09090b"),     # Black
            "text": colors.HexColor("#27272a"),
            "muted": colors.HexColor("#71717a"),
            "line": colors.HexColor("#e4e4e7")
        }
    }

    @classmethod
    def generate_pdf(cls, letter_data: Dict[str, Any], theme_name: str = "modern") -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=20*mm,
            rightMargin=20*mm,
            topMargin=18*mm,
            bottomMargin=18*mm
        )

        theme = cls.THEMES.get(theme_name, cls.THEMES["modern"])
        styles = getSampleStyleSheet()

        candidate_name_style = ParagraphStyle(
            'CandidateName',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=15,
            leading=18,
            textColor=theme["primary"]
        )
        
        candidate_sub_style = ParagraphStyle(
            'CandidateSub',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=13.5,
            textColor=theme["muted"]
        )

        recipient_style = ParagraphStyle(
            'RecipientStyle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9.5,
            leading=14,
            alignment=2, # Right aligned
            textColor=theme["text"]
        )

        date_style = ParagraphStyle(
            'DateStyle',
            parent=styles['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=9,
            leading=12,
            alignment=2, # Right aligned
            textColor=theme["muted"]
        )

        subject_style = ParagraphStyle(
            'SubjectStyle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=10.5,
            leading=14.5,
            textColor=theme["accent"]
        )

        body_style = ParagraphStyle(
            'BodyStyle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9.5,
            leading=14.5,
            textColor=theme["text"],
            alignment=4 # Justified
        )

        signature_style = ParagraphStyle(
            'SignatureStyle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=10.5,
            leading=15,
            textColor=theme["primary"]
        )

        story = []

        candidate = letter_data.get("candidate", {})
        recipient = letter_data.get("recipient", {})
        meta = letter_data.get("meta", {})
        content = letter_data.get("letter_content", {})

        # Build candidate contact line with bullet separator
        cand_name = candidate.get('name', 'Candidat')
        cand_headline = candidate.get('headline', '')
        email = candidate.get('email', '')
        phone = candidate.get('phone', '')
        location = candidate.get('location', '')

        cand_text = f"<b><font size=13 color='{theme['primary'].hexval()}'>{cand_name}</font></b><br/>"
        if cand_headline:
            cand_text += f"<font size=9.5 color='{theme['muted'].hexval()}'>{cand_headline}</font><br/>"
        
        # Details row
        details = []
        if email: details.append(f"<b>Email:</b> {email}")
        if phone: details.append(f"<b>Tél:</b> {phone}")
        if location: details.append(location)

        if details:
            cand_text += f"<font size=8.5 color='{theme['text'].hexval()}'>" + " &bull; ".join(details) + "</font>"

        # Recipient text
        recip_company = recipient.get('company', 'Entreprise')
        recip_dept = recipient.get('department', 'Direction du Recrutement')
        recip_city = recipient.get('city', '')

        recip_text = f"<b><font size=11 color='{theme['primary'].hexval()}'>{recip_company}</font></b><br/>"
        if recip_dept:
            recip_text += f"<font size=9 color='{theme['muted'].hexval()}'>{recip_dept}</font><br/>"
        if recip_city:
            recip_text += f"<font size=9 color='{theme['muted'].hexval()}'>{recip_city}</font>"

        header_table = Table(
            [[
                Paragraph(cand_text, candidate_sub_style),
                Paragraph(recip_text, recipient_style)
            ]],
            colWidths=[105*mm, 65*mm]
        )
        header_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('ALIGN', (1,0), (1,0), 'RIGHT'),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 4*mm))

        # Thin Accent Line
        story.append(HRFlowable(width="100%", thickness=1.5, color=theme["line"], spaceBefore=0, spaceAfter=4*mm))

        # Date Line
        date_val = meta.get("date", "")
        if date_val:
            story.append(Paragraph(date_val, date_style))
            story.append(Spacer(1, 3*mm))

        # Subject Line
        subject_val = meta.get("subject", "Objet : Candidature")
        story.append(Paragraph(subject_val, subject_style))
        story.append(Spacer(1, 4.5*mm))

        # Salutation
        salutation = content.get("salutation", "Madame, Monsieur,")
        story.append(Paragraph(f"<b>{salutation}</b>", body_style))
        story.append(Spacer(1, 3*mm))

        # Paragraphs
        paragraphs = [
            content.get("paragraph_hook", ""),
            content.get("paragraph_experience", ""),
            content.get("paragraph_team_fit", ""),
            content.get("paragraph_call_to_action", "")
        ]

        for p in paragraphs:
            if p and p.strip():
                story.append(Paragraph(p.strip(), body_style))
                story.append(Spacer(1, 3.2*mm))

        # Valediction & Signature
        valediction = content.get("valediction", "Bien cordialement,")
        sig_name = content.get("signature", cand_name)

        story.append(Spacer(1, 2*mm))
        story.append(Paragraph(valediction, body_style))
        story.append(Spacer(1, 3.5*mm))
        story.append(Paragraph(sig_name, signature_style))

        # Build PDF
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
