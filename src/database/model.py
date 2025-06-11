from email import message
from sqlalchemy.orm import DeclarativeBase, Mapped, sessionmaker, mapped_column
from sqlalchemy import ForeignKey
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


class UserMessageAI(Base):
    """
    UserMessageAI model representing a message sent by the AI to a user.
    Contains fields for message ID, user ID, and the message content.
    """

    __tablename__ = "user_message_ai"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    is_ai: Mapped[bool] = mapped_column(default=False)
    message: Mapped[str] = mapped_column()

    def shema(self):
        """
        Schema method to return a dictionary representation of the UserMessageAI instance.
        """
        return {"role": "assistant" if self.is_ai else "user", "content": self.message}


Base.metadata.create_all(bind=engine)
