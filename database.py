from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from models import Base

# 🔧 Replace with your actual DB URL if needed
DATABASE_URL = "postgresql://postgres:password@postgres_db:5432/data_pipeline"

# 🌐 Create engine + session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 📦 Base class for models
Base = declarative_base()

# ✅ Dependency for getting DB session (used in FastAPI routes)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)