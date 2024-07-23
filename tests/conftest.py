import alembic
import pytest
from alembic.config import Config
from fastapi.testclient import TestClient
from typing import Generator

from app.main import app
from app.db.db import async_session
from app.repositories import UserRepository
from app.services.users_service import UserService


@pytest.fixture(autouse=True)
def apply_migrations() -> Generator[None, None, None]:
    config = Config('alembic.ini')
    alembic.command.upgrade(config, 'head')
    yield
    alembic.command.downgrade(config, 'base')


@pytest.fixture(scope='module')
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


@pytest.fixture
async def get_db():
    async with async_session() as session:
        yield session


@pytest.fixture
def user_repo(get_db):
    return UserRepository(get_db)


@pytest.fixture
def user_service(user_repo):
    return UserService(user_repo)
