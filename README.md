# Aroma Coffee — сайт кофейни

Красивый сайт кофейни на **Django** (фронтенд + админ-панель) и **FastAPI** (REST API для меню).

## Возможности

- Главная страница с популярными напитками
- Страница меню по категориям
- Страница «О нас»
- Админ-панель Django для управления меню и сайтом

## Запуск

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Миграции и данные

```bash
python manage.py migrate
python manage.py create_admin
python manage.py load_initial_data
```

### 3. Запуск Django (сайт)

```bash
python run_server.py
```

Сайт: http://127.0.0.1:8135

### 4. Запуск FastAPI (API меню)

В отдельном терминале:

```bash
python run_api.py
```

API: http://127.0.0.1:8001/docs

## Админ-панель

- URL: http://127.0.0.1:8135/admin/
- Логин: `admin`
- Пароль: `admin`

В админке можно управлять категориями, меню и контентом сайта.

## API эндпоинты

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/menu` | Все позиции меню |
| GET | `/api/menu/popular` | Популярные напитки |

## Структура

```
coffee/
├── coffeeshop/       # Django-проект
├── main/             # Django-приложение (модели, шаблоны, CSS)
├── api/              # FastAPI (REST API)
├── run_api.py        # Запуск FastAPI
└── manage.py
```
