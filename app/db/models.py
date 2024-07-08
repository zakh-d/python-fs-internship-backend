from datetime import datetime
from sqlalchemy import BIGINT, TIMESTAMP, Boolean, String, Uuid
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import mapped_column, Mapped, declarative_base
from uuid import UUID

Base = declarative_base()


class ModelBase(AsyncAttrs, Base):
    """Base class for all models containing UUID as primary key."""
    __abstract__ = True

    type_annotation_map = {
        int: BIGINT,
        datetime: TIMESTAMP(timezone=True),
        UUID: Uuid,
        str: String,
        bool: Boolean,
    }

    id: Mapped[UUID] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(server_default='now()')
    updated_at: Mapped[datetime] = mapped_column(server_default='now()', onupdate='now()')


class User(ModelBase):
    __tablename__ = 'users'

    username: Mapped[str] = mapped_column(index=True, unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]

    def __repr__(self):
        return f'<User {self.username}>'
