# Motiva — Service de Lettres de Motivation Authentiques & Anti-IA

Motiva est une application conçue pour générer des lettres de motivation **profondément personnalisées, honnêtes et percutantes**, évitant tous les clichés et tournures artificielles des IA génératives classiques.

---

## ✨ Fonctionnalités Clés

1. **Ingestion Intelligente du CV** :
   - Support des formats PDF, DOCX et texte brut.
   - Extraction automatique des coordonnées, du profil et des réalisations marquantes.
2. **Enquête sur l'Entreprise et l'Équipe** :
   - Support d'une **URL d'offre** (extraction automatique propre) ou d'un **texte copié-collé**.
   - Recherche contextuelle sur l'entreprise (culture, mission, défis récents, équipe associée).
3. **Moteur Rédactionnel "Anti-Clichés IA"** :
   - Bannissement strict des expressions robotiques (*"dynamique et motivé"*, *"c'est avec un vif intérêt"*, *"catalyseur"*, *"synergie"*...).
   - Structure narrative humaine en 4 mouvements :
     - *Vous & le Défi* (accroche démontrant une vraie compréhension de l'entreprise).
     - *Moi & l'Impact* (preuves concrètes et chiffrées tirées du CV).
     - *Nous & l'Équipe* (projection réelle dans le quotidien et la collaboration).
     - *Conclusion & Appel à l'échange* (ton franc, direct et courtois).
4. **Éditeur Interactif en Direct (WYSIWYG)** :
   - Visualisation fidèle au format page A4.
   - Chaque paragraphe peut être édité ou retouché directement avant export.
5. **Export PDF Haute Définition** :
   - 3 thèmes graphiques professionnels (*Moderne*, *Exécutif*, *Minimaliste*).
   - Génération vectorielle A4 sans bavure, prête à l'envoi.

---

## 🚀 Lancement Rapide

### 1. Démarrage en une seule commande

Dans votre terminal :

```bash
cd /Users/pasuta/.gemini/antigravity/scratch/motiva
./run.sh
```

Ouvrez ensuite votre navigateur sur : **[http://localhost:8000](http://localhost:8000)**.

---

## 🔑 Configuration de l'IA (Gemini)

- Vous pouvez configurer votre clé d'API directement dans l'interface (icône **Clé API** en haut à droite).
- Elle est stockée dans le `localStorage` de votre navigateur.
- Alternativement, vous pouvez créer un fichier `.env` :
  ```bash
  echo "GEMINI_API_KEY=votre_cle_ici" > .env
  ```
- *Astuce : Vous pouvez obtenir une clé gratuite en quelques secondes sur [Google AI Studio](https://aistudio.google.com/app/apikey).*
- Si vous n'avez pas de clé sous la main, un **mode démonstration réaliste** est actif pour tester immédiatement l'interface et l'export PDF.

---

## 🏗️ Structure du Projet

```
motiva/
├── app/
│   ├── main.py            # API FastAPI et routes du service
│   ├── cv_parser.py       # Parseur PDF/DOCX et extracteur de profil
│   ├── researcher.py      # Scraping d'offres et recherche entreprise
│   ├── prompt_engine.py   # Garde-fous anti-clichés et prompts structurés
│   ├── ai_generator.py    # Client Gemini & synthèse intelligente
│   └── pdf_generator.py   # Générateur de PDF vectoriel A4 (ReportLab)
├── frontend/
│   ├── index.html         # Interface utilisateur complète (Tailwind CSS)
│   ├── styles.css         # Styles A4, thèmes et règles d'impression
│   └── app.js             # Logique interactive, édition en direct et export
├── requirements.txt       # Dépendances Python
├── run.sh                 # Script de démarrage tout-en-un
└── README.md              # Documentation
```
