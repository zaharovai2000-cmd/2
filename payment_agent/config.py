"""
Централизованная конфигурация приложения через Pydantic Settings.
Все переменные окружения читаются здесь — не разбросаны по файлам.
"""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional


class Settings(BaseSettings):
    # Приложение
    app_env: str = "development"
    allowed_origins: str = "http://localhost:3000"
    secret_key: str = "change-me-in-production"

    # База данных
    database_url: str = "sqlite+aiosqlite:///./flowers.db"

    # Stripe
    stripe_secret_key: str = ""
    stripe_publishable_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_currency: str = "rub"

    # ЮКасса
    yokassa_enabled: bool = False
    yokassa_shop_id: Optional[str] = None
    yokassa_secret_key: Optional[str] = None
    yokassa_return_url: str = "http://localhost:3000/payment/success"

    # Уведомления
    sms_api_key: Optional[str] = None
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None

    @field_validator("stripe_secret_key")
    @classmethod
    def validate_stripe_key(cls, v: str) -> str:
        if v and not v.startswith(("sk_test_", "sk_live_", "")):
            raise ValueError("Stripe secret key must start with sk_test_ or sk_live_")
        return v

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @property
    def allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Синглтон настроек — импортируем везде
settings = Settings()