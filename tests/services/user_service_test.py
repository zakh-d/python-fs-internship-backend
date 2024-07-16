import uuid
import pytest
from passlib.hash import argon2
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import UserRepository
from app.schemas.user_shema import UserSignUpSchema, UserUpdateSchema
from app.services.users_service import UserService
from app.services.users_service.exceptions import (
    UserAlreadyExistsException, UserNotFoundException, InvalidPasswordException
)


@pytest.mark.asyncio
async def test_get_all_users(
    user_repo: UserRepository,
    get_db: AsyncSession,
):
    john_snow = user_repo.create_user_with_hashed_password(
        username='john_snow',
        first_name='John',
        last_name='Snow',
        email='lord_commander@north.wall',
        hashed_password='password123'
    )

    daenerys = user_repo.create_user_with_hashed_password(
        username='daenerys',
        first_name='Daenerys',
        last_name='Targaryen',
        email='mother.of@dragons.com',
        hashed_password='password123'
    )

    await user_repo.commit_me(john_snow)
    await user_repo.commit_me(daenerys)

    users = await UserService.get_all_users(get_db)
    assert len(users.users) == 2


@pytest.mark.asyncio
async def test_create_user(
    user_repo: UserRepository,
    get_db: AsyncSession,
):
    john_snow = UserSignUpSchema(
        username='john_snow',
        first_name='John',
        last_name='Snow',
        email='lord_commader@north.wall',
        password='password123',
        password_confirmation='password123',
    )
    try:
        john_snow = await UserService.create_user(get_db, john_snow)
    except Exception:
        assert 1 == 0, 'UserService unexpectedly threw an exception'  # This should not happen

    assert 'id' in dir(john_snow)

    user_from_db = await user_repo.get_user_by_id(john_snow.id)
    assert user_from_db is not None
    assert user_from_db.hashed_password != 'password123'


@pytest.mark.asyncio
async def test_create_user_already_existing(
    user_repo: UserRepository,
    get_db: AsyncSession,
):
    john_snow = user_repo.create_user_with_hashed_password(
        username='john_snow',
        first_name='John',
        last_name='Snow',
        email='lord_commader@north.wall',
        hashed_password='password123',
    )

    await user_repo.commit_me(john_snow)

    john_snow = UserSignUpSchema(
        username='john_snow',
        first_name='John',
        last_name='Snow',
        email='lord_commader@north.wall',
        password='password123',
        password_confirmation='password123'
    )

    try:
        await UserService.create_user(get_db, john_snow)
        assert 1 == 0, 'UserService did not throw an exception'
    except UserAlreadyExistsException:
        pass
    except Exception:
        assert 1 == 0, 'UserService should have thrown a UserAlreadyExistsException'


@pytest.mark.asyncio
async def test_get_user_by_id(
    user_repo: UserRepository,
    get_db: AsyncSession,
):
    # Create a user and commit it to the database
    john_snow = user_repo.create_user_with_hashed_password(
        username='john_snow',
        first_name='John',
        last_name='Snow',
        email='lord_commander@north.wall',
        hashed_password='password123'
    )
    await user_repo.commit_me(john_snow)

    # Call the get_user_by_id method
    user = await UserService.get_user_by_id(get_db, john_snow.id)

    # Assert that the returned user is not None
    assert user is not None
    # Assert that the returned user has the correct id
    assert user.id == john_snow.id
    # Assert that the returned user has the correct username
    assert user.username == john_snow.username
    # Assert that the returned user has the correct first name
    assert user.first_name == john_snow.first_name
    # Assert that the returned user has the correct last name
    assert user.last_name == john_snow.last_name
    # Assert that the returned user has the correct email
    assert user.email == john_snow.email


@pytest.mark.asyncio
async def test_get_user_by_id_user_not_found(
    user_repo: UserRepository,
    get_db: AsyncSession,
):
    # Call the get_user_by_id method with an invalid user id
    try:
        user_id = uuid.uuid4()
        await UserService.get_user_by_id(get_db, user_id)
        assert 1 == 0, 'UserService did not throw an exception'
    except UserNotFoundException:
        pass


@pytest.mark.asyncio
async def test_update_user(
    user_repo: UserRepository,
    get_db: AsyncSession,
):
    # Create a user and commit it to the database
    john_snow = user_repo.create_user_with_hashed_password(
        username='john_snow',
        first_name='John',
        last_name='Snow',
        email='lord_commander@north.wall',
        hashed_password=argon2.hash('password123')
    )

    await user_repo.commit_me(john_snow)

    update_schema = UserUpdateSchema(
        first_name='Johny',
        password='password123'
    )
    try:
        await UserService.update_user(get_db, john_snow.id, update_schema)
    except Exception:
        assert 1 == 0, 'UserService unexpectedly threw an exception'

    await get_db.refresh(john_snow)

    assert john_snow.first_name == 'Johny'


@pytest.mark.asyncio
async def test_update_user_user_not_found(
    user_repo: UserRepository,
    get_db: AsyncSession,
):
    update_schema = UserUpdateSchema(
        first_name='Johny',
        password='password123'
    )
    try:
        await UserService.update_user(get_db, uuid.uuid4(), update_schema)
        assert 1 == 0, 'UserService did not throw an exception'
    except UserNotFoundException:
        pass


@pytest.mark.asyncio
async def test_update_user_invalid_password(
    user_repo: UserRepository,
    get_db: AsyncSession,
):
    # Create a user and commit it to the database
    john_snow = user_repo.create_user_with_hashed_password(
        username='john_snow',
        first_name='John',
        last_name='Snow',
        email='lord_commander@north.wall',
        hashed_password=argon2.hash('password123')
    )

    await user_repo.commit_me(john_snow)

    update_schema = UserUpdateSchema(
        first_name='Johny',
        password='password1231'
    )
    try:
        await UserService.update_user(get_db, john_snow.id, update_schema)
        assert 1 == 0, 'UserService did not throw an exception'
    except InvalidPasswordException:
        pass

    await get_db.refresh(john_snow)

    assert john_snow.first_name == 'John'


@pytest.mark.asyncio
@pytest.mark.parametrize(('conflict_field', 'value'), [
    ('email', 'lord_commander@north.wall'),
    ('username', 'john_snow'),
])
async def test_update_user_user_already_exists(
    user_repo: UserRepository,
    get_db: AsyncSession,
    conflict_field: str,
    value: str,
):
    # Create a user and commit it to the database
    john_snow = user_repo.create_user_with_hashed_password(
        username='john_snow',
        first_name='John',
        last_name='Snow',
        email='lord_commander@north.wall',
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

    update_schema = UserUpdateSchema(
        password='password123'
    )
    update_schema.__setattr__(conflict_field, value)

    try:
        await UserService.update_user(get_db, daenerys.id, update_schema)
        assert 1 == 0, 'UserService did not throw an exception'
    except UserAlreadyExistsException as e:
        assert str(e) == f"User with {conflict_field}: '{value}' already exists!"


@pytest.mark.asyncio
async def test_delete_user(
    user_repo: UserRepository,
    get_db: AsyncSession,
):
    john_snow = user_repo.create_user_with_hashed_password(
        username='john_snow',
        first_name='John',
        last_name='Snow',
        email='lord_commander@north.wall',
        hashed_password=argon2.hash('password123')
    )

    await user_repo.commit_me(john_snow)

    await UserService.delete_user(get_db, john_snow.id)

    users = await user_repo.get_all_users()

    assert len(users) == 0


@pytest.mark.asyncio
async def test_delete_user_user_not_found(
    user_repo: UserRepository,
    get_db: AsyncSession,
):
    try:
        await UserService.delete_user(get_db, uuid.uuid4())
        assert 1 == 0, 'UserService did not throw an exception'
    except UserNotFoundException:
        pass
