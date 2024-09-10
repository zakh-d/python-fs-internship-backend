from uuid import UUID

from fastapi import HTTPException, status


class NotificationNotFound(HTTPException):
    def __init__(self, notification_id: UUID):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, detail=f'Notification with id {notification_id} not found'
        )


class CannotSendNotificationException(Exception):
    pass
