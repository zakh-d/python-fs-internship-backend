from uuid import UUID

from fastapi import HTTPException, status

from app.db.models import CompanyActionType


class CompanyPermissionException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN, detail='User does not have permission for this action on the company'
        )


class CompanyNotFoundException(HTTPException):
    def __init__(self, company_id: UUID):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=f'Company with id {company_id} not found')


class UserAlreadyInvitedException(HTTPException):
    def __init__(self, user_id: UUID, company_id: UUID):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'User with id {user_id} is already invited to company with id {company_id}',
        )


class ActionNotFound(HTTPException):
    def __init__(self, type: CompanyActionType):
        if type == CompanyActionType.INVITATION:
            message = 'Invitation either not found, accepted or canceled'
        elif type == CompanyActionType.REQUEST:
            message = 'Request either not found, accepted or canceled'
        elif type == CompanyActionType.ADMIN:
            message = 'User is not an admin of this company'
        else:
            message = 'User is not a member of this company'
        super().__init__(status.HTTP_404_NOT_FOUND, message)


class CompanyActionException(HTTPException):
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )
