from uuid import UUID
from fastapi import HTTPException, status


class CompanyPermissionException(HTTPException):

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='User does not have permission to edit this company'
        )


class CompanyNotFoundException(HTTPException):

    def __init__(self, company_id: UUID):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Company with id {company_id} not found'
        )
