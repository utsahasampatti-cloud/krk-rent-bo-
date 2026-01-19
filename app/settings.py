from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str
    REDIS_URL: str

    OLX_REQUEST_DELAY_SEC: float = 1.5
    OLX_MAX_PAGES: int = 2

settings = Settings()
