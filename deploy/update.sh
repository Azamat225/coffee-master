#!/usr/bin/env bash
# Безопасное обновление на сервере: сбрасывает конфликтующие файлы и перезапускает сервисы.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

echo "==> Сброс локальных правок deploy-скриптов (если были)..."
git checkout -- deploy/start-screen.sh deploy/stop-screen.sh 2>/dev/null || true

echo "==> Удаление локального staticfiles (соберётся заново)..."
rm -rf staticfiles

echo "==> git pull..."
git pull

if [[ ! -d venv ]]; then
    echo "ОШИБКА: нет venv. Создайте: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# shellcheck disable=SC1091
source venv/bin/activate

echo "==> collectstatic..."
python manage.py collectstatic --noinput

echo "==> Перезапуск screen..."
chmod +x deploy/stop-screen.sh deploy/start-screen.sh
./deploy/stop-screen.sh
sleep 2
./deploy/start-screen.sh

echo ""
echo "Готово. Проверка:"
screen -ls 2>/dev/null | grep green-cafe || true
