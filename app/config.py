from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    DB_URL: str

    ADMIN_EMAIL: str
    SECRET_KEY: str
    ALGORITHM: str

    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USERNAME: str
    SMTP_PASSWORD: str

    model_config = SettingsConfigDict(env_file="../.env")


settings = Settings()
