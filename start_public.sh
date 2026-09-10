#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

# Kill any previous instances on port 8000
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
pkill -f "cloudflared tunnel" 2>/dev/null || true

echo "Starting Motiva Backend on port 8000..."
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 > /tmp/motiva_server.log 2>&1 &
UVICORN_PID=$!

sleep 2

echo "Starting Cloudflare Public Tunnel..."
cloudflared tunnel --url http://127.0.0.1:8000 > /tmp/cloudflared.log 2>&1 &
CLOUDFLARED_PID=$!

# Wait for public URL to appear in logs
for i in {1..25}; do
    URL=$(grep -o 'https://[a-zA-Z0-9-]*\.trycloudflare\.com' /tmp/cloudflared.log 2>/dev/null | head -n 1 || true)
    if [ -n "$URL" ]; then
        echo "$URL" > "$DIR/public_url.txt"
        echo "=========================================================="
        echo "   🌍 MOTIVA EST EN LIGNE SUR INTERNET !"
        echo "   👉 URL PUBLIQUE : $URL"
        echo "=========================================================="
        break
    fi
    sleep 1
done

# Keep script waiting
wait $UVICORN_PID $CLOUDFLARED_PID
