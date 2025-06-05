from src.database.model import SessionLocal, User


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
