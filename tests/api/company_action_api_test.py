from fastapi.testclient import TestClient
import pytest

from app.repositories.company_repository import CompanyRepository
from app.repositories.user_repository import UserRepository
from app.schemas.company_schema import CompanyCreateSchema, CompanySchema
from app.schemas.user_shema import UserSchema, UserSignUpSchema
from app.services.authentication_service.service import AuthenticationService
from app.services.company_service.service import CompanyService
from app.services.users_service.service import UserService


@pytest.fixture
async def comany_and_users(
    user_service: UserService,
    company_service: CompanyService,
    test_user: UserSchema
) -> tuple[CompanySchema, UserSchema, UserSchema]:
    owner = await user_service.create_user(
        UserSignUpSchema(
            username='owner',
            first_name='OWNER',
            last_name='OWNER',
            email='owner@example.com',
            password='testpass123',
            password_confirmation='testpass123'
        )
    )

    company = await company_service.create_company(CompanyCreateSchema(
        name='TEST',
        description='TEST',
        hidden=False
    ), owner)

    return company, owner, test_user



@pytest.mark.asyncio
async def test_cannot_invite_owner(
    comany_and_users: tuple[CompanySchema, UserSchema, UserSchema],
    auth_service: AuthenticationService,
    client: TestClient
):
    company, owner, _ = comany_and_users
    token = auth_service.generate_jwt_token(owner)
    response = client.post(f'/companies/{company.id}/invites/{owner.id}', json={}, headers={
        'Authorization': f'Bearer {token}'
    })
    assert response.status_code == 400
