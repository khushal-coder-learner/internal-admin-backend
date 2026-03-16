from app.core.security import pwd_context
from app.db.session import SessionLocal
from app.models.user import User

db = SessionLocal()

user = User(
    email="admin@example.com",
    hashed_password=pwd_context.hash("admin123"),
    role="admin",
)

db.add(user)
db.commit()