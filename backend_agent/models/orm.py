from datetime import datetime, date
from sqlalchemy import (
    Integer, String, Float, Text, DateTime, Date, Time,
    Enum as SAEnum, func
)
from sqlalchemy.orm import Mapped, mapped_column
from database import Base
import enum


# ── Enums (синхронизированы с frontend types/index.ts) ──────────────────────

class ProductLabel(str, enum.Enum):
    HIT = "ХИТ"
    NEW = "НОВИНКА"
    POPULAR = "ПОПУЛЯРНОЕ"


class ProductCategory(str, enum.Enum):
    ROMANCE = "Романтика"
    BIRTHDAY = "День рождения"
    WEDDING = "Свадьба"
    CORPORATE = "Корпоратив"
    JUST_BECAUSE = "Просто так"


class ProductColor(str, enum.Enum):
    RED = "Красный"
    PINK = "Розовый"
    WHITE = "Белый"
    YELLOW = "Жёлтый"
    MIXED = "Смешанный"
    PURPLE = "Фиолетовый"


class ProductSize(str, enum.Enum):
    SMALL = "Маленький"
    MEDIUM = "Средний"
    LARGE = "Большой"


class PaymentMethod(str, enum.Enum):
    CARD_ONLINE = "card_online"
    CASH_COURIER = "cash_courier"


class OrderStatus(str, enum.Enum):
    PENDING = "pending"       # Ожидает подтверждения
    CONFIRMED = "confirmed"   # Подтверждён
    DELIVERING = "delivering" # В доставке
    DELIVERED = "delivered"   # Доставлен
    CANCELLED = "cancelled"   # Отменён


# ── ORM-модели ───────────────────────────────────────────────────────────────

class Product(Base):
    """Товар (букет) — соответствует интерфейсу Product из types/index.ts."""
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    label: Mapped[str] = mapped_column(
        SAEnum(ProductLabel, values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    composition: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    category: Mapped[str] = mapped_column(
        SAEnum(ProductCategory, values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )
    color: Mapped[str] = mapped_column(
        SAEnum(ProductColor, values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )
    size: Mapped[str] = mapped_column(
        SAEnum(ProductSize, values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )
    image: Mapped[str] = mapped_column(String(500), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Order(Base):
    """Заказ — создаётся через POST /order без регистрации пользователя."""
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Данные из OrderFormData (frontend types/index.ts)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    address: Mapped[str] = mapped_column(Text, nullable=False)
    delivery_date: Mapped[date] = mapped_column(Date, nullable=False)
    delivery_time: Mapped[str] = mapped_column(String(10), nullable=False)
    wishes: Mapped[str] = mapped_column(Text, nullable=True)

    # Товар и количество
    product_id: Mapped[int] = mapped_column(Integer, nullable=False)
    product_name: Mapped[str] = mapped_column(String(200), nullable=False)  # снапшот названия
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    total_price: Mapped[float] = mapped_column(Float, nullable=False)

    # Платёж
    payment_method: Mapped[str] = mapped_column(
        SAEnum(PaymentMethod, values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )
    payment_url: Mapped[str] = mapped_column(String(500), nullable=True)  # заглушка

    # Статус
    status: Mapped[str] = mapped_column(
        SAEnum(OrderStatus, values_callable=lambda x: [e.value for e in x]),
        default=OrderStatus.PENDING.value
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Review(Base):
    """Отзыв покупателя."""
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    date: Mapped[str] = mapped_column(String(20), nullable=False)   # "15 марта 2024"
    rating: Mapped[int] = mapped_column(Integer, nullable=False)    # 1–5
    text: Mapped[str] = mapped_column(Text, nullable=False)
    avatar: Mapped[str] = mapped_column(String(500), nullable=False)
    bouquet: Mapped[str] = mapped_column(String(200), nullable=False)  # название букета
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )