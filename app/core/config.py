from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    environment: str = "development"
    database_url: str = "sqlite+pysqlite:///./test.db"
    apify_api_token: str = ""
    anthropic_api_key: str = ""
    resend_api_key: str = ""
    from_email: str = "Competitor Radar <hello@competitor-radar.com>"
    webhook_secret: str = "super-secret-default-key-change-me"
    log_level: str = "INFO"
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_price_id: str = ""
    jwt_secret_key: str = "super-secret-jwt-key"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60 * 24 * 7 # 7 days

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
