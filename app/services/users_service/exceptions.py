class UserNotFoundException(Exception):

    def __init__(self, field_name: str, value: any,  *args: object) -> None:
        self.field_name = field_name
        self.value = value
        super().__init__(*args)

    def __str__(self) -> str:
        return f'User with {self.field_name}={self.value} not found!'


class InvalidPasswordException(Exception):
    pass


class UserWithSameEmailAlreadyExistsException(Exception):
    pass


class UserWithSameUsernameAlreadyExistsException(Exception):
    pass
