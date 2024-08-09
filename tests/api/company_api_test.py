import uuid
from fastapi.testclient import TestClient
import pytest

from app.repositories.company_repository import CompanyRepository
from app.repositories.user_repository import UserRepository
from app.schemas.company_schema import CompanyCreateSchema
from app.schemas.user_shema import UserSchema


@pytest.mark.asyncio
async def test_get_list_endpoint(
    client: TestClient,
    access_token: str,
):
    response = client.get(
        '/companies/',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    assert response.status_code == 200

    assert 'total_count' in response.json()
    assert 'companies' in response.json()


@pytest.mark.asyncio
async def test_get_company_by_id_endpoint(
    client: TestClient,
    access_token: str,
    test_user: UserSchema,
    company_repo: CompanyRepository,
):
    company = company_repo.create_company(CompanyCreateSchema(
        name='Test Company',
        description='Test Company Description',
        hidden=False
    ), test_user.id)
    await company_repo.commit()

    response = client.get('/companies/' + str(company.id), headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 200
    assert response.json()['name'] == str(company.name)
    assert response.json()['id'] == str(company.id)


def test_get_company_by_id_endpoint_with_invalid_id(
    client: TestClient,
    access_token: str,
):
    response = client.get(f'/companies/{uuid.uuid4()}', headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_company_endpoint(
    client: TestClient,
    access_token: str,
    company_repo: CompanyRepository,
):
    response = client.post('/companies/', json={
        'name': 'Test Company',
        'description': 'Test Company Description',
        'hidden': False
    }, headers={'Authorization': f'Bearer {access_token}'})

    assert response.status_code == 200

    assert response.json()['owner']['email'] == 'test_user@example.com'

    company_count = await company_repo.get_companies_count()
    assert company_count == 1


@pytest.mark.asyncio
async def test_update_company_endpoint(
    client: TestClient,
    access_token: str,
    test_user: UserSchema,
    company_repo: CompanyRepository
):
    company = company_repo.create_company(CompanyCreateSchema(
        name='Test',
        description='Test',
        hidden=False
    ), test_user.id)
    await company_repo.commit()

    response = client.put(f'/companies/{company.id}', json={
        'name': 'Test1'
    }, headers={
        'Authorization': f'Bearer {access_token}'
    })

    assert response.status_code == 200
    await company_repo.db.refresh(company)
    assert company.name == 'Test1'


@pytest.mark.asyncio
async def test_not_owner_cannot_edit_company(
    user_repo: UserRepository,
    company_repo: CompanyRepository,
    access_token: str,
    client: TestClient
):
    user = user_repo.create_user_with_hashed_password(
        username='test',
        first_name='test',
        last_name='test',
        email='testfjsd@example.com',
        hashed_password='fake-hash-555'
    )
    await user_repo.commit_me(user)

    company = company_repo.create_company(
        CompanyCreateSchema(
            name='Company1',
            description='Test',
            hidden=False
        ),
        user.id
    )
    await company_repo.commit()

    response = client.put(f'/companies/{company.id}', json={
        'name': 'Company2'
    }, headers={
        'Authorization': f'Bearer {access_token}'
    })

    assert response.status_code == 403

    await company_repo.db.refresh(company)
    assert company.name == 'Company1'


@pytest.mark.asyncio
async def test_delete_company(
    client: TestClient,
    company_repo: CompanyRepository,
    test_user: UserSchema,
    access_token: str
):
    company = company_repo.create_company(
        CompanyCreateSchema(
            name='Company1',
            description='Test',
            hidden=False
        ),
        test_user.id
    )
    await company_repo.commit()
    company_count = await company_repo.get_companies_count()
    assert company_count == 1

    response = client.delete(f'/companies/{company.id}', headers={
        'Authorization': f'Bearer {access_token}'
    })

    assert response.status_code == 200
    company_count = await company_repo.get_companies_count()
    assert company_count == 0


@pytest.mark.asyncio
async def test_not_owner_cannot_delete_company(
    user_repo: UserRepository,
    company_repo: CompanyRepository,
    access_token: str,
    client: TestClient
):
    user = user_repo.create_user_with_hashed_password(
        username='test',
        first_name='test',
        last_name='test',
        email='testfjsd@example.com',
        hashed_password='fake-hash-555'
    )
    await user_repo.commit_me(user)

    company = company_repo.create_company(
        CompanyCreateSchema(
            name='Company1',
            description='Test',
            hidden=False
        ),
        user.id
    )
    await company_repo.commit()

    company_count = await company_repo.get_companies_count()
    assert company_count == 1

    response = client.delete(f'/companies/{company.id}', headers={
        'Authorization': f'Bearer {access_token}'
    })

    assert response.status_code == 403

    company_count = await company_repo.get_companies_count()
    assert company_count == 1
