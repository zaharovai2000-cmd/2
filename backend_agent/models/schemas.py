from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, field_validator, model_validator, Field
import phonenumbers
import re


# ── Вспомогательная валидация ────────────────────────────────────────────────

def validate_russian_phone(phone: str) -> str:
    """
    Принимает форматы: +79991234567, 89991234567, 9991234567
    Возвращает нормализованный: +79991234567
    Бросает ValueError при невалидном номере.
    """
    # Убираем пробелы, дефисы, скобки
    cleaned = re.sub(r"[\s\-\(\)]", "", phone)

    # Приводим к формату +7...
    if cleaned.startswith("8") and len(cleaned) == 11:
        cleaned = "+7" + cleaned[1:]
    elif cleaned.startswith("7") and len(cleaned) == 11:
        cleaned = "+" + cleaned
    elif not cleaned.startswith("+"):
        cleaned = "+7" + cleaned

    try:
        parsed = phonenumbers.parse(cleaned, "RU")
        if not phonenumbers.is_valid_number(parsed):
            raise ValueError("Невалидный номер телефона")
        return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except phonenumbers.NumberParseException:
        raise ValueError(
            "Неверный формат телефона. Используйте: +79991234567 или 89991234567"
        )


# ── Product schemas ──────────────────────────────────────────────────────────

class ProductOut(BaseModel):
    """Исходящая схема товара — точное соответствие Product из types/index.ts."""
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


class ProductListResponse(BaseModel):
    """Обёртка для списка товаров с метаданными."""
    items: list[ProductOut]
    total: int
    filters_applied: dict


# ── Order schemas ────────────────────────────────────────────────────────────

class OrderCreate(BaseModel):
    """
    Входящая схема заказа.
    Совместима с OrderFormData из frontend types/index.ts.
    Поля name, phone, address, date, time, wishes + product_id, quantity, payment_method.
    """
    # Личные данные (из OrderFormData)
    name: str = Field(
        ...,
        min_length=2,
        max_length=200,
        description="Имя получателя",
        examples=["Иван Петров"]
    )
    phone: str = Field(
        ...,
        description="Телефон в российском формате",
        examples=["+79991234567", "89991234567"]
    )
    address: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Адрес доставки",
        examples=["г. Москва, ул. Пушкина, д. 10, кв. 5"]
    )

    # Доставка (в frontend: date → delivery_date, time → delivery_time)
    delivery_date: date = Field(
        ...,
        description="Дата доставки (не раньше сегодня)",
        examples=["2024-06-15"]
    )
    delivery_time: str = Field(
        ...,
        pattern=r"^([01]\d|2[0-3]):([0-5]\d)$",
        description="Время доставки в формате HH:MM",
        examples=["14:30"]
    )
    wishes: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Пожелания (открытка, цвет ленты и т.д.)",
        examples=["Пожалуйста, добавьте открытку 'С днём рождения!'"]
    )

    # Товар
    product_id: int = Field(..., gt=0, description="ID товара из каталога")
    quantity: int = Field(default=1, ge=1, le=100, description="Количество букетов")

    # Платёж
    payment_method: str = Field(
        ...,
        description="Способ оплаты: card_online или cash_courier",
        examples=["card_online"]
    )

    @field_validator("phone")
    @classmethod
    def phone_must_be_russian(cls, v: str) -> str:
        return validate_russian_phone(v)

    @field_validator("delivery_date")
    @classmethod
    def date_not_in_past(cls, v: date) -> date:
        if v < date.today():
            raise ValueError("Дата доставки не может быть в прошлом")
        return v

    @field_validator("payment_method")
    @classmethod
    def payment_method_valid(cls, v: str) -> str:
        allowed = {"card_online", "cash_courier"}
        if v not in allowed:
            raise ValueError(f"Способ оплаты должен быть одним из: {', '.join(allowed)}")
        return v

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Имя не может быть пустым")
        return v.strip()


class OrderOut(BaseModel):
    """Исходящая схема после создания заказа."""
    order_id: int
    status: str
    product_name: str
    total_price: float
    delivery_date: date
    delivery_time: str
    payment_method: str
    payment_url: Optional[str] = None   # null для card_online (будет добавлен позже)
    message: str                         # Человекочитаемое подтверждение

    model_config = {"from_attributes": True}


# ── Review schemas ───────────────────────────────────────────────────────────

class ReviewOut(BaseModel):
    """Исходящая схема отзыва — соответствует Review из types/index.ts."""
    id: int
    name: str
    date: str
    rating: int
    text: str
    avatar: str
    bouquet: str

    model_config = {"from_attributes": True}


class ReviewListResponse(BaseModel):
    items: list[ReviewOut]
    total: int


# ── Health-check ─────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    database: str
    version: str
    timestamp: datetime