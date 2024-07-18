from typing import Any

from fastapi import HTTPException, status


class UserNotFoundException(HTTPException):
    def __init__(self, field_name: str, value: any) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User with {field_name}={value} not found!'
        )


class InvalidPasswordException(HTTPException):

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid credentials',
        )


class UserAlreadyExistsException(HTTPException):

    def __init__(self, conflicting_field: str, value: Any) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'User with {conflicting_field}: {value} already exists!'
        )
