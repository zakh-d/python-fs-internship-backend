from typing import Any, Literal
from pydantic import Field

from pydantic.fields import FieldInfo
from pydantic_settings import BaseSettings, EnvSettingsSource


class CustomSettingsSource(EnvSettingsSource):

    def prepare_field_value(self, field_name: str, field: FieldInfo, value: Any, value_is_complex: bool) -> Any:
        if field_name == 'ALLOWED_HOSTS':
            return value.strip().split(',')
        return super().prepare_field_value(field_name, field, value, value_is_complex)


class Settings(BaseSettings):

    ALLOWED_HOSTS: list[str] = Field(default_factory=list)

    @classmethod
    def settings_customise_sources(
        cls, settings_cls, init_settings, env_settings, dotenv_settings, file_secret_settings
    ):
        return (
            init_settings,
            CustomSettingsSource(settings_cls),
            dotenv_settings,
            file_secret_settings,
        )

    POSTGRES_PASSWORD: str
    POSTGRES_USER: str
    POSTGRES_DB: str
    POSTGRES_PORT: int = 5432
    POSTGRES_DB_HOST: str

    @property
    def postgres_dsn(self) -> str:
        return f'postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_DB_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}'

    REDIS_HOST: str
    REDIS_PORT: int = 6379

    @property
    def redis_url(self) -> str:
        return f'redis://{self.REDIS_HOST}:{self.REDIS_PORT}'

    ENVIRONMENT: Literal["local", "staging", "production"] = "local"


settings = Settings()
