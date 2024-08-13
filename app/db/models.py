import enum
from datetime import datetime
from typing import ClassVar
from uuid import UUID, uuid4

from sqlalchemy import TIMESTAMP, Boolean, ForeignKey, String, UniqueConstraint, Uuid
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

    company_actions: Mapped[list['CompanyAction']] = relationship(back_populates='user')

    def __repr__(self) -> str:
        return f'<User {self.username}>'


class Company(ModelWithIdAndTimeStamps):
    __tablename__ = 'companies'

    name: Mapped[str] = mapped_column(String(50), index=True)
    description: Mapped[str] = mapped_column(String(250), nullable=True)
    hidden: Mapped[bool] = mapped_column(Boolean, default=True)
    owner_id: Mapped[UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))

    owner: Mapped[User] = relationship(back_populates='companies')
    company_actions: Mapped[list['CompanyAction']] = relationship(back_populates='company')


class CompanyActionType(enum.Enum):
    INVITATION = 'invitation'
    REQUEST = 'request'
    MEMBERSHIP = 'membership'
    ADMIN = 'admin'


class CompanyAction(ModelWithIdAndTimeStamps):
    __tablename__ = 'company_actions'

    company_id: Mapped[UUID] = mapped_column(ForeignKey('companies.id', ondelete='CASCADE'))
    user_id: Mapped[UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    type: Mapped[CompanyActionType]

    __table_args__ = (UniqueConstraint('company_id', 'user_id', name='unique_company_user'),)

    company: Mapped[Company] = relationship(back_populates='company_actions')
    user: Mapped[User] = relationship(back_populates='company_actions')


class Quizz(ModelWithIdAndTimeStamps):
    __tablename__ = 'quizzes'

    title: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(String(250), nullable=True)
    company_id: Mapped[UUID] = mapped_column(ForeignKey('companies.id', ondelete='CASCADE'))
    frequency: Mapped[int]


class Question(ModelWithIdAndTimeStamps):
    __tablename__ = 'questions'

    text: Mapped[str] = mapped_column(String(250))
    quizz_id: Mapped[UUID] = mapped_column(ForeignKey('quizzes.id', ondelete='CASCADE'))



class Answer(ModelWithIdAndTimeStamps):
    __tablename__ = 'answers'

    text: Mapped[str] = mapped_column(String(250))
    question_id: Mapped[UUID] = mapped_column(ForeignKey('questions.id', ondelete='CASCADE'))
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)
