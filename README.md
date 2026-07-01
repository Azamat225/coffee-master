# Aroma Coffee — сайт кофейни

Красивый сайт кофейни на **Django** (фронтенд + админ-панель) и **FastAPI** (REST API для записи).

## Возможности

- Главная страница с популярными напитками
- Страница меню по категориям
- Страница «О нас»
- Онлайн-запись на столик (через FastAPI)
- Админ-панель Django для управления меню и записями

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

### 4. Запуск FastAPI (API записи)

В отдельном терминале:

```bash
python run_api.py
```

API: http://127.0.0.1:8001/docs

## Админ-панель

- URL: http://127.0.0.1:8135/admin/
- Логин: `admin`
- Пароль: `admin`

В админке можно управлять категориями, меню и записями гостей.

## API эндпоинты

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/menu` | Все позиции меню |
| GET | `/api/menu/popular` | Популярные напитки |
| POST | `/api/bookings` | Создать запись |
| GET | `/api/bookings/{id}` | Получить запись |

## Структура

```
coffee/
├── coffeeshop/       # Django-проект
├── main/             # Django-приложение (модели, шаблоны, CSS)
├── api/              # FastAPI (REST API)
├── run_api.py        # Запуск FastAPI
└── manage.py
```
