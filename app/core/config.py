from functools import lru_cache # Imports a decorator that remembers a function's returned value.

from pydantic_settings import BaseSettings, SettingsConfigDict

from pydantic import Field, SecretStr

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="LEAPSCOPE_",
        extra="ignore",
    )

    app_name: str = "LeapScope API"
    environment: str = "development"
    debug: bool = False
    database_url: str
    jwt_secret_key: SecretStr = Field(min_length=32)
    access_token_expire_minutes: int = Field(default=30, gt=0)
    
@lru_cache
def get_settings() -> Settings:
    return Settings()




















