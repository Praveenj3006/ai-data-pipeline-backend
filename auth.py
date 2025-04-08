from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from pydantic import BaseModel
import jwt
import datetime

from models import User
from database import get_db

# 🔐 JWT secret key — change this in production!
SECRET_KEY = "your_secret_key"

# 🔒 Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 🛡️ OAuth2 scheme — expects POST to /token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# 📦 Auth router
auth_router = APIRouter()

# 📌 Signup request body schema
class SignupRequest(BaseModel):
    username: str
    password: str
    email: str

# ✅ Signup route
@auth_router.post("/signup")
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    username = payload.username
    password = payload.password
    email = payload.email

    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already in use")

    hashed_pw = pwd_context.hash(password)
    new_user = User(username=username, email=email, password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully"}

# ✅ Login logic — used by /token route
async def login(form_data: OAuth2PasswordRequestForm, db: Session):
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user or not pwd_context.verify(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    token_data = {
        "sub": user.username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }

    token = jwt.encode(token_data, SECRET_KEY, algorithm="HS256")
    return {"access_token": token, "token_type": "bearer"}

# ✅ Token verification middleware
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
