from fastapi.testclient import TestClient
import pytest

from app.db.models import CompanyActionType
from app.repositories.company_action_repository import CompanyActionRepository
from app.schemas.company_schema import CompanySchema
from app.schemas.user_shema import UserSchema
from app.services.authentication_service.service import AuthenticationService


def test_quizz_creation_require_at_least_one_question(
    client: TestClient,
    company_and_users: tuple[CompanySchema, UserSchema, UserSchema],
    auth_service: AuthenticationService
):
    company, owner, _ = company_and_users
    quizz_json = {
        'title': 'Test quizz',
        'description': 'Test description',
        'frequency': 1,
        'company_id': str(company.id),
        'questions': []
    }

    token = auth_service.generate_jwt_token(owner)

    response = client.post(f'/quizzes/', json=quizz_json, headers={
        'Authorization': f'Bearer {token}'
    })

    assert response.status_code == 422
    response_body = response.json()
    assert any('quizz must have at least one question' in item['msg'] for item in response_body['detail'])


def test_quizz_question_requires_min_2_answers(
    client: TestClient,
    company_and_users: tuple[CompanySchema, UserSchema, UserSchema],
    auth_service: AuthenticationService 
):
    company, owner, _ = company_and_users
    quizz_json = {
        'title': 'Test quizz',
        'description': 'Test description',
        'frequency': 1,
        'company_id': str(company.id),
        'questions': [
            {
                'text': 'Test question',
                'answers': [
                    {
                        'text': 'Test answer',
                        'is_correct': True
                    }
                ]
            }
        ]
    }

    token = auth_service.generate_jwt_token(owner)

    response = client.post(f'/quizzes/', json=quizz_json, headers={
        'Authorization': f'Bearer {token}'
    })

    assert response.status_code == 422
    response_body = response.json()
    assert any('question must have at min 2' in item['msg'] for item in response_body['detail'])


def test_quizz_question_requires_max_4_answers(
    client: TestClient,
    company_and_users: tuple[CompanySchema, UserSchema, UserSchema],
    auth_service: AuthenticationService 
):
    company, owner, _ = company_and_users
    quizz_json = {
        'title': 'Test quizz',
        'description': 'Test description',
        'frequency': 1,
        'company_id': str(company.id),
        'questions': [
            {
                'text': 'Test question',
                'answers': [
                    {
                        'text': 'option 1',
                        'is_correct': True
                    },
                    {
                        'text': 'option 2',
                        'is_correct': False
                    },{
                        'text': 'option 3',
                        'is_correct': False
                    },{
                        'text': 'option 4',
                        'is_correct': False
                    },{
                        'text': 'option 5',
                        'is_correct': True
                    }
                ]
            }
        ]
    }

    token = auth_service.generate_jwt_token(owner)

    response = client.post(f'/quizzes/', json=quizz_json, headers={
        'Authorization': f'Bearer {token}'
    })

    assert response.status_code == 422
    response_body = response.json()
    assert any('question must have at min 2' in item['msg'] for item in response_body['detail'])


def test_quizz_question_must_have_at_least_one_correct_option(
    client: TestClient,
    company_and_users: tuple[CompanySchema, UserSchema, UserSchema],
    auth_service: AuthenticationService 
):
    company, owner, _ = company_and_users

    quizz_json = {
        'title': 'Test quizz',
        'description': 'Test description',
        'frequency': 1,
        'company_id': str(company.id),
        'questions': [
            {
                'text': 'Test question',
                'answers': [
                    {
                        'text': 'option 1',
                        'is_correct': False
                    },
                    {
                        'text': 'option 4',
                        'is_correct': False
                    }
                ]
            }
        ]
    }

    token = auth_service.generate_jwt_token(owner)

    response = client.post(f'/quizzes/', json=quizz_json, headers={
        'Authorization': f'Bearer {token}'
    })

    assert response.status_code == 422
    response_body = response.json()
    assert any('question must have at least one correct answer' in item['msg'] for item in response_body['detail'])


@pytest.mark.asyncio
async def test_member_cannot_create_quizz(
    client: TestClient,
    company_and_users: tuple[CompanySchema, UserSchema, UserSchema],
    auth_service: AuthenticationService,
    company_action_repo: CompanyActionRepository
):
    company, owner, user = company_and_users
    quizz_json = {
        'title': 'Test quizz',
        'description': 'Test description',
        'frequency': 1,
        'company_id': str(company.id),
        'questions': [
            {
                'text': 'Test question',
                'answers': [
                    {
                        'text': 'option 1',
                        'is_correct': False
                    },
                    {
                        'text': 'option 2',
                        'is_correct': True
                    }
                ]
            }
        ]
    }

    company_action_repo.create(company.id, user.id, CompanyActionType.MEMBERSHIP)
    await company_action_repo.commit()
    token = auth_service.generate_jwt_token(user)


    response = client.post(f'/quizzes/', json=quizz_json, headers={
        'Authorization': f'Bearer {token}'
    })

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_create_quizz(
    client: TestClient,
    company_and_users: tuple[CompanySchema, UserSchema, UserSchema],
    auth_service: AuthenticationService,
    company_action_repo: CompanyActionRepository
):
    company, owner, user = company_and_users
    quizz_json = {
        'title': 'Test quizz',
        'description': 'Test description',
        'company_id': str(company.id),
        'frequency': 1,
        'questions': [
            {
                'text': 'Test question',
                'answers': [
                    {
                        'text': 'option 1',
                        'is_correct': False
                    },
                    {
                        'text': 'option 2',
                        'is_correct': True
                    }
                ]
            }
        ]
    }

    company_action_repo.create(company.id, user.id, CompanyActionType.ADMIN)
    await company_action_repo.commit()
    token = auth_service.generate_jwt_token(user)


    response = client.post(f'/quizzes/', json=quizz_json, headers={
        'Authorization': f'Bearer {token}'
    })

    assert response.status_code == 200


def test_admin_can_create_quizz(
    client: TestClient,
    company_and_users: tuple[CompanySchema, UserSchema, UserSchema],
    auth_service: AuthenticationService,
):
    company, owner, _ = company_and_users
    quizz_json = {
        'title': 'Test quizz',
        'company_id': str(company.id),
        'description': 'Test description',
        'frequency': 1,
        'questions': [
            {
                'text': 'Test question',
                'answers': [
                    {
                        'text': 'option 1',
                        'is_correct': False
                    },
                    {
                        'text': 'option 2',
                        'is_correct': True
                    }
                ]
            }
        ]
    }

    token = auth_service.generate_jwt_token(owner)


    response = client.post(f'/quizzes/', json=quizz_json, headers={
        'Authorization': f'Bearer {token}'
    })

    assert response.status_code == 200
