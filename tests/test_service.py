import unittest
import io
import pypdf
from fastapi.testclient import TestClient
from app.main import app
from app.cv_parser import CVParser
from app.job_analyzer import JobAnalyzer
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

    def test_job_analyzer_stellantis_case(self):
        raw_title = "Stellantis recrute pour des postes de Apprentissage : Assistant chef de projet marketing"
        meta = JobAnalyzer.clean_job_title(raw_title)
        self.assertEqual(meta["company_name"], "Stellantis")
        self.assertEqual(meta["clean_title"], "Assistant Chef de Projet Marketing")
        self.assertEqual(meta["contract_type"], "Apprentissage")
        self.assertEqual(meta["department"], "Direction Marketing & Communication")
        self.assertIn("Assistant Chef de Projet Marketing (Apprentissage)", meta["clean_subject"])

    def test_api_analyze_job_endpoint(self):
        payload = {
            "raw_title": "Stellantis recrute pour des postes de Apprentissage : Assistant chef de projet marketing",
            "company_name": ""
        }
        res = self.client.post("/api/analyze-job", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["company_name"], "Stellantis")
        self.assertEqual(data["clean_title"], "Assistant Chef de Projet Marketing")
        self.assertEqual(data["contract_type"], "Apprentissage")
        self.assertIn("Dare Forward 2030", data["deep_context"].get("strategy", ""))

    def test_generation_stellantis_smart_hook(self):
        payload = {
            "cv_text": "Dany Ferreira\nChef de projet junior\ndany.ferreira@epitech.digital\n06 99 88 77 66",
            "company_name": "Stellantis",
            "job_title": "Stellantis recrute pour des postes de Apprentissage : Assistant chef de projet marketing",
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

        # Subject must be clean and not have "recrute pour des postes de"
        subject = data["meta"]["subject"]
        self.assertNotIn("recrute pour", subject)
        self.assertIn("Assistant Chef de Projet Marketing", subject)
        self.assertIn("Apprentissage", subject)

        # Hook must reference Stellantis strategic context
        hook = data["letter_content"]["paragraph_hook"]
        self.assertIn("Stellantis", hook)
        self.assertTrue("Dare Forward" in hook or "mobilité" in hook or "marques" in hook)

    def test_pdf_export_with_clean_title_and_contacts(self):
        payload = {
            "letter_data": {
                "candidate": {
                    "name": "Dany Ferreira",
                    "headline": "Assistant Chef de Projet Marketing",
                    "email": "dany.ferreira@epitech.digital",
                    "phone": "06 99 88 77 66",
                    "location": "Paris, France"
                },
                "recipient": {
                    "company": "Stellantis",
                    "department": "Direction Marketing & Communication",
                    "city": "Poissy, France"
                },
                "meta": {
                    "date": "10 septembre 2026",
                    "subject": "Objet : Candidature au poste de Assistant Chef de Projet Marketing (Apprentissage)"
                },
                "letter_content": {
                    "salutation": "Madame, Monsieur,",
                    "paragraph_hook": "La trajectoire du groupe Stellantis...",
                    "paragraph_experience": "Au cours de mes projets en gestion...",
                    "paragraph_team_fit": "Intégrer la Direction Marketing...",
                    "paragraph_call_to_action": "Je serais ravi d'échanger 15 minutes.",
                    "valediction": "Bien cordialement,",
                    "signature": "Dany Ferreira"
                }
            },
            "theme": "modern"
        }
        res = self.client.post("/api/export-pdf", json=payload)
        self.assertEqual(res.status_code, 200)

        reader = pypdf.PdfReader(io.BytesIO(res.content))
        text = reader.pages[0].extract_text()
        self.assertIn("dany.ferreira@epitech.digital", text)
        self.assertIn("06 99 88 77 66", text)
        self.assertIn("Assistant Chef de Projet Marketing (Apprentissage)", text)
        self.assertNotIn("recrute pour", text)

if __name__ == "__main__":
    unittest.main()
