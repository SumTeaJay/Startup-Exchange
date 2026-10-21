from sqlalchemy import select

from app.db import Base, SessionLocal, engine
from app.models import Post, PostType, User
from app.security import hash_password


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if db.scalar(select(User).where(User.email == "founder@example.com")):
            return
        founder = User(email="founder@example.com", password_hash=hash_password("password123"), name="Алексей Основатель")
        builder = User(email="builder@example.com", password_hash=hash_password("password123"), name="Мария Разработчик")
        db.add_all([founder, builder])
        db.flush()
        db.add(Post(author_id=founder.id, type=PostType.STARTUP, title="AI-платформа для студенческих команд", description="Ищем людей для создания сервиса подбора команд.", looking_for="Backend или product-minded frontend разработчик"))
        db.commit()


if __name__ == "__main__":
    seed()
