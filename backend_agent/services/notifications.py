"""
Сервис уведомлений.
Сейчас — заглушка с логированием в консоль.
Для подключения реального SMS/email-провайдера:
  1. Установите нужный SDK (twilio, sendgrid и т.д.)
  2. Замените тело функций — интерфейс менять не нужно.
"""
import logging
from dataclasses import dataclass
from datetime import date

logger = logging.getLogger("notifications")


@dataclass
class OrderNotificationData:
    """Данные для уведомления — отделены от ORM-модели."""
    order_id: int
    name: str
    phone: str
    address: str
    delivery_date: date
    delivery_time: str
    product_name: str
    quantity: int
    total_price: float
    payment_method: str
    wishes: str | None = None


async def send_order_confirmation(data: OrderNotificationData) -> bool:
    """
    Отправляет подтверждение заказа клиенту.
    
    Returns:
        True если уведомление отправлено успешно, False при ошибке.
    """
    # ── Форматируем сообщение ────────────────────────────────────────────────
    payment_label = (
        "Онлайн-оплата картой" if data.payment_method == "card_online"
        else "Оплата наличными курьеру"
    )
    wishes_line = f"\nПожелания: {data.wishes}" if data.wishes else ""

    message = (
        f"✅ Заказ #{data.order_id} подтверждён!\n"
        f"Букет: {data.product_name} × {data.quantity} шт.\n"
        f"Сумма: {data.total_price:,.0f} ₽\n"
        f"Доставка: {data.delivery_date.strftime('%d.%m.%Y')} в {data.delivery_time}\n"
        f"Адрес: {data.address}\n"
        f"Оплата: {payment_label}"
        f"{wishes_line}\n"
        f"Связь с магазином: +7 (999) 123-45-67"
    )

    # ── Логируем (заглушка вместо реальной отправки) ─────────────────────────
    logger.info(
        "📱 [SMS STUB] → %s\n%s",
        data.phone,
        message
    )

    # ── Здесь будет реальная отправка SMS ────────────────────────────────────
    # Пример для Twilio:
    # from twilio.rest import Client
    # client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    # client.messages.create(
    #     body=message,
    #     from_=settings.TWILIO_PHONE,
    #     to=data.phone
    # )

    # Пример для SMSC.ru:
    # await smsc_client.send(data.phone, message)

    return True


async def send_order_to_manager(data: OrderNotificationData) -> bool:
    """
    Уведомляет менеджера магазина о новом заказе.
    В продакшне: Telegram Bot API или email.
    """
    manager_message = (
        f"🌸 НОВЫЙ ЗАКАЗ #{data.order_id}\n"
        f"Клиент: {data.name}, {data.phone}\n"
        f"Букет: {data.product_name} × {data.quantity}\n"
        f"Сумма: {data.total_price:,.0f} ₽\n"
        f"Доставка: {data.delivery_date.strftime('%d.%m.%Y')} в {data.delivery_time}\n"
        f"Адрес: {data.address}\n"
        f"Оплата: {data.payment_method}"
    )

    logger.info(
        "📬 [MANAGER NOTIFY STUB]\n%s",
        manager_message
    )

    # Пример для Telegram:
    # await bot.send_message(chat_id=MANAGER_CHAT_ID, text=manager_message)

    return True