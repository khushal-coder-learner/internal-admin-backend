from app.core.security import pwd_context
from app.db.session import SessionLocal
from app.models.user import User
from sqlalchemy import select

ADMIN_EMAIL = "admin@example.com"

def admin_exists(db):
    stmt = select(User).where(User.email == ADMIN_EMAIL)
    return db.execute(stmt).scalar_one_or_none()


def create_admin():
    db = SessionLocal()
    try:
        existing_admin = admin_exists(db)

        if existing_admin:
            print("Admin user already exists")
            return

        admin_user = User(
            email="admin@example.com",
            hashed_password=pwd_context.hash("admin123"),
            role="admin",
        )

        db.add(admin_user)
        db.commit()

        print("Admin user created successfully")

    finally:
        db.close()


if __name__ == "__main__":
    create_admin()