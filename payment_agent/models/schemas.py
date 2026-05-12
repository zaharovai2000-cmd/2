"""
Pydantic-схемы для валидации данных на входе и выходе API.
Обновлено: добавлены схемы для платёжного флоу.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from models.orm import PaymentStatus, PaymentMethod
import re


# ── Продукты ──────────────────────────────────────────────────────────────

class ProductOut(BaseModel):
    id: int
    name: str
    label: str
    description: str
    composition: str
    price: float
    category: str
    color: str
    size: str
    image: str

    model_config = {"from_attributes": True}


# ── Заказы ────────────────────────────────────────────────────────────────

class OrderItemIn(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., ge=1, le=100)


class OrderCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    phone: str = Field(..., min_length=7, max_length=20)
    address: str = Field(..., min_length=5, max_length=500)
    date: str = Field(..., description="Дата доставки в формате YYYY-MM-DD")
    time: str = Field(..., description="Время доставки, например '14:00'")
    wishes: str = Field(default="", max_length=1000)
    payment_method: PaymentMethod = Field(default=PaymentMethod.CARD)
    items: list[OrderItemIn] = Field(..., min_length=1)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        cleaned = re.sub(r"[\s\-\(\)\+]", "", v)
        if not cleaned.isdigit() or len(cleaned) < 7:
            raise ValueError("Некорректный номер телефона")
        return v

    @field_validator("date")
    @classmethod
    def validate_date(cls, v: str) -> str:
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            raise ValueError("Дата должна быть в формате YYYY-MM-DD")
        return v


class OrderOut(BaseModel):
    """
    Ответ при создании заказа.
    Включает payment_status и payment_intent_id для фронтенда.
    """
    id: int
    created_at: datetime
    customer_name: str
    customer_phone: str
    delivery_address: str
    delivery_date: str
    delivery_time: str
    wishes: str
    total_amount: float
    payment_method: PaymentMethod
    payment_status: PaymentStatus
    payment_intent_id: Optional[str] = None

    model_config = {"from_attributes": True}


# ── Платежи ───────────────────────────────────────────────────────────────

class PaymentIntentCreate(BaseModel):
    """Запрос на создание PaymentIntent."""
    order_id: int = Field(..., gt=0, description="ID созданного заказа")


class PaymentIntentResponse(BaseModel):
    """
    Ответ с данными для Stripe Elements на фронтенде.
    client_secret передаётся в stripe.confirmPayment().
    """
    client_secret: str = Field(..., description="Stripe client secret для Elements")
    payment_intent_id: str = Field(..., description="ID PaymentIntent (pi_xxx)")
    amount: int = Field(..., description="Сумма в копейках (для отображения)")
    currency: str = Field(..., description="Валюта ISO 4217")
    publishable_key: str = Field(..., description="Публичный ключ Stripe для фронтенда")


class WebhookResponse(BaseModel):
    """Ответ на webhook от Stripe/ЮКассы."""
    received: bool = True
    status: str = "ok"


class YokassaPaymentCreate(BaseModel):
    """Запрос на создание платежа в ЮКассе."""
    order_id: int = Field(..., gt=0)


class YokassaPaymentResponse(BaseModel):
    """Ответ с URL для редиректа в ЮКассе."""
    payment_id: str
    confirmation_url: str
    status: str


# ── Отзывы ────────────────────────────────────────────────────────────────

class ReviewOut(BaseModel):
    id: int
    author_name: str
    date: str
    rating: int
    text: str
    avatar: str
    bouquet: str

    model_config = {"from_attributes": True}