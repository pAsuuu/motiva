import re
from typing import Dict, Any, Optional

class JobAnalyzer:
    """Intelligently cleans scraped job titles and extracts structured metadata."""

    KNOWN_COMPANIES = {
        "nestlé": {
            "name": "Nestlé",
            "sector": "Agroalimentaire & Produits de Grande Consommation",
            "strategy": "Transformation digitale omnicanale, innovation produit saine et durable, digitalisation des opérations IT et Trade Marketing.",
            "brands": "Nespresso, Nescafé, Purina, KitKat, Vittel, Perrier, Maggi",
            "challenges": "Alignement des projets IT avec les enjeux métiers, optimisation de la supply chain et déploiement d'outils collaboratifs à l'échelle."
        },
        "nestle": {
            "name": "Nestlé",
            "sector": "Agroalimentaire & Produits de Grande Consommation",
            "strategy": "Transformation digitale omnicanale, innovation produit saine et durable, digitalisation des opérations IT et Trade Marketing.",
            "brands": "Nespresso, Nescafé, Purina, KitKat, Vittel, Perrier, Maggi",
            "challenges": "Alignement des projets IT avec les enjeux métiers, optimisation de la supply chain et déploiement d'outils collaboratifs à l'échelle."
        },
        "stellantis": {
            "name": "Stellantis",
            "sector": "Automobile & Mobilité Durable",
            "strategy": "Plan stratégique Dare Forward 2030, transition vers l'électrification (gammes BEV) et excellence opérationnelle.",
            "brands": "Peugeot, Citroën, Fiat, Jeep, Alfa Romeo, DS Automobiles, Opel, Maserati",
            "challenges": "Déploiement de campagnes omnicanales innovantes, renforcement de l'expérience client numérique et valorisation des mobilités d'avenir."
        },
        "doctolib": {
            "name": "Doctolib",
            "sector": "E-Santé & Technologies Médicales",
            "strategy": "Amélioration du quotidien des soignants et accès aux soins pour des millions de patients.",
            "challenges": "Adoption d'outils d'IA médicale sécurisés, coordination hospitalière et simplicité d'usage."
        },
        "alan": {
            "name": "Alan",
            "sector": "Assurance Santé & Bien-être",
            "strategy": "Partenaire santé tout-en-un, culture d'entreprise radicalement transparente et asynchrone.",
            "challenges": "Expansion B2B européenne, prévention santé proactive et rapidité de remboursement."
        },
        "l'oréal": {
            "name": "L'Oréal",
            "sector": "Cosmétique & Beauty Tech",
            "strategy": "Leader mondial de la beauté, intégration de la Beauty Tech et développement durable.",
            "challenges": "Marketing d'influence data-driven, personnalisation des formules et e-commerce international."
        },
        "airbus": {
            "name": "Airbus",
            "sector": "Aéronautique & Spatial",
            "strategy": "Pionnier de l'aviation décarbonée (projets hydrogène ZEROe) et connectivité satellite.",
            "challenges": "Montée en cadence de production, rigueur de sécurité industrielle et technologies souveraines."
        }
    }

    CONTRACT_PATTERNS = [
        (r'\b(?:apprentissage|apprenti(?:e)?)\b', 'Apprentissage'),
        (r'\b(?:alternance|alternant(?:e)?)\b', 'Alternance'),
        (r'\b(?:stage|stagiaire|internship|intern)\b', 'Stage'),
        (r'\b(?:cdi|contrat\s+à\s+durée\s+indéterminée|permanent)\b', 'CDI'),
        (r'\b(?:cdd|contrat\s+à\s+durée\s+déterminée|fixed-term)\b', 'CDD'),
        (r'\b(?:freelance|indépendant|prestataire)\b', 'Freelance')
    ]

    DEPARTMENT_KEYWORDS = [
        (r'\b(?:it|informatique|systèmes\s+d[\'\']information|tech)\b', 'Direction des Systèmes d\'Information & IT'),
        (r'\bmarketing\b', 'Direction Marketing & Communication'),
        (r'\bcommunication\b', 'Direction de la Communication'),
        (r'\b(?:développeur|software|engineer|ingénieur)\b', 'Direction Technique & Ingénierie'),
        (r'\b(?:data|data\s+science|analyst)\b', 'Pôle Data & Analytics'),
        (r'\b(?:produit|product|pm)\b', 'Équipe Produit'),
        (r'\b(?:sales|commercial|business\s+dev)\b', 'Direction Commerciale & Business Development'),
        (r'\b(?:rh|ressources\s+humaines|talent)\b', 'Direction des Ressources Humaines'),
        (r'\b(?:finance|comptabilit[ée])\b', 'Direction Financière')
    ]

    @classmethod
    def clean_job_title(cls, raw_title: str, company_hint: str = "") -> Dict[str, Any]:
        text = raw_title.strip()

        detected_company = company_hint.strip()
        detected_contract = ""
        detected_dept = ""

        # Check for company in title if not given
        if not detected_company:
            comp_match = re.match(r'^([a-zA-Z0-9\s\'.-]{2,25})\s+(?:recrute|cherche|embauche)\b', text, re.I)
            if comp_match:
                detected_company = comp_match.group(1).strip()

        # Check for contract type
        for pattern, contract_name in cls.CONTRACT_PATTERNS:
            if re.search(pattern, text, re.I):
                detected_contract = contract_name
                break

        # Remove typical scraping noise prefixes
        noise_prefixes = [
            r'^(?:offre\s+d[\'\']emploi|job\s+offer|job|annonce)\s*:\s*',
            r'^(?:recrutement|nous\s+recrutons|on\s+recrute)\s*:\s*',
            r'^[a-zA-Z0-9\s\'.-]{2,30}\s+recrute\s+(?:pour\s+(?:des\s+postes?\s+de\s+|un\s+poste\s+de\s+)?)?',
            r'^(?:des\s+postes?\s+de|un\s+poste\s+de)\s+',
            r'^(?:recherche\s+(?:d[\'\']un|d[\'\']une)?\s+)',
            r'^(?:poste\s+de\s+)',
            r'^(?:alternant(?:e)?|apprenti(?:e)?|stagiaire)\s+(?:en\s+|de\s+)?'
        ]

        cleaned = text
        for pat in noise_prefixes:
            cleaned = re.sub(pat, '', cleaned, flags=re.I).strip()

        # Remove contract prefix inside title (e.g. 'Apprentissage : Assistant chef de projet marketing')
        cleaned = re.sub(r'^(?:apprentissage|alternance|stage|cdi|cdd)\s*:\s*', '', cleaned, flags=re.I).strip()

        # Remove trailing job board suffixes
        cleaned = re.sub(r'\s*\|\s*(?:linkedin|welcome\s+to\s+the\s+jungle|indeed|monster|apec|hellowork|glassdoor).*$', '', cleaned, flags=re.I).strip()
        cleaned = re.sub(r'\s*-\s*(?:linkedin|welcome\s+to\s+the\s+jungle|indeed|apec).*$', '', cleaned, flags=re.I).strip()

        # Remove gender indicators: (H/F), (F/H), H/F, F/H
        cleaned = re.sub(r'[\(\[\{]?(?:H/F|F/H|M/F|F/M)[\)\]\}]?', '', cleaned, flags=re.I).strip()

        # Normalize capitalization
        words = cleaned.split()
        capitalized_words = []
        lowercase_exceptions = {"de", "des", "du", "la", "le", "les", "et", "en", "pour", "à", "au", "aux", "d'"}
        for i, word in enumerate(words):
            lower_word = word.lower()
            if i > 0 and lower_word in lowercase_exceptions:
                capitalized_words.append(lower_word)
            elif lower_word in ["it", "rh", "crm", "seo", "sea", "api", "bi"]:
                capitalized_words.append(lower_word.upper())
            else:
                capitalized_words.append(word.capitalize())
        clean_title = " ".join(capitalized_words)

        # Infer department
        for pat, dept_name in cls.DEPARTMENT_KEYWORDS:
            if re.search(pat, clean_title, re.I):
                detected_dept = dept_name
                break

        # Build clean subject
        if detected_contract:
            subject = f"Objet : Candidature au poste de {clean_title} ({detected_contract})"
        else:
            subject = f"Objet : Candidature au poste de {clean_title}"

        return {
            "original_title": text,
            "clean_title": clean_title,
            "company_name": detected_company,
            "contract_type": detected_contract,
            "department": detected_dept or "Direction du Recrutement",
            "clean_subject": subject
        }

    @classmethod
    def get_deep_company_context(cls, company_name: str) -> Dict[str, Any]:
        """Returns deep context and recent strategic milestones for companies."""
        key = company_name.lower().strip()
        for comp_key, comp_info in cls.KNOWN_COMPANIES.items():
            if comp_key in key or key in comp_key:
                return comp_info

        return {
            "name": company_name,
            "sector": "Entreprise de référence",
            "strategy": f"Croissance, digitalisation et développement de solutions innovantes chez {company_name}.",
            "challenges": "Excellence opérationnelle, collaboration d'équipe et satisfaction client."
        }
