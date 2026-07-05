#!/usr/bin/env bash
set -euo pipefail

for session in green-cafe-django green-cafe-api; do
    if screen -list | grep -q "\.${session}"; then
        screen -S "$session" -X quit
        echo "Остановлен: $session"
    else
        echo "Не запущен: $session"
    fi
done
