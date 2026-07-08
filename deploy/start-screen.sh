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
DJANGO_PORT="${DJANGO_BIND##*:}"

if [[ ! -d venv ]]; then
    echo "Создайте venv: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

port_in_use() {
    ss -ltn 2>/dev/null | grep -q ":$1 "
}

if port_in_use "$DJANGO_PORT"; then
    echo "Django уже работает на ${DJANGO_BIND} (screen не нужен)."
elif screen -list | grep -q '\.green-cafe-django'; then
    echo "Screen green-cafe-django уже запущен"
else
    screen -dmS green-cafe-django bash -lc "
        cd '$ROOT_DIR' &&
        source venv/bin/activate &&
        [[ -f .env ]] && set -a && source .env && set +a &&
        exec gunicorn coffeeshop.wsgi:application --bind '$DJANGO_BIND' --workers 3
    "
    sleep 1
    if screen -list | grep -q '\.green-cafe-django' && port_in_use "$DJANGO_PORT"; then
        echo "Запущен screen: green-cafe-django ($DJANGO_BIND)"
    else
        echo "ОШИБКА: green-cafe-django не поднялся. Запусти вручную:"
        echo "  screen -S green-cafe-django"
        echo "  cd $ROOT_DIR && source venv/bin/activate && gunicorn coffeeshop.wsgi:application --bind $DJANGO_BIND --workers 3"
        exit 1
    fi
fi

if port_in_use "$API_PORT"; then
    echo "API уже работает на ${API_BIND} (screen не нужен)."
elif screen -list | grep -q '\.green-cafe-api'; then
    echo "Screen green-cafe-api уже запущен"
else
    screen -dmS green-cafe-api bash -lc "
        cd '$ROOT_DIR' &&
        source venv/bin/activate &&
        [[ -f .env ]] && set -a && source .env && set +a &&
        exec uvicorn api.main:app --host '$API_HOST' --port '$API_PORT' --workers 2
    "
    sleep 1
    if screen -list | grep -q '\.green-cafe-api' && port_in_use "$API_PORT"; then
        echo "Запущен screen: green-cafe-api ($API_BIND)"
    else
        echo "ОШИБКА: green-cafe-api не поднялся."
        exit 1
    fi
fi

echo ""
echo "Проверка портов:"
ss -ltnp | grep -E ":${DJANGO_PORT}|:${API_PORT}" || true
echo ""
echo "Подключиться: screen -r green-cafe-django  или  screen -r green-cafe-api"
echo "Список:       screen -ls"
