from fastapi.testclient import TestClient
import pytest

from app.db.models import CompanyActionType
from app.repositories.company_action_repository import CompanyActionRepository
from app.repositories.company_repository import CompanyRepository
from app.repositories.user_repository import UserRepository
from app.schemas.company_schema import CompanyCreateSchema, CompanySchema, CompanyUpdateSchema
from app.schemas.user_shema import UserSchema, UserSignUpSchema
from app.services.authentication_service.service import AuthenticationService
from app.services.company_service.service import CompanyService
from app.services.users_service.service import UserService


@pytest.fixture
async def company_and_users(
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


def test_cannot_invite_owner(
    company_and_users: tuple[CompanySchema, UserSchema, UserSchema],
    auth_service: AuthenticationService,
    client: TestClient
):
    company, owner, _ = company_and_users
    token = auth_service.generate_jwt_token(owner)
    response = client.post(f'/companies/{company.id}/invites/{owner.id}', json={}, headers={
        'Authorization': f'Bearer {token}'
    })
    assert response.status_code == 400


def test_cannot_invite_invited_user(
    company_and_users: tuple[CompanySchema, UserSchema, UserSchema],
    auth_service: AuthenticationService,
    client: TestClient
):
    company, owner, user = company_and_users
    token = auth_service.generate_jwt_token(owner)

    response = client.post(f'/companies/{company.id}/invites/{user.id}', json={}, headers={
        'Authorization': f'Bearer {token}'
    })

    assert response.status_code == 200

    response = client.post(f'/companies/{company.id}/invites/{user.id}', json={}, headers={
        'Authorization': f'Bearer {token}'
    })

    assert response.status_code == 400


def test_cannot_delete_owner_from_members(
    company_and_users: tuple[CompanySchema, UserSchema, UserSchema],
    auth_service: AuthenticationService,
    client: TestClient
):
    company, owner, _ = company_and_users
    token = auth_service.generate_jwt_token(owner)
    response = client.delete(f'/companies/{company.id}/members/{owner.id}', headers={
        'Authorization': f'Bearer {token}'
    })
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_cannot_request_to_hiden_company(
    company_and_users: tuple[CompanySchema, UserSchema, UserSchema],
    auth_service: AuthenticationService,
    client: TestClient,
    company_service: CompanyService
):
    company, owner, user = company_and_users
    await company_service.update_company(company_id=company.id, company_data=CompanyUpdateSchema(hidden=True), current_user=owner)

    response = client.post(f'/users/{user.id}/requests/{company.id}', headers={
        'Authorization': f'Bearer {auth_service.generate_jwt_token(user)}'
    })

    assert response.status_code == 404


def test_owner_added_to_members(
        client: TestClient,
        company_and_users: tuple[CompanySchema, UserSchema, UserSchema],
        auth_service: AuthenticationService
):
    company, owner, _ = company_and_users

    response = client.get(f'/companies/{company.id}/members/', headers={'Authorization': f'Bearer {auth_service.generate_jwt_token(owner)}'})
    assert response.status_code == 200

    assert response.json()['total_count'] == 1
    assert response.json()['users'][0]['id'] == str(owner.id)


def test_owner_can_invite_user(
    client: TestClient,
    company_and_users: tuple[CompanySchema, UserSchema, UserSchema],
    auth_service: AuthenticationService
):
    company, owner, user = company_and_users
    response = client.post(f'/companies/{company.id}/invites/{user.id}', json={}, headers={
        'Authorization': f'Bearer {auth_service.generate_jwt_token(owner)}'
    })

    assert response.status_code == 200

    response = client.get(f'/companies/{company.id}/invites/', headers={
        'Authorization': f'Bearer {auth_service.generate_jwt_token(owner)}'
    })

    assert response.status_code == 200
    assert response.json()['total_count'] == 1
    assert response.json()['users'][0]['id'] == str(user.id)


@pytest.mark.asyncio
async def test_assigning_member_as_admin(
    client: TestClient,
    company_and_users: tuple[CompanySchema, UserSchema, UserSchema],
    company_action_repo: CompanyActionRepository,
    auth_service: AuthenticationService
):
    company, owner, user = company_and_users
    company_action_repo.create(company.id, user.id, CompanyActionType.MEMBERSHIP)
    await company_action_repo.commit()

    response = client.post(f'/companies/{company.id}/admins/', json={
        'user_id': str(user.id)
    }, headers={
        'Authorization': f'Bearer {auth_service.generate_jwt_token(owner)}'})

    assert response.status_code == 200


def test_cannot_assign_owner_as_admin(
    client: TestClient,
    company_and_users: tuple[CompanySchema, UserSchema, UserSchema],
    auth_service: AuthenticationService
):
    company, owner, _ = company_and_users
    response = client.post(f'/companies/{company.id}/admins/', json={
        'user_id': str(owner.id)
    }, headers={
        'Authorization': f'Bearer {auth_service.generate_jwt_token(owner)}'})

    assert response.status_code == 400


def test_cannot_assign_not_member_as_admin(
    client: TestClient,
    company_and_users: tuple[CompanySchema, UserSchema, UserSchema],
    auth_service: AuthenticationService
):
    company, owner, user = company_and_users
    response = client.post(f'/companies/{company.id}/admins/', json={
        'user_id': str(user.id)
    }, headers={
        'Authorization': f'Bearer {auth_service.generate_jwt_token(owner)}'})

    assert response.status_code == 404
    assert response.json()['detail'] == 'User is not a member of this company'


@pytest.mark.asyncio
async def test_removing_from_admins_downgrades_to_member(
    client: TestClient,
    company_and_users: tuple[CompanySchema, UserSchema, UserSchema],
    company_action_repo: CompanyActionRepository,
    auth_service: AuthenticationService
):
    company, owner, user = company_and_users
    company_action_repo.create(company.id, user.id, CompanyActionType.ADMIN)
    await company_action_repo.commit()

    response = client.delete(f'/companies/{company.id}/admins/{user.id}', headers={
        'Authorization': f'Bearer {auth_service.generate_jwt_token(owner)}'
    })

    assert response.status_code == 200

    membership = await company_action_repo.get_company_action_by_company_and_user(company.id, user.id, CompanyActionType.MEMBERSHIP)

    assert membership is not None
