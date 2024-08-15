from fastapi import HTTPException, status


class QuizzNotFound(HTTPException):
    
    def __init__(self, item: str = 'Quizz') -> None:
        super().__init__(status.HTTP_404_NOT_FOUND, f'{item} not found')


class QuizzError(HTTPException):
    
    def __init__(self, detail: str) -> None:
        super().__init__(status.HTTP_400_BAD_REQUEST, detail)
