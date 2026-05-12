## 📋 Что сделано

• **`main.py`** — точка входа приложения: создаёт FastAPI-экземпляр, подключает все роутеры, настраивает CORS, запускает uvicorn. Именно здесь собирается всё приложение.

• **`database.py`** — подключение к SQLite через SQLAlchemy с async-поддержкой. Одна переменная `DATABASE_URL` позволяет переключиться на PostgreSQL без изменения остального кода.

• **`models/orm.py`** — ORM-модели (таблицы в БД): Product, Order, Review. SQLAlchemy описывает структуру таблиц и связи между ними.

• **`models/schemas.py`** — Pydantic-модели для валидации входящих и исходящих данных. Отделены от ORM-моделей, чтобы API и БД можно было менять независимо.

• **`routers/products.py`** — эндпоинты для товаров: список с фильтрацией и детальная карточка. Фильтры применяются на уровне SQL-запроса, не в Python.

• **`routers/orders.py`** — приём заказа: валидация, сохранение в БД, заглушка уведомления, возврат order_id. Содержит логику платёжной заглушки.

• **`routers/reviews.py`** — список отзывов из БД, предзаполненных через seed.

• **`services/notifications.py`** — заглушка SMS/email-уведомлений с логированием в консоль. Реальный сервис подключается сюда без изменения роутеров.

• **`seed_data.py`** — скрипт первоначального наполнения БД: 12 товаров (точная копия frontend data/products.ts) и 8 отзывов. Запускается один раз перед стартом.

• **`requirements.txt`** — все зависимости с зафиксированными версиями для воспроизводимой установки.

---

## Структура проекта

---

## `requirements.txt`

---

## `.env.example`

---

## `database.py`

---

## `models/orm.py`

---

## `models/schemas.py`

---

## `services/notifications.py`

---

## `routers/products.py`

---

## `routers/orders.py`

```python
# routers/orders.py
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models.orm import Order, Product, OrderStatus
from models.schemas import OrderCreate, OrderOut
from services.notifications import (
    OrderNotificationData,
    send_order_confirmation,
    send_order_to_manager,
)

logger = logging.getLogger("orders")

router = APIRouter(prefix="/orders", tags=["Заказы"])

@router.post(
    "",
    response_model=OrderOut,
    status_code=201,
    summary="Создать заказ",
    description=(
        "Принимает данные формы заказа. Совместим с OrderFormData из frontend types/index.ts. "
        "Не требует регистрации. При payment_method=card_online возвращает payment_url=null "
        "(будет заполнен платёжным агентом)."
    ),
    responses={
        404: {"description": "Товар не найден"},
        422: {"description": "Ошибка валидации (неверный телефон, прошедшая дата и т.д.)"},
    },
)
async def create_order(
    order_data: OrderCreate,
    db: AsyncSession = Depends(get_db),
):
    # ── 1. Проверяем, что товар существует ──────────────────────────────────
    product_result = await db.execute(
        select(Product).where(
            Product.id == order_data.product_id,
            Product.is_active == True  # noqa: E712
        )
    )
    product = product_result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=404,
            detail=f"Товар с id={order_data.product_id} не найден или недоступен"
        )

    # ── 2. Считаем итоговую сумму ────────────────────────────────────────────
    total_price = product.price * order_data.quantity

    # ── 3. Определяем payment_url (заглушка) ────────────────────────────────
    # Реальная ссылка будет генерироваться payment_agent (Stripe, ЮКасса и т.д.)
    payment_url = None
    if order_data.payment_method == "card_online":
        # Заглушка: в продакшне здесь будет вызов платёжного API
        # payment_url = await payment_service.create_payment_link(total_price, order_id)
        payment_url = None
        logger.info(
            "💳 Платёж онлайн: payment_url будет добавлен платёжным агентом. "
            "Сумма: %.0f ₽",
            total_price
        )

    # ── 4. Сохраняем заказ в БД ─────────────────────────────────────────────
    new_order = Order(
        name=order_data.name,
        phone=order_data.phone,
        address=order_data.address,
        delivery_date=order_data.delivery_date,
        delivery_time=order_data.delivery_time,

---
## 📁 Созданные файлы
- [requirements-2.txt](requirements-2.txt)
- [requirements-3.txt](requirements-3.txt)
- [.env.example](.env.example)
- [database.py](database.py)
- [orm.py](orm.py)
- [schemas.py](schemas.py)
- [notifications.py](notifications.py)
- [products.py](products.py)