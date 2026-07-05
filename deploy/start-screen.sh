#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

if [[ -f .env ]]; then
    set -a
    # shellcheck disable=SC1091
    source .env
    set +a
fi

DJANGO_BIND="${DJANGO_BIND:-127.0.0.1:8135}"
API_BIND="${API_BIND:-127.0.0.1:8036}"
API_HOST="${API_BIND%:*}"
API_PORT="${API_BIND##*:}"

if [[ ! -d venv ]]; then
    echo "Создайте venv: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# shellcheck disable=SC1091
source venv/bin/activate

if screen -list | grep -q '\.green-cafe-django'; then
    echo "Screen green-cafe-django уже запущен"
else
    screen -dmS green-cafe-django bash -lc "
        cd '$ROOT_DIR' &&
        source venv/bin/activate &&
        [[ -f .env ]] && set -a && source .env && set +a &&
        exec gunicorn coffeeshop.wsgi:application --bind '$DJANGO_BIND' --workers 3
    "
    echo "Запущен screen: green-cafe-django ($DJANGO_BIND)"
fi

if screen -list | grep -q '\.green-cafe-api'; then
    echo "Screen green-cafe-api уже запущен"
else
    screen -dmS green-cafe-api bash -lc "
        cd '$ROOT_DIR' &&
        source venv/bin/activate &&
        [[ -f .env ]] && set -a && source .env && set +a &&
        exec uvicorn api.main:app --host '$API_HOST' --port '$API_PORT' --workers 2
    "
    echo "Запущен screen: green-cafe-api ($API_BIND)"
fi

echo ""
echo "Подключиться: screen -r green-cafe-django  или  screen -r green-cafe-api"
echo "Список:       screen -ls"
