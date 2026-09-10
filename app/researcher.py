import re
import urllib.parse
from typing import Dict, Any, List, Optional
import httpx
from bs4 import BeautifulSoup
from app.job_analyzer import JobAnalyzer

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
}

class Researcher:
    """Scrapes job descriptions from URLs, bypasses job board authwalls, and gathers deep company intelligence."""

    @classmethod
    async def _handle_linkedin_url(cls, url: str) -> Optional[Dict[str, Any]]:
        """Bypasses LinkedIn authwalls by querying the public guest job posting endpoint."""
        try:
            parsed = urllib.parse.urlparse(url)
            qs = urllib.parse.parse_qs(parsed.query)
            
            # Extract job ID from currentJobId param or /jobs/view/<id> path
            job_id = qs.get("currentJobId", [""])[0]
            if not job_id:
                m = re.search(r'/jobs/view/(\d+)', url)
                if m:
                    job_id = m.group(1)

            keywords = qs.get("keywords", [""])[0]

            if not job_id:
                # If only keywords are present without job_id
                if keywords:
                    meta = JobAnalyzer.clean_job_title(keywords)
                    return {
                        "success": True,
                        "url": url,
                        "raw_title": keywords,
                        "clean_title": meta["clean_title"],
                        "company_name": meta["company_name"],
                        "contract_type": meta["contract_type"],
                        "department": meta["department"],
                        "clean_subject": meta["clean_subject"],
                        "text": f"Poste identifié depuis les paramètres de recherche : {keywords}",
                        "source": "linkedin_keywords_fallback"
                    }
                return None

            guest_url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
            async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True, timeout=10.0) as client:
                resp = await client.get(guest_url)
                if resp.status_code == 200 and len(resp.text) > 500:
                    soup = BeautifulSoup(resp.text, "html.parser")
                    
                    title_el = soup.find("h2", class_=re.compile(r"topcard__title|top-card-layout__title")) or soup.find("h1")
                    comp_el = soup.find("a", class_=re.compile(r"topcard__org-name-link|topcard__flavor")) or soup.find("span", class_=re.compile(r"topcard__flavor"))
                    desc_el = soup.find("div", class_=re.compile(r"show-more-less-html__markup|description__text")) or soup.find("section")

                    raw_title = title_el.get_text().strip() if title_el else keywords
                    comp_name = comp_el.get_text().strip() if comp_el else ""
                    desc_text = desc_el.get_text(separator="\n").strip() if desc_el else ""

                    # Clean title and company
                    meta = JobAnalyzer.clean_job_title(raw_title or keywords, company_hint=comp_name)
                    final_company = comp_name or meta["company_name"]
                    deep_info = JobAnalyzer.get_deep_company_context(final_company)

                    return {
                        "success": True,
                        "url": url,
                        "raw_title": raw_title,
                        "clean_title": meta["clean_title"],
                        "company_name": final_company,
                        "contract_type": meta["contract_type"],
                        "department": meta["department"],
                        "clean_subject": meta["clean_subject"],
                        "text": desc_text[:12000],
                        "company_deep_info": deep_info,
                        "source": "linkedin_guest_api"
                    }
        except Exception:
            pass

        return None

    @classmethod
    async def fetch_job_from_url(cls, url: str) -> Dict[str, Any]:
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        # 1. Specialized LinkedIn bypass
        if "linkedin.com" in url:
            linkedin_res = await cls._handle_linkedin_url(url)
            if linkedin_res and linkedin_res.get("success"):
                return linkedin_res

        # 2. General Scraping
        try:
            async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True, timeout=12.0) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                html = resp.text

            soup = BeautifulSoup(html, "html.parser")

            # Remove noise elements
            for tag in soup(["script", "style", "nav", "footer", "aside", "header", "noscript", "svg", "form"]):
                tag.decompose()

            raw_title = ""
            og_title = soup.find("meta", property="og:title")
            if og_title and og_title.get("content"):
                raw_title = og_title["content"].strip()
            elif soup.title and soup.title.string:
                raw_title = soup.title.string.strip()
            elif soup.find("h1"):
                raw_title = soup.find("h1").get_text().strip()

            # Anti-Authwall check: If page is a login wall ("S'identifier", "Sign in", etc.)
            authwall_signals = ["s'identifier", "s’identifier", "se connecter", "sign in", "authwall", "log in"]
            if any(signal in raw_title.lower() for signal in authwall_signals):
                # Check if URL had keywords or params we can salvage
                parsed_url = urllib.parse.urlparse(url)
                qs = urllib.parse.parse_qs(parsed_url.query)
                keywords = qs.get("keywords", [""])[0] or qs.get("q", [""])[0]
                if keywords:
                    meta = JobAnalyzer.clean_job_title(keywords)
                    return {
                        "success": True,
                        "url": url,
                        "raw_title": keywords,
                        "clean_title": meta["clean_title"],
                        "company_name": meta["company_name"],
                        "contract_type": meta["contract_type"],
                        "department": meta["department"],
                        "clean_subject": meta["clean_subject"],
                        "text": f"Poste identifié : {keywords}. (Le site requiert une connexion pour lire le texte complet).",
                        "authwall_detected": True,
                        "source": "authwall_keywords_fallback"
                    }
                else:
                    return {
                        "success": False,
                        "url": url,
                        "title": "",
                        "clean_title": "",
                        "text": "",
                        "error": "Ce site (ex: LinkedIn) demande d'être connecté pour afficher l'annonce. Astuce : Copiez le texte de l'annonce depuis votre navigateur et collez-le dans l'onglet 'Coller le texte' !"
                    }

            # Clean job title intelligently
            cleaned_meta = JobAnalyzer.clean_job_title(raw_title)

            # Target main job container
            possible_containers = [
                soup.find("div", class_=re.compile(r"job[-_]description|posting[-_]description|offer[-_]description|content[-_]body", re.I)),
                soup.find("section", class_=re.compile(r"job|description|posting|offer", re.I)),
                soup.find("article"),
                soup.find("main"),
                soup.find("div", id=re.compile(r"job[-_]description|description|offer", re.I))
            ]

            target_container = next((c for c in possible_containers if c is not None), None)

            if target_container:
                text = target_container.get_text(separator="\n")
            else:
                body = soup.find("body")
                text = body.get_text(separator="\n") if body else soup.get_text(separator="\n")

            cleaned_lines = []
            for line in text.splitlines():
                cleaned = line.strip()
                if len(cleaned) > 2 and not any(skip in cleaned.lower() for skip in ["cookie", "politique de confidentialité", "accepter tout", "sign in", "se connecter"]):
                    cleaned_lines.append(cleaned)

            cleaned_text = "\n".join(cleaned_lines)[:12000]

            company_name = cleaned_meta.get("company_name", "")
            if not company_name:
                parsed_domain = urllib.parse.urlparse(url).netloc
                domain_parts = parsed_domain.replace("www.", "").split(".")
                if domain_parts and len(domain_parts[0]) > 2 and domain_parts[0] not in ["linkedin", "welcometothejungle", "indeed"]:
                    company_name = domain_parts[0].capitalize()
                    cleaned_meta["company_name"] = company_name

            deep_info = JobAnalyzer.get_deep_company_context(company_name) if company_name else {}

            return {
                "success": True,
                "url": url,
                "raw_title": raw_title,
                "clean_title": cleaned_meta["clean_title"],
                "company_name": cleaned_meta["company_name"],
                "contract_type": cleaned_meta["contract_type"],
                "department": cleaned_meta["department"],
                "clean_subject": cleaned_meta["clean_subject"],
                "text": cleaned_text,
                "company_deep_info": deep_info,
                "source": "smart_url_scraper"
            }

        except Exception as e:
            return {
                "success": False,
                "url": url,
                "title": "",
                "clean_title": "",
                "text": "",
                "error": f"Impossible d'extraire automatiquement l'URL ({str(e)}). Vous pouvez coller le texte ci-dessous dans l'onglet 'Coller le texte'."
            }

    @staticmethod
    async def search_company_info(company_name: str) -> Dict[str, Any]:
        """Searches public information and deep context on company strategy, news and team."""
        cleaned_name = company_name.strip()
        if not cleaned_name:
            return {"company_name": "", "insights": [], "raw_insights": ""}

        insights: List[str] = []

        deep = JobAnalyzer.get_deep_company_context(cleaned_name)
        if deep.get("sector"):
            insights.append(f"Secteur : {deep['sector']}")
        if deep.get("strategy"):
            insights.append(f"Actualité & Stratégie clé : {deep['strategy']}")
        if deep.get("brands"):
            insights.append(f"Marques & Écosystème : {deep['brands']}")
        if deep.get("challenges"):
            insights.append(f"Défis opérationnels de l'équipe : {deep['challenges']}")

        try:
            wiki_url = f"https://fr.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(cleaned_name)}"
            async with httpx.AsyncClient(headers=HEADERS, timeout=4.0) as client:
                resp = await client.get(wiki_url)
                if resp.status_code == 200:
                    data = resp.json()
                    extract = data.get("extract", "")
                    if extract:
                        insights.append(f"Présentation générale : {extract[:350]}...")
        except Exception:
            pass

        return {
            "company_name": cleaned_name,
            "raw_insights": "\n".join(insights),
            "insights_count": len(insights)
        }
