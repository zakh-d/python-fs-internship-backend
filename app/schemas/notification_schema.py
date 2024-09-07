from uuid import UUID

from pydantic import BaseModel, ConfigDict


class NotificationSchema(BaseModel):
    id: UUID
    title: str
    body: str
    is_read: bool

    model_config = ConfigDict(from_attributes=True)
