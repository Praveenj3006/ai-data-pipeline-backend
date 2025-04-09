import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ✅ Get the DATABASE_URL from environment variable (Render sets this securely)
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL not set in environment variables.")

# ✅ Create engine & session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ✅ Declarative base for models
Base = declarative_base()

# ✅ Dependency for DB session (used in FastAPI routes)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Initialize DB tables (run at app startup)
def init_db():
    from models import User, Pipeline  # Import models to register with Base
    Base.metadata.create_all(bind=engine)
