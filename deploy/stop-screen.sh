#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

DJANGO_BIND="${DJANGO_BIND:-127.0.0.1:8135}"
API_BIND="${API_BIND:-127.0.0.1:8036}"
DJANGO_PORT="${DJANGO_BIND##*:}"
API_PORT="${API_BIND##*:}"

stop_screen() {
    local session="$1"
    if screen -list 2>/dev/null | grep -q "\.${session}"; then
        screen -S "$session" -X quit 2>/dev/null || true
        echo "Screen остановлен: $session"
    fi
}

kill_port() {
    local port="$1"
    local attempt pids

    for attempt in 1 2 3; do
        pids="$(ss -ltnp 2>/dev/null | grep ":${port} " | grep -oP 'pid=\K[0-9]+' | sort -u | tr '\n' ' ' || true)"
        pids="${pids// /}"
        if [[ -z "$pids" ]]; then
            return 0
        fi
        echo "Останавливаю процессы на порту ${port}: ${pids}"
        # shellcheck disable=SC2086
        kill $pids 2>/dev/null || true
        sleep 1
        # shellcheck disable=SC2086
        kill -9 $pids 2>/dev/null || true
        sleep 1
    done

    if ss -ltn 2>/dev/null | grep -q ":${port} "; then
        echo "ВНИМАНИЕ: порт ${port} всё ещё занят"
        return 1
    fi
}

stop_screen green-cafe-django
stop_screen green-cafe-api

# Убиваем процессы по имени (на случай если screen уже умер, а gunicorn/uvicorn остались)
pkill -f "gunicorn coffeeshop.wsgi:application.*${DJANGO_BIND}" 2>/dev/null || true
pkill -f "gunicorn coffeeshop.wsgi:application.*:${DJANGO_PORT}" 2>/dev/null || true
pkill -f "uvicorn api.main:app.*--port ${API_PORT}" 2>/dev/null || true
pkill -f "uvicorn api.main:app.*:${API_PORT}" 2>/dev/null || true
sleep 1

kill_port "$DJANGO_PORT" || true
kill_port "$API_PORT" || true

echo "Green Cafe остановлен."
