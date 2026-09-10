import re
import urllib.parse
from typing import Dict, Any, List, Optional
import httpx
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
}

class Researcher:
    """Scrapes job descriptions from URLs and gathers contextual intelligence on companies."""

    @staticmethod
    async def fetch_job_from_url(url: str) -> Dict[str, Any]:
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        try:
            async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True, timeout=12.0) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                html = resp.text

            soup = BeautifulSoup(html, "html.parser")

            # Remove noise elements
            for tag in soup(["script", "style", "nav", "footer", "aside", "header", "noscript", "svg", "form"]):
                tag.decompose()

            # Try to get page title or job title
            title = ""
            og_title = soup.find("meta", property="og:title")
            if og_title and og_title.get("content"):
                title = og_title["content"].strip()
            elif soup.title and soup.title.string:
                title = soup.title.string.strip()
            elif soup.find("h1"):
                title = soup.find("h1").get_text().strip()

            # Try finding the core job description container
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

            # Clean and normalize lines
            cleaned_lines = []
            for line in text.splitlines():
                cleaned = line.strip()
                if len(cleaned) > 2 and not any(skip in cleaned.lower() for skip in ["cookie", "politique de confidentialité", "accepter tout", "sign in", "se connecter"]):
                    cleaned_lines.append(cleaned)

            cleaned_text = "\n".join(cleaned_lines)
            cleaned_text = cleaned_text[:12000]

            return {
                "success": True,
                "url": url,
                "title": title,
                "text": cleaned_text,
                "source": "url_scraper"
            }

        except Exception as e:
            return {
                "success": False,
                "url": url,
                "title": "",
                "text": "",
                "error": f"Impossible d'extraire automatiquement l'URL ({str(e)}). Vous pouvez copier-coller directement le texte de l'annonce ci-dessous."
            }

    @staticmethod
    async def search_company_info(company_name: str) -> Dict[str, Any]:
        """Searches public information on the company to identify mission, culture, and context."""
        cleaned_name = company_name.strip()
        if not cleaned_name:
            return {"company_name": "", "insights": [], "raw_insights": ""}

        insights: List[str] = []

        # 1. Try fetching Wikipedia summary API for established companies
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

        # 2. Try DuckDuckGo Instant Answer API
        try:
            ddg_api = f"https://api.duckduckgo.com/?q={urllib.parse.quote(cleaned_name)}&format=json&no_redirect=1"
            async with httpx.AsyncClient(headers=HEADERS, timeout=4.0) as client:
                resp = await client.get(ddg_api)
                if resp.status_code == 200:
                    data = resp.json()
                    abstract = data.get("AbstractText", "")
                    if abstract and abstract not in insights:
                        insights.append(f"Secteur & Activité : {abstract}")
        except Exception:
            pass

        # Fallback contextual notes
        if not insights:
            insights.append(f"Acteur de référence dans son secteur d'activité ({cleaned_name}).")
            insights.append("Focus sur la qualité d'exécution, l'impact opérationnel et la collaboration transverse.")

        return {
            "company_name": cleaned_name,
            "raw_insights": "\n".join(insights),
            "insights_count": len(insights)
        }
