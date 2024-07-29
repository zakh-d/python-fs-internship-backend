from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.db.models import RequestInviteStatus


class InvitationOrRequestCreateSchema(BaseModel):
    user_id: UUID
    company_id: UUID


class InvitationOrRequestSchema(InvitationOrRequestCreateSchema):
    status: RequestInviteStatus

    model_config = ConfigDict(from_attributes=True)
