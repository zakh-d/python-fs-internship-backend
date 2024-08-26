from fastapi.testclient import TestClient
import pytest

from app.db.models import CompanyActionType
from app.repositories.company_action_repository import CompanyActionRepository
from app.repositories.quizz_repository import QuizzRepository
from app.schemas.company_schema import CompanySchema
from app.schemas.quizz_schema import AnswerCreateSchema, QuestionCreateSchema, QuizzCreateSchema, QuizzSchema
from app.schemas.user_shema import UserSchema
from app.services.authentication_service.service import AuthenticationService
from app.services.quizz_service.service import QuizzService


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

    assert response.status_code == 404


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


@pytest.mark.asyncio
async def test_member_cannot_access_correct_answers(
    client: TestClient,
    company_and_users: tuple[CompanySchema, UserSchema, UserSchema],
    company_action_repo: CompanyActionRepository,
    auth_service: AuthenticationService,
    test_quizz: QuizzSchema,
):
    comapny, owner, user = company_and_users
    company_action_repo.create(comapny.id, user.id, CompanyActionType.MEMBERSHIP)
    await company_action_repo.commit()

    response = client.get(f'/quizzes/{test_quizz.id}/correct', headers={
        'Authorization': f'Bearer {auth_service.generate_jwt_token(user)}'
    })
    assert response.status_code == 404



def test_owner_can_access_correct_answers(
    client: TestClient,
    company_and_users: tuple[CompanySchema, UserSchema, UserSchema],
    auth_service: AuthenticationService,
    test_quizz: QuizzSchema,
):
    comapny, owner, user = company_and_users

    response = client.get(f'/quizzes/{test_quizz.id}/correct', headers={
        'Authorization': f'Bearer {auth_service.generate_jwt_token(owner)}'
    })
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_admin_can_access_correct_answers(
    client: TestClient,
    company_and_users: tuple[CompanySchema, UserSchema, UserSchema],
    company_action_repo: CompanyActionRepository,
    auth_service: AuthenticationService,
    test_quizz: QuizzSchema,
):
    comapny, owner, user = company_and_users
    company_action_repo.create(comapny.id, user.id, CompanyActionType.ADMIN)
    await company_action_repo.commit()

    response = client.get(f'/quizzes/{test_quizz.id}/correct', headers={
        'Authorization': f'Bearer {auth_service.generate_jwt_token(user)}'
    })
    assert response.status_code == 200


def test_does_not_expose_correct_answers(
    client: TestClient,
    company_and_users: tuple[CompanySchema, UserSchema, UserSchema],
    auth_service: AuthenticationService,
    test_quizz: QuizzSchema,
):
    response = client.get(f'/quizzes/{test_quizz.id}', headers={
        'Authorization': f'Bearer {auth_service.generate_jwt_token(company_and_users[1])}'
    })

    assert all('is_correct' not in answer for question in response.json()['questions'] for answer in question['answers'])


def test_cannot_delete_only_question(
    client: TestClient,
    company_and_users: tuple[CompanySchema, UserSchema, UserSchema],
    auth_service: AuthenticationService,
    test_quizz: QuizzSchema,
):
    response = client.delete(f'/quizzes/{test_quizz.id}/question/{test_quizz.questions[0].id}', headers={
        'Authorization': f'Bearer {auth_service.generate_jwt_token(company_and_users[1])}'
    })

    assert response.status_code == 400
    assert response.json()['detail'] == 'Cannot delete last question'


@pytest.mark.asyncio
async def test_cannot_delete_last_of_two_answers(
    client: TestClient,
    company_and_users: tuple[CompanySchema, UserSchema, UserSchema],
    auth_service: AuthenticationService,
    test_quizz: QuizzSchema,
    quizz_service: QuizzService
):
    question = test_quizz.questions[0]
    await quizz_service.delete_answer(question.answers[2].id, test_quizz.id)
    response = client.delete(f'/quizzes/{test_quizz.id}/answer/{question.answers[0].id}', headers={
        'Authorization': f'Bearer {auth_service.generate_jwt_token(company_and_users[1])}'
    })

    assert response.status_code == 400
    assert response.json()['detail'] == 'Question must have at least two answer'


def test_canot_delete_only_correct_option(
    client: TestClient,
    company_and_users: tuple[CompanySchema, UserSchema, UserSchema],
    auth_service: AuthenticationService,
    test_quizz: QuizzSchema,
):
    question = test_quizz.questions[0]
    response = client.delete(f'/quizzes/{test_quizz.id}/answer/{question.answers[1].id}', headers={
        'Authorization': f'Bearer {auth_service.generate_jwt_token(company_and_users[1])}'
    })

    assert response.status_code == 400
    assert response.json()['detail'] == 'Cannot delete only correct answer'

   
def test_cannot_update_only_correct_answer_to_false(
    client: TestClient,
    company_and_users: tuple[CompanySchema, UserSchema, UserSchema],
    auth_service: AuthenticationService,
    test_quizz: QuizzSchema, 
):
    question = test_quizz.questions[0]
    response = client.put(f'/quizzes/{test_quizz.id}/answer/{question.answers[1].id}', json={
        'text': 'new option',
        'is_correct': False
    }, headers={
        'Authorization': f'Bearer {auth_service.generate_jwt_token(company_and_users[1])}'
    })
    assert response.json()['detail'] == 'Question must have at least one correct answers'
