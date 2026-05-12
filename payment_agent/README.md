## 📋 Что сделано

• **`routers/payments.py`** — главный файл с двумя эндпоинтами: `POST /payments/create-intent` создаёт Stripe PaymentIntent и возвращает client_secret фронтенду; `POST /payments/webhook` принимает события от Stripe и обновляет статус заказа в БД.

• **`services/stripe_service.py`** — вся логика работы со Stripe API инкапсулирована здесь: создание PaymentIntent, верификация webhook-подписи, маппинг Stripe-статусов в наши статусы. Роутер использует этот сервис, не зная деталей Stripe SDK.

• **`services/yokassa_service.py`** — опциональный сервис ЮКассы для РФ-рынка. Та же интерфейсная логика, что и Stripe-сервис, подключается через feature-флаг в `.env`.

• **`models/orm.py`** (обновление) — добавлены поля `payment_status`, `payment_intent_id`, `payment_method` в модель Order. Три статуса: `pending`, `paid`, `failed`.

• **`models/schemas.py`** (обновление) — обновлена схема `OrderOut` с новыми полями; добавлены схемы `PaymentIntentCreate`, `PaymentIntentResponse`, `WebhookResponse`.

• **`routers/orders.py`** (обновление) — убрана заглушка оплаты. При `payment_method=cash` заказ сразу получает статус `pending_cash`; при `payment_method=card` — ждёт Stripe webhook.

• **`components/StripePayment.tsx`** — React-компонент с Stripe Elements (`PaymentElement`). Инкапсулирует всю логику: загрузку SDK, создание PaymentIntent через API, подтверждение оплаты, отображение ошибок. Вставляется в `OrderForm.tsx` как замена заглушки.

• **`components/OrderForm.tsx`** (обновление) — добавлен выбор способа оплаты (карта/наличные), условный рендер `StripePayment`, двухшаговый флоу: сначала создаётся заказ, потом оплата.

• **`.env.example`** (обновление) — добавлены `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PUBLISHABLE_KEY`, `YOKASSA_SHOP_ID`, `YOKASSA_SECRET_KEY`.

• **`PCI_DSS_CHECKLIST.md`** — документ с чеклистом безопасности: что сделано для соответствия PCI DSS, что нужно сделать при переходе в продакшн.

---

## Архитектура платёжного флоу

---

## Backend: обновлённые файлы

### `requirements.txt`

---

### `.env.example`

---

### `config.py`

---

### `models/orm.py`

---

### `models/schemas.py`

---

### `services/stripe_service.py`

---

### `services/yokassa_service.py`

```python
# services/yokassa_service.py
"""
Опциональный сервис ЮКассы для приёма платежей на РФ-рынке.
Активируется через YOKASSA_ENABLED=true в .env

ЮКасса использует redirect-flow:
1. Создаём платёж → получаем URL для редиректа
2. Покупатель переходит на страницу ЮКассы и платит
3. ЮКасса отправляет webhook с результатом
4. Мы обновляем статус заказа

Документация: https://yookassa.ru/developers/api
"""
import uuid
import logging
import json
from typing import Optional

from config import settings

logger = logging.getLogger(__name__)

class YokassaPaymentError(Exception):
    """Ошибка при работе с ЮКассой."""
    def __init__(self, message: str, code: Optional[str] = None):
        super().__init__(message)
        self.code = code

def _get_yokassa_client():
    """
    Ленивая инициализация клиента ЮКассы.
    Импортируем только если YOKASSA_ENABLED=true.
    """
    if not settings.yokassa_enabled:
        raise YokassaPaymentError(
            "ЮКасса не включена: установите YOKASSA_ENABLED=true",
            code="not_enabled"
        )

    if not settings.yokassa_shop_id or not settings.yokassa_secret_key:
        raise YokassaPaymentError(
            "ЮКасса не настроена: провер

---
## 📁 Созданные файлы
- [requirements-2.txt](requirements-2.txt)
- [requirements-3.txt](requirements-3.txt)
- [.env.example](.env.example)
- [config.py](config.py)
- [orm.py](orm.py)
- [schemas.py](schemas.py)
- [stripe_service.py](stripe_service.py)