from datetime import date, time

from pydantic import BaseModel, Field


class MenuItemOut(BaseModel):
    id: int
    name: str
    description: str
    price: float
    image_emoji: str
    is_popular: bool
    category_name: str

    model_config = {'from_attributes': True}


class BookingCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., min_length=5, max_length=20)
    email: str = ''
    date: date
    time: time
    guests: int = Field(default=2, ge=1, le=20)
    comment: str = ''


class BookingOut(BaseModel):
    id: int
    name: str
    phone: str
    date: date
    time: time
    guests: int
    status: str

    model_config = {'from_attributes': True}
