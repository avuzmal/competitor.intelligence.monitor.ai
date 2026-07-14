from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    environment: str = "development"
    database_url: str = "sqlite+pysqlite:///./test.db"
    apify_api_token: str = ""
    anthropic_api_key: str = ""
    resend_api_key: str = ""
    from_email: str = "Competitor Radar <hello@competitor-radar.com>"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
