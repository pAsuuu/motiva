import json
from datetime import datetime
from typing import Optional, Dict
from app.job_analyzer import JobAnalyzer

class PromptEngine:
    """Builds hyper-personalized, authentic, anti-AI cover letter prompts with deep company grounding."""

    BANNED_CLICHES = [
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
        "Passionné depuis toujours"
    ]

    @classmethod
    def build_system_prompt(cls, tone: str = "direct_authentic") -> str:
        tone_instructions = {
            "direct_authentic": "Ton percutant, honnête, professionnel et direct. Phrases rythmées, vivantes, sans détours ni flagornerie.",
            "startup_tech": "Ton moderne, axé produit, impact et vélocité. Vocabulaire tech précis, décontracté mais rigoureux.",
            "corporate_executive": "Ton institutionnel moderne, soigné, élégant et mesuré, valorisant la vision stratégique et les résultats.",
        }.get(tone, "Ton percutant, honnête, professionnel et direct.")

        return f"""Tu es un directeur de recrutement et rédacteur d'élite spécialisé dans les candidatures de HAUT NIVEAU.

OBJECTIF CRUCIAL :
La lettre doit paraître 100% HUMAINE, RÉFLÉCHIE, ULTRA-PRÉCISE et profondément ancrée dans l'actualité et la stratégie réelle de l'entreprise.
Le recruteur ou manager de l'équipe doit se dire : "Ce candidat comprend exactement notre métier, nos marques, nos défis actuels et ce qu'on attend de lui dès le premier jour."

RÈGLES D'OR DE RÉDACTION :
1. {tone_instructions}
2. BANNISSEMENT ABSOLU DES FORMULES CLICHÉES :
   Interdiction totale d'utiliser : {', '.join(cls.BANNED_CLICHES)}.
3. ÉPURATION DU TITRE ET DE L'OBJET :
   - BANNIR TOUT TEXTE BRUT DE SITE D'EMPLOI (ex: 'X recrute pour des postes de...', 'Offre d'emploi', '(H/F)').
   - Utiliser STRICTEMENT le titre métier noble et épuré (ex: 'Assistant Chef de Projet Marketing').
   - Préciser la formule de contrat si applicable (ex: 'Objet : Candidature au poste d'Assistant Chef de Projet Marketing (Apprentissage)').
4. ANCRAGE D'ACTUALITÉ ET DE STRATÉGIE (VOUS & LE DÉFI) :
   - Mentionne des éléments concrets, récents et stratégiques de l'entreprise (ex: pour Stellantis, citer le plan Dare Forward 2030, la transition vers l'électrique, le déploiement omnicanal de leurs marques comme Peugeot, Fiat, Jeep, Citroën, etc.).
   - Parle du quotidien et du rôle de l'équipe (Direction Marketing, pôle activation, coordination transversale).
5. LA PREUVE PAR L'IMPACT (MOI & L'ACTION) :
   - Sélectionne 2 ou 3 faits tangibles, projets, données ou outils du CV qui prouvent que le candidat est déjà opérationnel.
6. LA VISION COMMUNE (NOUS & L'ÉQUIPE) :
   - Comment le candidat contribuera concrètement aux objectifs de l'équipe dès son arrivée.
7. COORDONNÉES STRICTES :
   - Conserve à l'identique les coordonnées réelles fournies pour le candidat. Ne jamais générer d'email ou de téléphone fictif.
8. FORMAT STRICT DE SORTIE :
   Répondre EXCLUSIVEMENT avec le JSON demandé, sans bloc de code markdown."""

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
        # Normalize and clean job title
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

        prompt = f"""Rédige une lettre de motivation exceptionnelle, ultra-ciblée et percutante :

=== 1. COORDONNÉES CANDIDAT (À REPRODUIRE EXACTEMENT) ===
Nom : {cand_name}
Email : {cand_email}
Téléphone : {cand_phone}
Ville : {cand_loc}
Titre : {cand_head}

=== 2. INFORMATIONS ENTREPRISE, ÉQUIPE & ACTUALITÉ STRATÉGIQUE ===
Entreprise : {company_name}
Poste épuré : {clean_title}
Objet préconisé : {clean_subject}
Direction / Équipe ciblée : {department}
Éléments d'actualité, stratégie et défis recueillis :
{company_research or "Grand acteur du secteur. S'appuyer sur la culture et les objectifs de l'entreprise."}

=== 3. DESCRIPTIF / CONTENU DE L'OFFRE ===
{job_text[:4000] if job_text else "Pas d'annonce fournie, focalise-toi sur le poste et les missions types."}

=== 4. EXPÉRIENCES DU CANDIDAT (CV) ===
{cv_text[:5000]}

=== 5. ANECDOTE OU SOUHAIT PARTICULIER CANDIDAT ===
{custom_notes or "Aucune indication particulière."}

=== FORMAT JSON ATTENDU ===
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
    "paragraph_hook": "Accroche ancrée directement dans l'actualité, la transformation ou le défi concret de {company_name} et de son équipe {department}.",
    "paragraph_experience": "Faits précis, compétences et réalisations concrètes du CV en résonance directe avec les missions de {clean_title}.",
    "paragraph_team_fit": "Projection dans le travail d'équipe, la coordination de projets et la dynamique collective de {company_name}.",
    "paragraph_call_to_action": "Proposition sobre et professionnelle d'un entretien d'échange.",
    "valediction": "Bien cordialement,",
    "signature": "{cand_name}"
  }},
  "match_score": 97,
  "research_insights": [
    "Alignement avec la feuille de route stratégique de {company_name}",
    "Prise en compte des enjeux spécifiques du poste de {clean_title}",
    "Mise en valeur d'expériences clés du CV démontrant la valeur opérationnelle"
  ]
}}
"""
        return prompt
