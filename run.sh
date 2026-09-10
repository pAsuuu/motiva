#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "=========================================================="
echo "    🚀 Motiva — Lettres de motivation authentiques & anti-IA"
echo "=========================================================="

if [ ! -d ".venv" ]; then
    echo "📦 Création de l'environnement virtuel Python..."
    python3 -m venv .venv
    echo "⬇️  Installation des dépendances..."
    .venv/bin/pip install -r requirements.txt
fi

echo "🌐 Lancement du serveur sur http://localhost:8000..."
echo "👉 Ouvrez http://localhost:8000 dans votre navigateur."
echo "=========================================================="

exec .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
