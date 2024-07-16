import alembic
import pytest
from alembic.config import Config
from fastapi.testclient import TestClient
from typing import Generator

from app.main import app


@pytest.fixture(scope='session')
def apply_migrations() -> Generator[None, None, None]:
    config = Config('alembic.ini')
    alembic.command.upgrade(config, 'head')
    yield
    alembic.command.downgrade(config, 'base')


@pytest.fixture(scope='module')
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c
