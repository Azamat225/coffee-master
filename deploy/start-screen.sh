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
DJANGO_HOST="${DJANGO_BIND%:*}"
DJANGO_PORT="${DJANGO_BIND##*:}"
LOG_DIR="${ROOT_DIR}/deploy/logs"
mkdir -p "$LOG_DIR"

if [[ ! -d venv ]]; then
    echo "Создайте venv: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

port_in_use() {
    ss -ltn 2>/dev/null | grep -q ":$1 "
}

screen_running() {
    screen -list 2>/dev/null | grep -q "\.$1"
}

http_ok() {
    local url="$1"
    local host="${2:-}"
    local code
    if [[ -n "$host" ]]; then
        code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 -H "Host: ${host}" "$url" 2>/dev/null || echo "000")"
    else
        code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 "$url" 2>/dev/null || echo "000")"
    fi
    # 2xx/3xx — ок; 400 — Django жив, но Host не тот (тоже ок для проверки порта)
    [[ "$code" =~ ^[23] ]] || [[ "$code" == "400" ]]
}

free_port_if_orphan() {
    local port="$1"
    local session="$2"
    local pattern="$3"

    if ! port_in_use "$port"; then
        return 0
    fi

    if screen_running "$session"; then
        return 0
    fi

    echo "Порт ${port} занят, но screen ${session} нет — убиваю зависшие процессы..."
    pkill -f "$pattern" 2>/dev/null || true
    sleep 1

    local pids
    pids="$(ss -ltnp 2>/dev/null | grep ":${port} " | grep -oP 'pid=\K[0-9]+' | sort -u | tr '\n' ' ' || true)"
    if [[ -n "${pids// /}" ]]; then
        # shellcheck disable=SC2086
        kill -9 $pids 2>/dev/null || true
        sleep 1
    fi
}

start_django() {
    free_port_if_orphan "$DJANGO_PORT" "green-cafe-django" "gunicorn coffeeshop.wsgi:application"

    if screen_running "green-cafe-django" && port_in_use "$DJANGO_PORT"; then
        if http_ok "http://${DJANGO_HOST}:${DJANGO_PORT}/" "green-cafe-str.ru"; then
            echo "green-cafe-django уже работает ($DJANGO_BIND)"
            return 0
        fi
        echo "green-cafe-django не отвечает — перезапускаю..."
        screen -S green-cafe-django -X quit 2>/dev/null || true
        pkill -f "gunicorn coffeeshop.wsgi:application" 2>/dev/null || true
        sleep 1
    fi

    if port_in_use "$DJANGO_PORT"; then
        echo "ОШИБКА: порт ${DJANGO_PORT} занят. Запусти: ./deploy/stop-screen.sh"
        exit 1
    fi

    screen -dmS green-cafe-django bash -lc "
        cd '$ROOT_DIR' &&
        source venv/bin/activate &&
        [[ -f .env ]] && set -a && source .env && set +a &&
        exec gunicorn coffeeshop.wsgi:application \
            --bind '$DJANGO_BIND' \
            --workers 3 \
            --timeout 120 \
            --access-logfile '$LOG_DIR/django-access.log' \
            --error-logfile '$LOG_DIR/django-error.log'
    "
    sleep 2

    if ! screen_running "green-cafe-django" || ! port_in_use "$DJANGO_PORT"; then
        echo "ОШИБКА: green-cafe-django не поднялся."
        echo "Лог: tail -50 $LOG_DIR/django-error.log"
        tail -30 "$LOG_DIR/django-error.log" 2>/dev/null || true
        exit 1
    fi

    if ! http_ok "http://${DJANGO_HOST}:${DJANGO_PORT}/" "green-cafe-str.ru"; then
        echo "ОШИБКА: Django слушает порт, но не отвечает на HTTP."
        echo "Лог: tail -50 $LOG_DIR/django-error.log"
        tail -30 "$LOG_DIR/django-error.log" 2>/dev/null || true
        exit 1
    fi

    echo "Запущен screen: green-cafe-django ($DJANGO_BIND)"
}

start_api() {
    free_port_if_orphan "$API_PORT" "green-cafe-api" "uvicorn api.main:app"

    if screen_running "green-cafe-api" && port_in_use "$API_PORT"; then
        if http_ok "http://${API_HOST}:${API_PORT}/docs"; then
            echo "green-cafe-api уже работает ($API_BIND)"
            return 0
        fi
        echo "green-cafe-api не отвечает — перезапускаю..."
        screen -S green-cafe-api -X quit 2>/dev/null || true
        pkill -f "uvicorn api.main:app" 2>/dev/null || true
        sleep 1
    fi

    if port_in_use "$API_PORT"; then
        echo "ОШИБКА: порт ${API_PORT} занят. Запусти: ./deploy/stop-screen.sh"
        exit 1
    fi

    screen -dmS green-cafe-api bash -lc "
        cd '$ROOT_DIR' &&
        source venv/bin/activate &&
        [[ -f .env ]] && set -a && source .env && set +a &&
        exec uvicorn api.main:app \
            --host '$API_HOST' \
            --port '$API_PORT' \
            --workers 2 \
            --log-level info
    "
    sleep 2

    if ! screen_running "green-cafe-api" || ! port_in_use "$API_PORT"; then
        echo "ОШИБКА: green-cafe-api не поднялся."
        exit 1
    fi

    echo "Запущен screen: green-cafe-api ($API_BIND)"
}

start_django
start_api

echo ""
echo "Проверка портов:"
ss -ltnp | grep -E ":${DJANGO_PORT}|:${API_PORT}" || true
echo ""
echo "Screen-сессии:"
screen -ls 2>/dev/null | grep -E 'green-cafe-(django|api)' || echo "(нет сессий)"
echo ""
echo "Подключиться: screen -r green-cafe-django  или  screen -r green-cafe-api"
echo "Логи Django:  tail -f $LOG_DIR/django-error.log"
