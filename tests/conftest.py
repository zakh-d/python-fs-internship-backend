import alembic
import pytest
from alembic.config import Config
from fastapi.testclient import TestClient
from typing import Generator

from app.core.security import get_current_user
from app.main import app
from app.db.db import async_session
from app.repositories import UserRepository
from app.repositories.company_action_repository import CompanyActionRepository
from app.repositories.company_repository import CompanyRepository
from app.schemas.user_shema import UserSchema
from app.services.authentication_service.service import AuthenticationService
from app.services.company_service.service import CompanyService
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
    return UserService(user_repo, None)


@pytest.fixture
def fake_authentication():
    app.dependency_overrides[get_current_user] = lambda: 1
    yield
    del app.dependency_overrides[get_current_user]


@pytest.fixture
async def test_user(user_repo: UserRepository) -> UserSchema:
    user = user_repo.create_user_with_hashed_password(
        username='test_user',
        first_name='TEST',
        last_name='USER',
        email='test_user@example.com',
        hashed_password='fake-hash-password123'
    )
    await user_repo.commit_me(user)
    return UserSchema.model_validate(user)


@pytest.fixture
def auth_service(user_repo: UserRepository) -> AuthenticationService:
    return AuthenticationService(user_repo)


@pytest.fixture
async def access_token(
    test_user: UserSchema,
    auth_service: AuthenticationService
) -> str:
    return auth_service.generate_jwt_token(UserSchema.model_validate(test_user))


@pytest.fixture
def company_repo(get_db) -> CompanyRepository:
    return CompanyRepository(get_db)


@pytest.fixture
def company_action_repo(get_db) -> CompanyActionRepository:
    return CompanyActionRepository(get_db)


@pytest.fixture
def company_service(company_repo, company_action_repo) -> CompanyService:
    return CompanyService(company_repository=company_repo, company_action_repository=company_action_repo)
