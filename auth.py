from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt, JWTError, ExpiredSignatureError
import datetime

from models import User
from database import SessionLocal

# 🔐 Secret key + algorithm
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

# 🔐 Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 🛡️ OAuth2 bearer token handler
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token", auto_error=False)

# 📦 Router
auth_router = APIRouter()

# 📌 DB session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Get current user (from token)
def get_current_user(token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=401, detail="Token missing")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ✅ Signup route
@auth_router.post("/signup")
def signup(username: str, password: str, email: str, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter((User.username == username) | (User.email == email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already exists")

    hashed_pw = pwd_context.hash(password)
    user = User(username=username, email=email, password=hashed_pw)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "User created successfully"}

# ✅ Login route
@auth_router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user or not pwd_context.verify(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create JWT token valid for 24 hours
    token_data = {
        "sub": user.username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

    return {"access_token": token, "token_type": "bearer"}
