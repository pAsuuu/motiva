import os
import io
from typing import Optional, Dict, Any
from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.responses import Response, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from app.cv_parser import CVParser
from app.researcher import Researcher
from app.ai_generator import AIGenerator
from app.pdf_generator import PDFGenerator
from app.job_analyzer import JobAnalyzer

load_dotenv()

app = FastAPI(title="Motiva — Lettres de motivation d'élite & Analyse Intelligente")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FetchJobRequest(BaseModel):
    url: str

class ResearchRequest(BaseModel):
    company_name: str
    job_text: Optional[str] = ""

class AnalyzeJobRequest(BaseModel):
    raw_title: Optional[str] = ""
    company_name: Optional[str] = ""
    job_text: Optional[str] = ""

class GenerateLetterRequest(BaseModel):
    cv_text: str
    company_name: str
    job_title: Optional[str] = ""
    job_text: Optional[str] = ""
    company_research: Optional[str] = ""
    candidate_contact: Optional[Dict[str, str]] = None
    custom_notes: Optional[str] = ""
    tone: Optional[str] = "direct_authentic"
    api_key: Optional[str] = None
    model_name: Optional[str] = None

class ExportPDFRequest(BaseModel):
    letter_data: Dict[str, Any]
    theme: Optional[str] = "modern"

@app.get("/api/status")
def get_status():
    env_key = bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))
    return {
        "status": "ready",
        "has_env_key": env_key,
        "supported_models": ["gemini-2.5-flash", "gemini-1.5-pro", "gemini-1.5-flash"]
    }

@app.post("/api/upload-cv")
async def upload_cv(file: UploadFile = File(...)):
    try:
        content = await file.read()
        parsed = CVParser.parse(file.filename, content)
        return parsed
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur d'analyse du CV: {str(e)}")

@app.post("/api/fetch-job")
async def fetch_job(payload: FetchJobRequest):
    if not payload.url or not payload.url.strip():
        raise HTTPException(status_code=400, detail="URL requise")
    res = await Researcher.fetch_job_from_url(payload.url)
    return res

@app.post("/api/analyze-job")
async def analyze_job(payload: AnalyzeJobRequest):
    meta = JobAnalyzer.clean_job_title(payload.raw_title or "", company_hint=payload.company_name or "")
    comp_name = meta["company_name"] or payload.company_name or ""
    deep_ctx = JobAnalyzer.get_deep_company_context(comp_name) if comp_name else {}
    return {
        "clean_title": meta["clean_title"],
        "company_name": comp_name,
        "contract_type": meta["contract_type"],
        "department": meta["department"],
        "clean_subject": meta["clean_subject"],
        "deep_context": deep_ctx
    }

@app.post("/api/research-company")
async def research_company(payload: ResearchRequest):
    if not payload.company_name or not payload.company_name.strip():
        raise HTTPException(status_code=400, detail="Nom d'entreprise requis")
    res = await Researcher.search_company_info(payload.company_name)
    return res

@app.post("/api/generate-letter")
async def generate_letter(payload: GenerateLetterRequest):
    if not payload.cv_text or not payload.cv_text.strip():
        raise HTTPException(status_code=400, detail="Texte du CV manquant")
    if not payload.company_name or not payload.company_name.strip():
        raise HTTPException(status_code=400, detail="Nom de l'entreprise manquant")

    result = await AIGenerator.generate(
        cv_text=payload.cv_text,
        company_name=payload.company_name,
        job_title=payload.job_title or "",
        job_text=payload.job_text or "",
        company_research=payload.company_research or "",
        candidate_contact=payload.candidate_contact,
        custom_notes=payload.custom_notes or "",
        tone=payload.tone or "direct_authentic",
        api_key=payload.api_key,
        model_name=payload.model_name
    )
    return result

@app.post("/api/export-pdf")
async def export_pdf(payload: ExportPDFRequest):
    try:
        pdf_bytes = PDFGenerator.generate_pdf(payload.letter_data, payload.theme or "modern")
        candidate_name = payload.letter_data.get("candidate", {}).get("name", "Candidat").replace(" ", "_")
        company = payload.letter_data.get("recipient", {}).get("company", "Entreprise").replace(" ", "_")
        filename = f"Lettre_Motivation_{candidate_name}_{company}.pdf"

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de génération PDF: {str(e)}")

# Mount frontend static files
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
