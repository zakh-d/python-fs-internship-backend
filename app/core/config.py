from typing import Any
from pydantic import (
    Field,
    computed_field,
)

from pydantic.fields import FieldInfo
from pydantic_core import MultiHostUrl
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
    POSRGRES_PORT: int = 5432
    POSTGRES_DB_HOST: str

    @computed_field
    @property
    def postgres_dsn(self) -> str:
        return str(MultiHostUrl.build(
            scheme='postgresql+asyncpg',
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_DB_HOST,
            port=self.POSRGRES_PORT,
            path=f'{self.POSTGRES_DB}',
        ))


settings = Settings()
