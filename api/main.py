import os
from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import get_db
from .models import Booking, MenuItem
from .schemas import BookingCreate, BookingOut, MenuItemOut

app = FastAPI(
    title='Aroma Coffee API',
    description='API для меню и записи в кофейню',
    version='1.0.0',
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


@app.post('/api/bookings', response_model=BookingOut, status_code=201)
def create_booking(data: BookingCreate, db: Session = Depends(get_db)):
    booking = Booking(
        name=data.name,
        phone=data.phone,
        email=data.email,
        date=data.date,
        time=data.time,
        guests=data.guests,
        comment=data.comment,
        status='pending',
        created_at=datetime.utcnow(),
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


@app.get('/api/bookings/{booking_id}', response_model=BookingOut)
def get_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail='Запись не найдена')
    return booking
