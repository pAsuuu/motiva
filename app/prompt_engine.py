import json
from datetime import datetime
from typing import Optional, Dict
from app.job_analyzer import JobAnalyzer

class PromptEngine:
    """Builds 100% human, authentic, zero-cliche cover letters grounded in real facts and missions."""

    BANNED_CLICHES = [
        "J'ai attentivement suivi vos priorités de développement",
        "La rigueur que vous appliquez à l'exécution de vos feuilles de route",
        "C'est avec un vif intérêt",
        "Je me permets de vous adresser ma candidature",
        "Dynamique, rigoureux et motivé",
        "Fort de mon expérience",
        "Véritable couteau suisse",
        "Au sein d'une entreprise leader",
        "J'ai l'honneur de",
        "Je suis convaincu d'être le candidat idéal",
        "Veuillez agréer, Madame, Monsieur, l'expression de mes salutations distinguées",
        "Dans l'attente d'un retour favorable",
        "Apporter ma pierre à l'édifice",
        "Esprit d'équipe et autonomie",
        "Catalyseur de synergie",
        "Passionné depuis toujours",
        "Particulièrement stimulant",
        "Conjuguer analyse méthodique et efficacité opérationnelle",
        "Face à des problématiques exigeantes",
        "Acteur incontournable de votre marché"
    ]

    @classmethod
    def build_system_prompt(cls, tone: str = "direct_authentic") -> str:
        return f"""Tu es un mentor de recrutement d'élite. Ton rôle est de rédiger des lettres de motivation EXTRÊMEMENT HUMAINES, PRÉCISES, SOBRES et EFFICACES.

RÈGLE CARDINALE : ZÉRO LANGUE DE BOIS & ZÉRO PHRASE DE REMPLISSAGE ROBOTIQUE.
Tout recruteur ou manager qui lit cette lettre doit immédiatement voir que le candidat a COMPRIS LE BOULOT, ses difficultés réelles et qu'il parle comme un vrai collègue pragmatique.

LISTE NOIRE ABSOLUE DE TOURNURES INTERDITES :
Ne JAMAIS écrire de phrases creuses du type :
{chr(10).join(f"- {c}" for c in cls.BANNED_CLICHES)}

EXEMPLES DE CE QUI EST INTERDIT VS CE QUI EST EXIGÉ :
❌ HORRIBLE (Fluff IA) : "J'ai attentivement suivi vos priorités de développement et la rigueur que vous appliquez à l'exécution de vos feuilles de route."
✅ PERCUTANT & HUMAIN : "Fluidifier le quotidien des équipes métiers tout en garantissant l'adoption sans friction de nouveaux outils informatiques est un rôle charnière, en particulier sur des fonctions Trade & Marketing."

❌ HORRIBLE (Fluff IA) : "Au cours de mes missions, j'ai veillé à conjuguer analyse méthodique et efficacité opérationnelle face à des problématiques exigeantes."
✅ FACTUEL & CONCRET : "Lors de mes récents projets, j'ai notamment pris en charge le recueil des besoins auprès d'une quinzaine d'utilisateurs, le cadrage des tests de recette et la formation aux nouveaux outils."

DIRECTIVES D'ÉCRITURE :
1. ACCROCHE : Entre directement dans le vif du sujet. Parle du rôle réel, du problème métier que l'entreprise cherche à résoudre ou de l'équipe mentionnée dans l'offre (ex: si le tuteur/manager est nommé, cite-le naturellement).
2. PREUVE PAR L'ACTION : Tire 2 ou 3 compétences ou accomplissements tangibles du CV du candidat. Pas d'adjectifs flatteurs ("je suis rigoureux"), mais des preuves concrètes ("j'ai coordonné...", "j'ai automatisé...", "j'ai formé...").
3. PROJECTION ÉQUIPE : Décris comment le candidat va s'intégrer au quotidien dans les rituels et apporter une aide immédiate.
4. APPEL À L'ACTION : Simple, direct et poli (ex: "Je serais ravi d'échanger une quinzaine de minutes avec vous lors d'un premier entretien.").
5. COORDONNÉES RÉELLES : Garde strictement le nom, l'email, le téléphone et la ville du candidat.
6. SORTIE JSON STRICTE : Réponds uniquement avec le JSON demandé, sans bloc de code markdown."""

    @classmethod
    def build_user_prompt(
        cls,
        cv_text: str,
        company_name: str,
        job_title: str,
        job_text: str,
        company_research: str,
        candidate_contact: Optional[Dict[str, str]] = None,
        custom_notes: str = "",
        tone: str = "direct_authentic"
    ) -> str:
        meta_clean = JobAnalyzer.clean_job_title(job_title or "", company_hint=company_name)
        clean_title = meta_clean["clean_title"] or "Poste Stratégique"
        clean_subject = meta_clean["clean_subject"]
        department = meta_clean["department"]

        contact = candidate_contact or {}
        cand_name = contact.get("name") or "Candidat"
        cand_email = contact.get("email") or ""
        cand_phone = contact.get("phone") or ""
        cand_loc = contact.get("location") or "France"
        cand_head = contact.get("headline") or clean_title

        date_str = datetime.now().strftime("%d %B %Y").replace("January", "janvier").replace("February", "février").replace("March", "mars").replace("April", "avril").replace("May", "mai").replace("June", "juin").replace("July", "juillet").replace("August", "août").replace("September", "septembre").replace("October", "octobre").replace("November", "novembre").replace("December", "décembre")

        prompt = f"""Rédige une lettre de motivation exceptionnelle, réaliste et 100% crédible en t'appuyant sur ces détails concrets :

=== 1. COORDONNÉES RÉELLES CANDIDAT (À RESPECTER STRICTEMENT) ===
Nom : {cand_name}
Email : {cand_email}
Téléphone : {cand_phone}
Ville : {cand_loc}
Titre : {cand_head}

=== 2. L'ENTREPRISE & L'ÉQUIPE ===
Entreprise : {company_name}
Poste : {clean_title}
Objet préconisé : {clean_subject}
Direction / Équipe : {department}
Contexte d'entreprise recueilli :
{company_research or "Grand acteur du secteur."}

=== 3. ANNONCE RÉELLE & MISSIONS CLÉS ===
{job_text[:5000] if job_text else "Pas d'annonce brute, se concentrer sur les missions réelles du poste."}

=== 4. EXPÉRIENCE CANDIDAT (CV) ===
{cv_text[:5000]}

=== 5. NOTES PARTICULIÈRES CANDIDAT ===
{custom_notes or "Aucune note particulière."}

=== INSTRUCTIONS DE SORTIE JSON STRICT ===
{{
  "candidate": {{
    "name": "{cand_name}",
    "email": "{cand_email}",
    "phone": "{cand_phone}",
    "location": "{cand_loc}",
    "headline": "{cand_head}"
  }},
  "recipient": {{
    "company": "{company_name}",
    "department": "{department}",
    "city": "Siège ou Ville"
  }},
  "meta": {{
    "date": "{date_str}",
    "subject": "{clean_subject}"
  }},
  "letter_content": {{
    "salutation": "Madame, Monsieur,",
    "paragraph_hook": "Accroche percutante et naturelle ancrée sur les missions réelles et l'équipe (sans aucune flatterie robotique).",
    "paragraph_experience": "Réalisations concrètes et compétences du CV directement reliées aux besoins de l'offre.",
    "paragraph_team_fit": "Intégration dans le collectif et apport opérationnel immédiat.",
    "paragraph_call_to_action": "Proposition sobre et professionnelle d'un entretien.",
    "valediction": "Bien cordialement,",
    "signature": "{cand_name}"
  }},
  "match_score": 97,
  "research_insights": [
    "Prise en compte des missions concrètes de l'offre",
    "Élimination totale du jargon IA et des clichés",
    "Lien direct entre le parcours du candidat et les besoins de l'équipe"
  ]
}}
"""
        return prompt
