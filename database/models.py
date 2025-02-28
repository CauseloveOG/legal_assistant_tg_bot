from sqlalchemy import BigInteger, Integer, Text, ForeignKey, String
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .data_base import Base


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str] = mapped_column(String, nullable=True)
    full_name: Mapped[str] = mapped_column(String, nullable=True)

    cases: Mapped[list['Case']] = relationship('Case', back_populates='user', cascade='all, delete-orphan')


class Case(Base):
    __tablename__ = 'cases'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=True)
    case_name: Mapped[str] = mapped_column(String, nullable=True, unique=True)
    case_number: Mapped[str] = mapped_column(String, nullable=True)
    court_name: Mapped[str] = mapped_column(String, nullable=True)

    user: Mapped['User'] = relationship('User', back_populates='cases')
