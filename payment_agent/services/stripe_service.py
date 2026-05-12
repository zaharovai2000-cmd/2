"""
Инкапсулирует всю логику работы со Stripe API.
Роутер вызывает методы этого сервиса, не зная деталей SDK.

Ключевые принципы PCI DSS:
- Карточные данные НИКОГДА не касаются нашего сервера
- Мы создаём PaymentIntent и получаем client_secret
- Фронтенд передаёт карту напрямую в Stripe через Elements
- Мы только верифицируем webhook-подпись для подтверждения оплаты
"""
import logging
import json
from typing import Optional

import stripe
from stripe import StripeError

from config import settings

logger = logging.getLogger(__name__)

# Инициализируем Stripe SDK один раз при импорте
stripe.api_key = settings.stripe_secret_key
# Фиксируем версию API для предсказуемого поведения
stripe.api_version = "2024-04-10"


class StripePaymentError(Exception):
    """Ошибка при работе со Stripe."""
    def __init__(self, message: str, code: Optional[str] = None):
        super().__init__(message)
        self.code = code


async def create_payment_intent(
    order_id: int,
    amount_rub: float,
    customer_name: str,
    customer_phone: str,
    currency: str = None,
) -> dict:
    """
    Создаёт PaymentIntent в Stripe.

    Args:
        order_id: ID нашего заказа (сохраняем в metadata для webhook)
        amount_rub: Сумма в рублях (конвертируем в копейки внутри)
        customer_name: Имя покупателя для metadata
        customer_phone: Телефон для metadata
        currency: Валюта (по умолчанию из настроек)

    Returns:
        dict с client_secret и payment_intent_id
    """
    if not settings.stripe_secret_key:
        raise StripePaymentError(
            "Stripe не настроен: отсутствует STRIPE_SECRET_KEY",
            code="stripe_not_configured"
        )

    currency = currency or settings.stripe_currency

    # Stripe принимает суммы в минимальных единицах валюты
    # Для RUB: 1 рубль = 100 копеек
    # Для USD: 1 доллар = 100 центов
    amount_in_minor_units = _to_minor_units(amount_rub, currency)

    try:
        intent = stripe.PaymentIntent.create(
            amount=amount_in_minor_units,
            currency=currency,
            # metadata сохраняется в Stripe и приходит обратно в webhook
            # Так мы связываем Stripe PaymentIntent с нашим заказом
            metadata={
                "order_id": str(order_id),
                "customer_name": customer_name,
                "customer_phone": customer_phone,
                "source": "flower-shop-landing",
            },
            # automatic_payment_methods включает все доступные методы оплаты
            # (карты, Apple Pay, Google Pay) без дополнительной настройки
            automatic_payment_methods={"enabled": True},
            # Описание появится в Stripe Dashboard
            description=f"Заказ #{order_id} — цветочный магазин",
        )

        logger.info(
            "PaymentIntent создан",
            extra={
                "payment_intent_id": intent.id,
                "order_id": order_id,
                "amount": amount_in_minor_units,
                "currency": currency,
            }
        )

        return {
            "client_secret": intent.client_secret,
            "payment_intent_id": intent.id,
            "amount": amount_in_minor_units,
            "currency": currency,
        }

    except stripe.error.CardError as e:
        # Карта отклонена — ошибка на стороне покупателя
        logger.warning(f"Карта отклонена для заказа {order_id}: {e.user_message}")
        raise StripePaymentError(e.user_message or "Карта отклонена", code="card_declined")

    except stripe.error.AuthenticationError:
        # Неверный API ключ
        logger.error("Ошибка аутентификации Stripe — проверьте STRIPE_SECRET_KEY")
        raise StripePaymentError("Ошибка конфигурации платёжного шлюза", code="auth_error")

    except stripe.error.RateLimitError:
        logger.warning("Stripe rate limit достигнут")
        raise StripePaymentError("Слишком много запросов, попробуйте позже", code="rate_limit")

    except StripeError as e:
        logger.error(f"Stripe ошибка для заказа {order_id}: {e}")
        raise StripePaymentError(str(e), code="stripe_error")


async def verify_webhook_event(payload: bytes, sig_header: str) -> stripe.Event:
    """
    Верифицирует подпись webhook от Stripe.

    КРИТИЧЕСКИ ВАЖНО: без верификации подписи любой может отправить
    поддельный webhook и пометить заказ как оплаченный.

    Args:
        payload: Сырое тело запроса (bytes, НЕ декодированное)
        sig_header: Значение заголовка Stripe-Signature

    Returns:
        Верифицированный объект Event

    Raises:
        StripePaymentError при неверной подписи
    """
    if not settings.stripe_webhook_secret:
        raise StripePaymentError(
            "STRIPE_WEBHOOK_SECRET не настроен",
            code="webhook_not_configured"
        )

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=settings.stripe_webhook_secret,
        )
        return event

    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Неверная подпись Stripe webhook: {e}")
        raise StripePaymentError("Неверная подпись webhook", code="invalid_signature")

    except ValueError as e:
        logger.error(f"Некорректный payload webhook: {e}")
        raise StripePaymentError("Некорректный payload", code="invalid_payload")


def parse_webhook_event(event: stripe.Event) -> dict:
    """
    Разбирает событие webhook и возвращает структурированные данные.

    Обрабатываемые события:
    - payment_intent.succeeded → статус paid
    - payment_intent.payment_failed → статус failed
    - payment_intent.canceled → статус cancelled
    - payment_intent.refunded → статус refunded

    Returns:
        dict с payment_intent_id, status, order_id из metadata
    """
    event_type = event["type"]
    payment_intent = event["data"]["object"]

    # Достаём order_id, который мы сохранили при создании intent
    order_id = payment_intent.get("metadata", {}).get("order_id")
    payment_intent_id = payment_intent.get("id")

    # Маппинг Stripe-событий → наши статусы
    status_map = {
        "payment_intent.succeeded": "paid",
        "payment_intent.payment_failed": "failed",
        "payment_intent.canceled": "cancelled",
    }

    our_status = status_map.get(event_type)

    logger.info(
        f"Webhook получен: {event_type}",
        extra={
            "payment_intent_id": payment_intent_id,
            "order_id": order_id,
            "our_status": our_status,
        }
    )

    return {
        "event_type": event_type,
        "payment_intent_id": payment_intent_id,
        "order_id": order_id,
        "our_status": our_status,
        "raw": json.dumps(dict(payment_intent), default=str)[:5000],  # Лимит для БД
    }


async def create_refund(payment_intent_id: str, amount_rub: Optional[float] = None) -> dict:
    """
    Создаёт возврат средств (частичный или полный).

    Args:
        payment_intent_id: ID PaymentIntent (pi_xxx)
        amount_rub: Сумма возврата в рублях. None = полный возврат.

    Returns:
        dict с ID возврата и статусом
    """
    try:
        refund_params = {"payment_intent": payment_intent_id}
        if amount_rub is not None:
            refund_params["amount"] = _to_minor_units(amount_rub, settings.stripe_currency)

        refund = stripe.Refund.create(**refund_params)

        logger.info(f"Возврат создан: {refund.id} для {payment_intent_id}")
        return {"refund_id": refund.id, "status": refund.status}

    except StripeError as e:
        logger.error(f"Ошибка создания возврата: {e}")
        raise StripePaymentError(str(e), code="refund_error")


def _to_minor_units(amount: float, currency: str) -> int:
    """
    Конвертирует сумму в минимальные единицы валюты.
    Stripe требует целое число (копейки, центы, etc.)

    Нулевые-decimal валюты (JPY, KRW) — не умножаем.
    """
    zero_decimal_currencies = {"jpy", "krw", "bif", "clp", "gnf", "mga", "pyg", "rwf", "ugx", "vnd", "xaf", "xof"}
    if currency.lower() in zero_decimal_currencies:
        return int(amount)
    return int(round(amount * 100))