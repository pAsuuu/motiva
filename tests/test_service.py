import unittest
import io
import pypdf
from fastapi.testclient import TestClient
from app.main import app
from app.cv_parser import CVParser
from app.pdf_generator import PDFGenerator
from app.prompt_engine import PromptEngine
from app.ai_generator import AIGenerator

class TestMotivaService(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_status_endpoint(self):
        response = self.client.get("/api/status")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ready")

    def test_cv_parser_contact_info(self):
        sample_cv = """
Dany Ferreira
Lead Cloud Engineer
dany.ferreira@epitech.digital
06 99 88 77 66
Paris, France

Expérience:
- Architecture AWS haute disponibilité
"""
        parsed = CVParser.parse("cv.txt", sample_cv.encode("utf-8"))
        self.assertEqual(parsed["contact"]["name"], "Dany Ferreira")
        self.assertEqual(parsed["contact"]["email"], "dany.ferreira@epitech.digital")
        self.assertEqual(parsed["contact"]["phone"], "06 99 88 77 66")

    def test_candidate_contact_preservation_in_generation(self):
        payload = {
            "cv_text": "Dany Ferreira\nLead Cloud Engineer\ndany.ferreira@epitech.digital\n06 99 88 77 66",
            "company_name": "Alan",
            "job_title": "Lead Cloud",
            "candidate_contact": {
                "name": "Dany Ferreira",
                "email": "dany.ferreira@epitech.digital",
                "phone": "06 99 88 77 66",
                "location": "Paris, France"
            }
        }
        res = self.client.post("/api/generate-letter", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["candidate"]["email"], "dany.ferreira@epitech.digital")
        self.assertEqual(data["candidate"]["phone"], "06 99 88 77 66")
        self.assertEqual(data["candidate"]["name"], "Dany Ferreira")

    def test_pdf_export_contains_real_email_and_phone(self):
        payload = {
            "letter_data": {
                "candidate": {
                    "name": "Dany Ferreira",
                    "headline": "Lead Cloud Engineer",
                    "email": "dany.ferreira@epitech.digital",
                    "phone": "06 99 88 77 66",
                    "location": "Paris, France"
                },
                "recipient": {"company": "Alan Health", "department": "Tech", "city": "Paris"},
                "meta": {"date": "10/09/2026", "subject": "Objet : Candidature"},
                "letter_content": {
                    "salutation": "Bonjour,",
                    "paragraph_hook": "Accroche percutante.",
                    "paragraph_experience": "Réalisations concrètes.",
                    "paragraph_team_fit": "Fit équipe.",
                    "paragraph_call_to_action": "Échangeons.",
                    "valediction": "Cordialement,",
                    "signature": "Dany Ferreira"
                }
            },
            "theme": "modern"
        }
        res = self.client.post("/api/export-pdf", json=payload)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers["content-type"], "application/pdf")
        
        # Verify text extracted from generated PDF
        reader = pypdf.PdfReader(io.BytesIO(res.content))
        text = reader.pages[0].extract_text()
        self.assertIn("dany.ferreira@epitech.digital", text)
        self.assertIn("06 99 88 77 66", text)

if __name__ == "__main__":
    unittest.main()
