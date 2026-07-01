from datetime import date, datetime, time

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Category(Base):
    __tablename__ = 'main_category'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    slug: Mapped[str] = mapped_column(String(50))
    order: Mapped[int] = mapped_column(Integer, default=0)

    items: Mapped[list['MenuItem']] = relationship(back_populates='category')


class MenuItem(Base):
    __tablename__ = 'main_menuitem'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey('main_category.id'))
    name: Mapped[str] = mapped_column(String(150))
    description: Mapped[str] = mapped_column(Text, default='')
    price: Mapped[float] = mapped_column(Numeric(8, 2))
    image_emoji: Mapped[str] = mapped_column(String(10), default='☕')
    is_popular: Mapped[bool] = mapped_column(Boolean, default=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)

    category: Mapped['Category'] = relationship(back_populates='items')


class Booking(Base):
    __tablename__ = 'main_booking'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str] = mapped_column(String(20))
    email: Mapped[str] = mapped_column(String(254), default='')
    date: Mapped[date] = mapped_column(Date)
    time: Mapped[time] = mapped_column(Time)
    guests: Mapped[int] = mapped_column(Integer, default=2)
    comment: Mapped[str] = mapped_column(Text, default='')
    status: Mapped[str] = mapped_column(String(20), default='pending')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
