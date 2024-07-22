import uuid
import pytest
from fastapi.testclient import TestClient
from passlib.hash import argon2

from app.repositories import UserRepository


def test_get_user_list(client: TestClient, fake_authentication):
    response = client.get('/users/')
    assert response.status_code == 200
    data = response.json()
    assert "users" in data
    assert type(data["users"]) is list


def test_user_create_success(client: TestClient):
    user_dict = {
        "username": "drogo",
        "password": "stringst",
        "email": "drogo@khal.com",
        "first_name": "Khal",
        "last_name": "Drogo",
        "password_confirmation": "stringst"
    }
    response = client.post('/users/sign_up/', json=user_dict)
    assert response.status_code == 200

    data = response.json()
    assert "id" in data

    response = client.get('/users')
    assert response.status_code == 200
    data = response.json()
    assert len(data['users']) == 1


def test_user_create_passwords_min_length(client: TestClient):
    user_dict = {
        "username": "string",
        "password": "s",
        "email": "user@example.com",
        "first_name": "string",
        "last_name": "string",
        "password_confirmation": "s"
    }
    response = client.post('/users/sign_up/', json=user_dict)
    assert response.status_code == 422
    data = response.json()
    assert data["detail"][0]["msg"] == "String should have at least 8 characters"


def test_user_create_passwords_max_length(client: TestClient):
    long_password = "abc" * 1000

    user_dict = {
        "username": "string",
        "password": long_password,
        "email": "user@example.com",
        "first_name": "string",
        "last_name": "string",
        "password_confirmation": long_password
    }

    response = client.post('/users/sign_up/', json=user_dict)
    assert response.status_code == 422


def test_user_create_passwords_must_match(client: TestClient):

    user_dict = {
        "username": "jamie",
        "password": 'password_1',
        "email": "user@example.com",
        "first_name": "Jamie",
        "last_name": "Lannister",
        "password_confirmation": 'password_2'
    }

    response = client.post('/users/sign_up/', json=user_dict)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_user_create_email_already_exists(
        client: TestClient,
        user_repo: UserRepository
):
    user_dict = {
        "username": "lord_commander",
        "email": "john@starks.com",
        "first_name": "John",
        "last_name": "Snow",
    }

    user = user_repo.create_user_with_hashed_password(
        **user_dict,
        hashed_password='hashed_password'
    )

    await user_repo.commit_me(user)

    user_dict.update({
        "username": 'john_snow',
        "password_confirmation": "stringst",
        "password": "stringst"
    })
    response = client.post('/users/sign_up/', json=user_dict)
    assert response.status_code == 400
    assert response.json() == {'detail': "User with email: 'john@starks.com' already exists!"}


def test_user_create_email_invalid(client: TestClient):
    user_dict = {
        "username": "lord_commander",
        "password": "stringst",
        "email": "john.com",
        "first_name": "John",
        "last_name": "Snow",
        "password_confirmation": "stringst"
    }
    response = client.post('/users/sign_up/', json=user_dict)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_user_update(
        client: TestClient,
        user_repo: UserRepository,
        fake_authentication
):
    user = user_repo.create_user_with_hashed_password(
        username='john_snow',
        first_name='John',
        last_name='Snow',
        email='lord_commander@north.wall',
        hashed_password=argon2.hash('password123')
    )

    await user_repo.commit_me(user)

    response = client.put(f'/users/{user.id}', json={
        'first_name': 'Johny',
        'password': 'password123'
    })
    assert response.status_code == 200

    data = response.json()
    assert data['first_name'] == 'Johny'


@pytest.mark.asyncio
async def test_user_update_invalid_password(
        client: TestClient,
        user_repo: UserRepository,
        fake_authentication
):
    user = user_repo.create_user_with_hashed_password(
        username='john_snow',
        first_name='John',
        last_name='Snow',
        email='lord_commander@north.wall',
        hashed_password=argon2.hash('password123')
    )
    await user_repo.commit_me(user)

    response = client.put(f'/users/{user.id}', json={
        'first_name': 'Johny',
        'password': 'password1234'
    })

    assert response.status_code == 401


def test_user_update_user_not_found(client: TestClient, fake_authentication):
    response = client.put(f'/users/{uuid.uuid4()}', json={
        'first_name': 'Johny',
        'password': 'password123'
    })
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_user_update_user_with_email_already_exists(
        client: TestClient,
        user_repo: UserRepository,
        fake_authentication
):
    john_snow = user_repo.create_user_with_hashed_password(
        username='john_snow',
        first_name='John',
        last_name='Snow',
        email='test@mail.com',
        hashed_password=argon2.hash('password123')
    )

    daenerys = user_repo.create_user_with_hashed_password(
        username='daenerys',
        first_name='Daenerys',
        last_name='Targaryen',
        email='mother.of@dragons',
        hashed_password=argon2.hash('password123')
    )

    await user_repo.commit_me(john_snow)
    await user_repo.commit_me(daenerys)

    response = client.put(f'/users/{daenerys.id}', json={
        'email': 'test@mail.com',
        'password': 'password123'
    })

    assert response.status_code == 400
    assert response.json() == {'detail': "User with email: 'test@mail.com' already exists!"}


def test_update_very_long_password_rejects(
        client: TestClient,
        fake_authentication
):
    very_long_password = 'abc' * 1000
    response = client.put(f'/users/{uuid.uuid4}/', json={
        'first_name': 'Robert',
        'password': very_long_password
    })

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_user_delete(
        client: TestClient,
        user_repo: UserRepository,
        fake_authentication
):
    daenerys = user_repo.create_user_with_hashed_password(
        username='daenerys',
        first_name='Daenerys',
        last_name='Targaryen',
        email='mother.of@dragons',
        hashed_password=argon2.hash('password123')
    )
    await user_repo.commit_me(daenerys)

    response = client.delete(f'/users/{daenerys.id}')
    assert response.status_code == 200

    users = await user_repo.get_all_users()
    assert len(users) == 0


def test_user_delete_user_not_found(client: TestClient, fake_authentication):
    response = client.delete(f'/users/{uuid.uuid4()}')
    assert response.status_code == 404
    assert 'not found' in response.json()['detail']
