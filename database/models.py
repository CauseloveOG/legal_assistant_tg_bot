from datetime import datetime

from sqlalchemy import BigInteger, Integer, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .data_base import Base


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str | None]
    full_name: Mapped[str | None]
    reminder_enabled: Mapped[bool] = mapped_column(Boolean, default=False)

    cases: Mapped[list['Case']] = relationship(
        'Case',
        back_populates='user',
        cascade='all, delete-orphan')


class Case(Base):
    __tablename__ = 'cases'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id'))
    case_name: Mapped[str]
    case_number: Mapped[str | None]
    court_name: Mapped[str | None]

    user: Mapped['User'] = relationship(
        'User',
        back_populates='cases')

    session: Mapped['Session'] = relationship(
        'Session',
        back_populates='case',
        cascade='all, delete-orphan')


class Session(Base):
    __tablename__ = 'sessions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    case_id: Mapped[int] = mapped_column(Integer, ForeignKey('cases.id'), unique=True)
    date: Mapped[datetime] = mapped_column(DateTime)
    reminder_sent: Mapped[bool] = mapped_column(Boolean, default=False)

    case: Mapped['Case'] = relationship(
        'Case',
        back_populates='session')