import enum
from datetime import datetime
from typing import ClassVar
from uuid import UUID, uuid4

from sqlalchemy import TIMESTAMP, Boolean, Column, Enum, ForeignKey, String, Table, Uuid
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class ModelWithIdAndTimeStamps(AsyncAttrs, Base):
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


associate_table = Table(
    'membership_table',
    Base.metadata,
    Column('company_id', ForeignKey('companies.id', ondelete='CASCADE'), primary_key=True),
    Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
)


class User(ModelWithIdAndTimeStamps):
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

    participated_companies: Mapped[list['Company']] = relationship(secondary=associate_table, back_populates='members')
    invitations: Mapped[list['Invitation']] = relationship(back_populates='user')
    requests: Mapped[list['Invitation']] = relationship(back_populates='user')

    def __repr__(self) -> str:
        return f'<User {self.username}>'


class Company(ModelWithIdAndTimeStamps):
    __tablename__ = 'companies'

    name: Mapped[str] = mapped_column(String(50), index=True)
    description: Mapped[str] = mapped_column(String(250), nullable=True)
    hidden: Mapped[bool] = mapped_column(Boolean, default=True)
    owner_id: Mapped[UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))

    owner: Mapped[User] = relationship(back_populates='companies')
    members: Mapped[list[User]] = relationship(secondary=associate_table, back_populates='participated_companies')
    invitations: Mapped[list['Invitation']] = relationship(back_populates='company')
    requests: Mapped[list['Request']] = relationship(back_populates='company')


class RequestInviteStatus(enum.Enum):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'


class Invitation(Base):
    __tablename__ = 'invitations'

    user_id: Mapped[UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    company_id: Mapped[UUID] = mapped_column(ForeignKey('companies.id', ondelete='CASCADE'), primary_key=True)
    pending: Mapped[RequestInviteStatus] = mapped_column(
        Enum(RequestInviteStatus, name='invitation_status'), default=RequestInviteStatus.PENDING
    )

    user: Mapped[User] = relationship(back_populates='invitations')
    company: Mapped[Company] = relationship(back_populates='invitations')


class Request(Base):
    __tablename__ = 'requests'

    user_id: Mapped[UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    company_id: Mapped[UUID] = mapped_column(ForeignKey('companies.id', ondelete='CASCADE'), primary_key=True)
    pending: Mapped[RequestInviteStatus] = mapped_column(
        Enum(RequestInviteStatus, name='request_status'), default=RequestInviteStatus.PENDING
    )

    user: Mapped[User] = relationship(back_populates='requests')
    company: Mapped[Company] = relationship(back_populates='requests')
