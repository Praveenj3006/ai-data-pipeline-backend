import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ✅ Load the DATABASE_URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

# ✅ Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# ✅ Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ✅ Base class for models
Base = declarative_base()

# ✅ Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Optional: call this during app startup to ensure tables are created
def init_db():
    from models import User, Pipeline  # Import models here to register them with Base
    Base.metadata.create_all(bind=engine)
