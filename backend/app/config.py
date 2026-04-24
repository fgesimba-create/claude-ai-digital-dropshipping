from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Anthropic
    anthropic_api_key: str

    # Database
    database_url: str = "postgresql+asyncpg://dropship:dropship_pass@db:5432/dropship_db"
    redis_url: str = "redis://redis:6379/0"

    # CJDropshipping supplier
    cj_api_key: str = ""
    cj_access_token: str = ""

    # Stripe
    stripe_secret_key: str = ""
    stripe_publishable_key: str = ""
    stripe_webhook_secret: str = ""

    # Store
    store_name: str = "TechFlow"
    store_domain: str = "http://localhost:3000"
    store_currency: str = "USD"
    store_email: str = "support@techflow.store"

    # Pricing
    min_profit_multiplier: float = 2.2
    target_profit_multiplier: float = 2.8
    max_product_price: float = 299.00

    # Automation intervals (hours)
    product_discovery_interval_hours: int = 24
    price_update_interval_hours: int = 6
    inventory_sync_interval_hours: int = 2
    security_scan_interval_hours: int = 12
    analytics_report_interval_hours: int = 24

    # Security
    secret_key: str = "change_me_to_64_char_random_string"
    admin_email: str = "admin@techflow.store"
    admin_password: str = "change_me"

    # Notifications
    slack_webhook_url: str = ""
    sendgrid_api_key: str = ""

    # Environment
    environment: str = "production"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
