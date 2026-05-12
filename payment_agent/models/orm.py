"""
ORM-модели SQLAlchemy. Описывают структуру таблиц в БД.
Обновлено: добавлены поля payment_status, payment_intent_id, payment_method в Order.
"""
from datetime import datetime
from sqlalchemy import (
    Integer, String, Float, Text, DateTime,
    ForeignKey, Enum as SAEnum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base
import enum


class PaymentStatus(str, enum.Enum):
    """Статусы оплаты заказа."""
    PENDING = "pending"           # Ожидает оплаты (карта, intent создан)
    PENDING_CASH = "pending_cash" # Ожидает оплаты наличными курьеру
    PAID = "paid"                 # Успешно оплачен
    FAILED = "failed"             # Оплата не прошла
    REFUNDED = "refunded"         # Возврат выполнен
    CANCELLED = "cancelled"       # Отменён


class PaymentMethod(str, enum.Enum):
    """Способы оплаты."""
    CARD = "card"       # Онлайн картой через Stripe
    CASH = "cash"       # Наличными курьеру
    YOKASSA = "yokassa" # ЮКасса (для РФ)


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    label: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(Text)
    composition: Mapped[str] = mapped_column(Text)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    category: Mapped[str] = mapped_column(String(100))
    color: Mapped[str] = mapped_column(String(50))
    size: Mapped[str] = mapped_column(String(50))
    image: Mapped[str] = mapped_column(String(500))

    order_items: Mapped[list["OrderItem"]] = relationship(
        back_populates="product"
    )


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    # Данные покупателя
    customer_name: Mapped[str] = mapped_column(String(200), nullable=False)
    customer_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    delivery_address: Mapped[str] = mapped_column(String(500), nullable=False)
    delivery_date: Mapped[str] = mapped_column(String(20), nullable=False)
    delivery_time: Mapped[str] = mapped_column(String(20), nullable=False)
    wishes: Mapped[str] = mapped_column(Text, default="")

    # Суммы
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)

    # ── Платёжные поля ────────────────────────────────────────────────────
    payment_method: Mapped[str] = mapped_column(
        SAEnum(PaymentMethod),
        nullable=False,
        default=PaymentMethod.CARD
    )
    payment_status: Mapped[str] = mapped_column(
        SAEnum(PaymentStatus),
        nullable=False,
        default=PaymentStatus.PENDING
    )
    # ID из Stripe (pi_xxx) или ЮКассы — null для cash-заказов
    payment_intent_id: Mapped[str | None] = mapped_column(
        String(200), nullable=True, unique=True, index=True
    )
    # Сырой ответ от платёжной системы для отладки (не показываем в API)
    payment_raw_response: Mapped[str | None] = mapped_column(Text, nullable=True)

    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("orders.id"), nullable=False
    )
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    price_at_order: Mapped[float] = mapped_column(Float, nullable=False)

    order: Mapped["Order"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship(back_populates="order_items")


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author_name: Mapped[str] = mapped_column(String(200))
    date: Mapped[str] = mapped_column(String(20))
    rating: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text)
    avatar: Mapped[str] = mapped_column(String(500))
    bouquet: Mapped[str] = mapped_column(String(200))