from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from auth import auth_router, get_current_user, get_db
from pipeline import pipeline_router
from database import init_db
from models import User

app = FastAPI()

# ✅ CORS Setup — allows frontend to connect
origins = [
    "http://localhost:8081",  # Local frontend (if served)
    "http://127.0.0.1:8081",
    "*",  # Allow all origins during development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Run database initialization at startup
@app.on_event("startup")
def on_startup():
    init_db()

# ✅ Register routers
app.include_router(auth_router, prefix="", tags=["Auth"])
app.include_router(pipeline_router, prefix="", tags=["Pipelines"])

# ✅ Public health check
@app.get("/")
def home():
    return {"message": "Welcome to AI Data Pipeline API"}

# ✅ Get current logged-in user's profile
@app.get("/me")
def read_users_me(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == current_user).first()
    if user:
        return {
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
    raise HTTPException(status_code=404, detail="User not found")
