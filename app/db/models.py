from datetime import datetime
from typing import ClassVar
from uuid import UUID, uuid4

from sqlalchemy import TIMESTAMP, Boolean, ForeignKey, String, Uuid
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship

Base = declarative_base()


class ModelBase(AsyncAttrs, Base):
    """Base class for all models containing UUID as primary key."""

    __abstract__ = True

    type_annotation_map: ClassVar[dict] = {
        datetime: TIMESTAMP(timezone=True),
        UUID: Uuid,
        str: String,
        bool: Boolean,
    }

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    created_at: Mapped[datetime] = mapped_column(server_default='now()')
    updated_at: Mapped[datetime] = mapped_column(server_default='now()', onupdate=datetime.now)


class User(ModelBase):
    __tablename__ = 'users'

    username: Mapped[str] = mapped_column(String(50), index=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=True)
    last_name: Mapped[str] = mapped_column(String(50), nullable=True)
    # email index is useful for searching users by email when using jwt
    email: Mapped[str] = mapped_column(String(50), index=True, unique=True)
    hashed_password: Mapped[str] = mapped_column(String(256))

    companies: Mapped[list['Company']] = relationship(
        'Company', back_populates='owner', cascade='all, delete-orphan', passive_deletes=True
    )

    def __repr__(self) -> str:
        return f'<User {self.username}>'


class Company(ModelBase):
    __tablename__ = 'companies'

    name: Mapped[str] = mapped_column(String(50), index=True)
    description: Mapped[str] = mapped_column(String(250), nullable=True)
    hidden: Mapped[bool] = mapped_column(Boolean, default=True)
    owner_id: Mapped[UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))

    owner: Mapped[User] = relationship(back_populates='companies')
