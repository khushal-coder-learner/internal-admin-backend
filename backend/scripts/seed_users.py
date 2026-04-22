from app.core.security import pwd_context
from app.db.session import SessionLocal
from app.models.user import User

def seed_users(n: int = 100):
    db = SessionLocal()

    try:
        users = []
        emails = {u.email for u in db.query(User.email).all()}
        for i in range(n):
            email = f"user{i}@example.com"

            # check if already exists (avoid duplicates)
            if email in emails:
                continue
            
            user = User(
                email=email,
                hashed_password=pwd_context.hash("password123"),
                role="staff",
            )
            users.append(user)

        db.add_all(users)
        db.commit()

        print(f"✅ Created {len(users)} users")

    finally:
        db.close()


if __name__ == "__main__":
    seed_users(100)