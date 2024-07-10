from datetime import datetime
from sqlalchemy import TIMESTAMP, String, Uuid
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import mapped_column, Mapped, declarative_base
from uuid import UUID

Base = declarative_base()


class ModelBase(AsyncAttrs, Base):
    """Base class for all models containing UUID as primary key."""
    __abstract__ = True

    type_annotation_map = {
        datetime: TIMESTAMP(timezone=True),
        UUID: Uuid,
        str: String,
    }

    id: Mapped[UUID] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(server_default='now()')
    updated_at: Mapped[datetime] = mapped_column(server_default='now()', onupdate='now()')


class User(ModelBase):
    __tablename__ = 'users'

    username: Mapped[str] = mapped_column(String(50), index=True, unique=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=True)
    last_name: Mapped[str] = mapped_column(String(50), nullable=True)
    # email index is useful for searching users by email when using jwt
    email: Mapped[str] = mapped_column(String(50), index=True, unique=True)
    hashed_password: Mapped[str] = mapped_column(String(256))

    def __repr__(self):
        return f'<User {self.username}>'
