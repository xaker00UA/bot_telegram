from src.database.model import SessionLocal, User, UserMessageAI


def get_user_language(user_id: int):
    with SessionLocal() as session:
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            return user.language
        return "en"


def set_user_language(user_id: int, language: str):
    with SessionLocal() as session:
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            user.language = language
            session.commit()
        else:
            new_user = User(id=user_id, language=language)
            session.add(new_user)
            session.commit()


def add_message(user_id: int, message: str, is_ai: bool = False):
    with SessionLocal() as session:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            set_user_language(
                user_id, "en"
            )  # Устанавливаем язык по умолчанию, если пользователь не найден

        # Получаем количество сообщений пользователя
        user_messages = (
            session.query(UserMessageAI)
            .filter(UserMessageAI.user_id == user_id)
            .order_by(UserMessageAI.id)
            .all()
        )

        # Если сообщений 20 или больше, удаляем самое старое
        if len(user_messages) >= 20:
            session.delete(user_messages[0])  # Удаляем первое (старое) сообщение

        # Добавляем новое сообщение
        new_message = UserMessageAI(user_id=user_id, message=message, is_ai=is_ai)
        session.add(new_message)
        session.commit()


def get_messages(user_id: int) -> list[UserMessageAI]:
    with SessionLocal() as session:
        messages = (
            session.query(UserMessageAI).filter(UserMessageAI.user_id == user_id).all()
        )
        return messages
