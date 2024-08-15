from fastapi import HTTPException, status


class QuizzNotFound(HTTPException):
    
    def __init__(self) -> None:
        super().__init__(status.HTTP_404_NOT_FOUND, 'Quizz not found')


class QuizzError(HTTPException):
    
    def __init__(self, detail: str) -> None:
        super().__init__(status.HTTP_400_BAD_REQUEST, detail)
