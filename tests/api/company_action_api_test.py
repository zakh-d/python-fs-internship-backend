from fastapi.testclient import TestClient
import pytest

from app.db.models import CompanyActionType
from app.repositories.company_action_repository import CompanyActionRepository
from app.schemas.company_schema import CompanySchema, CompanyUpdateSchema
from app.schemas.user_shema import UserSchema
from app.services.authentication_service.service import AuthenticationService
from app.services.company_service.service import CompanyService


def test_cannot_invite_owner(
    company_and_users: tuple[CompanySchema, UserSchema, UserSchema],
    auth_service: AuthenticationService,
    client: TestClient
):
    company, owner, _ = company_and_users
    token = auth_service.generate_jwt_token(owner)
    response = client.post(f'/companies/{company.id}/invites/', json={
        'email': owner.email
    }, headers={
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

    response = client.post(f'/companies/{company.id}/invites/', json={
        'email': user.email
    }, headers={
        'Authorization': f'Bearer {token}'
    })

    assert response.status_code == 200

    response = client.post(f'/companies/{company.id}/invites/', json={
        'email': user.email
    }, headers={
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
    response = client.post(f'/companies/{company.id}/invites/', json={
        'email': user.email
    }, headers={
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

    membership = await company_action_repo.get_by_company_user_and_type(company.id, user.id, CompanyActionType.MEMBERSHIP)

    assert membership is not None


@pytest.mark.asyncio
async def test_admin_is_on_members_list(
    client: TestClient,
    company_and_users: tuple[CompanySchema, UserSchema, UserSchema],
    company_action_repo: CompanyActionRepository,
    auth_service: AuthenticationService
):
    company, owner, user = company_and_users
    company_action_repo.create(company.id, user.id, CompanyActionType.ADMIN)
    await company_action_repo.commit()

    response = client.get(f'/companies/{company.id}/members/', headers={
        'Authorization': f'Bearer {auth_service.generate_jwt_token(owner)}'
    })

    assert response.status_code == 200

    assert response.json()['total_count'] == 2
    
    members = response.json()['users']

    members_ids = [member['id'] for member in members]

    assert str(user.id) in members_ids
