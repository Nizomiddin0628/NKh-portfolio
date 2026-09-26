#!/usr/bin/env bash
# Update the live site. Run on the server as root:
#   bash /srv/portfolio/app/scripts/deploy.sh
# Pulls the code, installs new requirements (only if they changed), applies
# migrations (content updates are migrations too), collects static files,
# compiles translations, restarts the app and checks that it answers.
set -euo pipefail

APP=/srv/portfolio/app
VENV=/srv/portfolio/venv
RUN="sudo -u portfolio"
cd "$APP"

step() { printf '\n\033[1;36m→ %s\033[0m\n' "$1"; }

step "Pulling latest code"
BEFORE=$($RUN git rev-parse HEAD)
$RUN git pull --ff-only -q
AFTER=$($RUN git rev-parse HEAD)
if [ "$BEFORE" = "$AFTER" ]; then echo "  already up to date"; else $RUN git log --oneline "$BEFORE..$AFTER" | sed 's/^/  /'; fi

if $RUN git diff --name-only "$BEFORE" "$AFTER" | grep -q '^requirements.txt$'; then
  step "Installing new requirements"
  "$VENV/bin/pip" install -q -r requirements.txt
fi

step "Applying migrations"
$RUN "$VENV/bin/python" manage.py migrate --noinput

step "Collecting static files"
$RUN "$VENV/bin/python" manage.py collectstatic --noinput -v0

step "Compiling translations"
$RUN "$VENV/bin/python" scripts/compile_po.py | tail -1

step "Restarting the app"
systemctl restart portfolio
sleep 3

# Health check straight against gunicorn, as Caddy would call it
HOST=$(grep -E '^ALLOWED_HOSTS=' .env | cut -d= -f2- | tr -d "\"'" | cut -d, -f1)
CODE=$(curl -s -o /dev/null -w '%{http_code}' -H "Host: ${HOST:-localhost}" \
       -H 'X-Forwarded-Proto: https' http://127.0.0.1:8001/en/ || true)
if [ "$CODE" = "200" ]; then
  printf '\n\033[1;32m✓ Deployed, site answers 200\033[0m\n'
else
  printf '\n\033[1;31m✗ Site answered %s — last log lines:\033[0m\n' "$CODE"
  journalctl -u portfolio -n 30 --no-pager
  exit 1
fi
