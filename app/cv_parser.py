import re
import io
from typing import Dict, Any, Optional

class CVParser:
    """Parses CV files (PDF, DOCX, TXT) and extracts structured data with high precision."""

    @staticmethod
    def extract_text_from_pdf(file_bytes: bytes) -> str:
        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            text_parts = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            return "\n\n".join(text_parts).strip()
        except Exception as e:
            return f"Erreur lors de la lecture du PDF: {str(e)}"

    @staticmethod
    def extract_text_from_docx(file_bytes: bytes) -> str:
        try:
            import docx
            doc = docx.Document(io.BytesIO(file_bytes))
            text_parts = []
            for para in doc.paragraphs:
                if para.text.strip():
                    text_parts.append(para.text.strip())
            for table in doc.tables:
                for row in table.rows:
                    row_texts = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                    if row_texts:
                        text_parts.append(" | ".join(row_texts))
            return "\n".join(text_parts).strip()
        except Exception as e:
            return f"Erreur lors de la lecture du DOCX: {str(e)}"

    @staticmethod
    def extract_contact_info(text: str) -> Dict[str, str]:
        # Robust Email regex
        email_match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
        email = email_match.group(0).strip() if email_match else ""

        # French & international phone formats:
        # e.g. 06 12 34 56 78, 06.12.34.56.78, 0612345678, +33 6 12 34 56 78, 0033 6...
        phone_patterns = [
            r'(?:(?:\+|00)33[\s.-]?(?:\(0\)[\s.-]?)?|0)[1-9](?:[\s.-]?\d{2}){4}',
            r'\+?\d{1,3}[\s.-]?(?:\(?\d{2,4}\)?[\s.-]?)?\d{2,4}[\s.-]?\d{2,4}',
            r'0[67]\d{8}'
        ]
        phone = ""
        for pattern in phone_patterns:
            match = re.search(pattern, text)
            if match:
                phone = match.group(0).strip()
                break

        # Location heuristic: search for common French cities or zip code
        location = ""
        zip_match = re.search(r'\b(?:75|69|13|31|33|44|59|67|06|34|35|38|83|92|93|94|78|91|95)\d{3}\b', text)
        city_match = re.search(r'\b(Paris|Lyon|Marseille|Toulouse|Bordeaux|Nantes|Lille|Strasbourg|Nice|Montpellier|Rennes|Grenoble|Rouen|Toulon|Angers|Dijon|Brest|Le Mans|Aix-en-Provence|Clermont-Ferrand)\b', text, re.IGNORECASE)
        if city_match:
            location = city_match.group(1).title() + ", France"
        elif zip_match:
            location = "France"

        lines = [line.strip() for line in text.splitlines() if line.strip()]
        name = ""
        headline = ""

        # Find first line with 2-4 words, capitalized, no digits, no email
        for i, line in enumerate(lines[:8]):
            cleaned = re.sub(r'[^\w\s-]', '', line).strip()
            words = cleaned.split()
            if 2 <= len(words) <= 4 and not re.search(r'\d|@|www|http|linkedin|github', line, re.IGNORECASE):
                if not any(header in line.lower() for header in ["curriculum", "resume", "cv", "profil", "expérience", "formation", "contact", "compétences"]):
                    name = line
                    # Look ahead for headline
                    for next_line in lines[i+1:i+4]:
                        if not re.search(r'@|\d{4}|http|tel', next_line, re.IGNORECASE) and 5 < len(next_line) < 70:
                            headline = next_line
                            break
                    break

        return {
            "name": name,
            "email": email,
            "phone": phone,
            "location": location,
            "headline": headline
        }

    @classmethod
    def parse(cls, filename: str, file_bytes: bytes) -> Dict[str, Any]:
        lower_fn = filename.lower()
        if lower_fn.endswith('.pdf'):
            text = cls.extract_text_from_pdf(file_bytes)
        elif lower_fn.endswith(('.docx', '.doc')):
            text = cls.extract_text_from_docx(file_bytes)
        else:
            try:
                text = file_bytes.decode('utf-8', errors='replace')
            except Exception:
                text = str(file_bytes)

        contact = cls.extract_contact_info(text)

        return {
            "filename": filename,
            "raw_text": text,
            "contact": contact,
            "char_count": len(text)
        }
