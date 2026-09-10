import json
from datetime import datetime
from typing import Optional, Dict

class PromptEngine:
    """Builds hyper-personalized, authentic, anti-AI cover letter prompts."""

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

        return f"""Tu es un rédacteur d'élite et mentor en recrutement spécialisé dans la rédaction de lettres de motivation HAUTE FIDÉLITÉ et AUTHENTIQUES.

L'objectif absolu de l'utilisateur : Une lettre qui sonne 100% HUMAINE, VRAIE, PRÉCISE et SPÉCIFIQUE.
Le recruteur doit se dire : "Cette personne a pris le temps de nous comprendre, ce n'est absolument pas une lettre générée par IA ou un template réchauffé."

RÈGLES D'OR DE RÉDACTION :
1. {tone_instructions}
2. BANNISSEMENT TOTAL DU JARGON ET DES CLICHÉS IA :
   Ne JAMAIS utiliser : {', '.join(cls.BANNED_CLICHES)}.
3. STRUCTURE STRATÉGIQUE (4 MOUVEMENTS NATURELS) :
   - ACCROCHE (VOUS & LE DÉFI) : Commence immédiatement par l'actualité de l'entreprise, un projet récent, ou le défi concret lié au poste et à l'équipe. Montre d'emblée une vraie curiosité pour ce qu'ils construisent.
   - LA PREUVE PAR LES FAITS (MOI & L'IMPACT) : Ne te contente pas de lister des qualités. Cite 2 ou 3 faits réels, chiffres, technologies ou projets concrets extraits du CV du candidat qui prouvent qu'il a déjà résolu des problèmes similaires.
   - LA COLLABORATION (NOUS & L'ÉQUIPE) : Décris comment le candidat s'intégrera dans le quotidien de l'équipe (collaboration produit, tech, opérations ou business). Explique ce qu'ils vont construire ensemble.
   - CONCLUSION & APPEL À L'ACTION : Simple, chaleureuse et professionnelle. Propose un court échange (15-20 minutes) de manière naturelle. Formule de fin sobre (ex: "Bien cordialement,", "Très bonne semaine à vous,").

4. COORDONNÉES CANDIDAT :
   Garde STRICTEMENT le nom, l'email, le téléphone et la ville fournis dans la section candidat. N'invente aucun faux contact.

5. FORMAT DE SORTIE :
Tu dois répondre STRICTEMENT en JSON respectant exactement le schéma demandé, sans aucun markdown englobant (` ```json `), uniquement le JSON brut."""

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
        contact = candidate_contact or {}
        cand_name = contact.get("name") or "Candidat"
        cand_email = contact.get("email") or ""
        cand_phone = contact.get("phone") or ""
        cand_loc = contact.get("location") or "France"
        cand_head = contact.get("headline") or job_title or "Professionnel Qualifié"

        date_str = datetime.now().strftime("%d %B %Y").replace("January", "janvier").replace("February", "février").replace("March", "mars").replace("April", "avril").replace("May", "mai").replace("June", "juin").replace("July", "juillet").replace("August", "août").replace("September", "septembre").replace("October", "octobre").replace("November", "novembre").replace("December", "décembre")

        prompt = f"""Rédige la lettre de motivation parfaite et authentique en t'appuyant sur ces données réelles :

=== 1. COORDONNÉES RÉELLES DU CANDIDAT (À REPRODUIRE EXACTEMENT) ===
Nom : {cand_name}
Email : {cand_email}
Téléphone : {cand_phone}
Ville : {cand_loc}
Titre : {cand_head}

=== 2. CONTENU DU CV DU CANDIDAT ===
{cv_text[:5000]}

=== 3. INFORMATIONS ENTREPRISE & ÉQUIPE ===
Nom de l'entreprise : {company_name}
Poste ciblé : {job_title or "Poste à identifier d'après l'offre"}
Éléments de recherche recueillis sur l'entreprise et son écosystème :
{company_research or "Entreprise dynamique du secteur. Analyser les détails dans l'offre."}

=== 4. ANNONCE / DESCRIPTIF DU POSTE ===
{job_text[:4000] if job_text else "Pas d'annonce fournie, se baser sur le nom de l'entreprise et le poste ciblé."}

=== 5. INDICATIONS PARTICULIÈRES CANDIDAT ===
{custom_notes or "Aucune consigne particulière."}

=== FORMAT JSON STRICT ATTENDU ===
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
    "department": "À l'attention de l'équipe Recrutement",
    "city": "Paris"
  }},
  "meta": {{
    "date": "{date_str}",
    "subject": "Objet : Candidature au poste de [Intitulé exact]"
  }},
  "letter_content": {{
    "salutation": "Madame, Monsieur,",
    "paragraph_hook": "Accroche contextuelle basée sur l'actualité ou le défi précis de l'entreprise et l'équipe.",
    "paragraph_experience": "Réalisations concrètes du CV avec chiffres/outils, démontrant la valeur immédiate.",
    "paragraph_team_fit": "Collaboration concrète au sein de l'équipe, intégration dans leurs rituels et vision.",
    "paragraph_call_to_action": "Proposition naturelle d'un échange direct et conclusion sobre.",
    "valediction": "Bien cordialement,",
    "signature": "{cand_name}"
  }},
  "match_score": 94,
  "research_insights": [
    "Insight 1 sur l'entreprise / culture intégré dans la lettre",
    "Insight 2 sur le défi de l'équipe adressé",
    "Synergie clé relevée entre le CV et l'offre"
  ]
}}
"""
        return prompt
