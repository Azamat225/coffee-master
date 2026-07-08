import os
from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import get_db
from .models import MenuItem
from .schemas import MenuItemOut

app = FastAPI(
    title='Green Studio API',
    description='API для меню кофейни',
    version='1.1.0',
)

CORS_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        'API_CORS_ORIGINS',
        'http://127.0.0.1:8135,http://localhost:8135,'
        'https://green-cafe-str.ru,https://www.green-cafe-str.ru',
    ).split(',')
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/api/menu', response_model=list[MenuItemOut])
def get_menu(db: Session = Depends(get_db)):
    items = (
        db.query(MenuItem)
        .filter(MenuItem.is_available.is_(True))
        .order_by(MenuItem.category_id, MenuItem.name)
        .all()
    )
    return [
        MenuItemOut(
            id=item.id,
            name=item.name,
            description=item.description or '',
            price=float(item.price),
            image_emoji=item.image_emoji,
            is_popular=item.is_popular,
            category_name=item.category.name if item.category else '',
        )
        for item in items
    ]


@app.get('/api/menu/popular', response_model=list[MenuItemOut])
def get_popular_menu(db: Session = Depends(get_db)):
    items = (
        db.query(MenuItem)
        .filter(MenuItem.is_available.is_(True), MenuItem.is_popular.is_(True))
        .limit(6)
        .all()
    )
    return [
        MenuItemOut(
            id=item.id,
            name=item.name,
            description=item.description or '',
            price=float(item.price),
            image_emoji=item.image_emoji,
            is_popular=item.is_popular,
            category_name=item.category.name if item.category else '',
        )
        for item in items
    ]


@app.get('/api/bookings', include_in_schema=False)
def bookings_disabled():
    raise HTTPException(status_code=410, detail='Онлайн-запись больше недоступна')

