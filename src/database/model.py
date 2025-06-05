from ssl import cert_time_to_seconds
from sqlalchemy.orm import DeclarativeBase, Mapped, sessionmaker, mapped_column
from sqlalchemy import create_engine


engine = create_engine("sqlite:///./user.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """
    Base class for all database models.
    Inherits from DeclarativeBase to enable SQLAlchemy ORM features.
    """

    pass


class User(Base):
    """
    User model representing a user in the system.
    Contains fields for user ID, username, and email.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    language: Mapped[str] = mapped_column(default="en")


Base.metadata.create_all(bind=engine)
