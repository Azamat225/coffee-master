#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

DJANGO_BIND="${DJANGO_BIND:-127.0.0.1:8135}"
API_BIND="${API_BIND:-127.0.0.1:8036}"
DJANGO_PORT="${DJANGO_BIND##*:}"
API_PORT="${API_BIND##*:}"

kill_port() {
    local port="$1"
    local pids
    pids="$(ss -ltnp 2>/dev/null | grep ":${port} " | grep -oP 'pid=\K[0-9]+' | sort -u || true)"
    if [[ -n "$pids" ]]; then
        echo "Останавливаю процессы на порту ${port}: ${pids//$'\n'/ }"
        # shellcheck disable=SC2086
        kill $pids 2>/dev/null || true
        sleep 1
    fi
}

for session in green-cafe-django green-cafe-api; do
    if screen -list | grep -q "\.${session}"; then
        screen -S "$session" -X quit || true
        echo "Screen остановлен: $session"
    fi
done

kill_port "$DJANGO_PORT"
kill_port "$API_PORT"

echo "Green Cafe остановлен."
