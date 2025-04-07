from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from models import Base  # 👈 Required for init_db

# Load database URL from Docker env or fallback
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5433/data_pipeline")

# Engine and session setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# ✅ Dependency for injecting DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ This is what fixes your current issue
def init_db():
    Base.metadata.create_all(bind=engine)
