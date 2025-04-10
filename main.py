from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from auth import auth_router, get_current_user, get_db
from pipeline import pipeline_router
from database import init_db
from models import User, Base
from database import engine

app = FastAPI(
    title="AI Data Pipeline API",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# ✅ CORS setup
origins = [
    "https://deluxe-churros-d93fea.netlify.app",  # your frontend
    "http://localhost:8081",
    "http://127.0.0.1:8081",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Initialize DB on startup
@app.on_event("startup")
def on_startup():
    init_db()

# ✅ Include auth and pipeline routers
app.include_router(auth_router, prefix="", tags=["Auth"])
app.include_router(pipeline_router, prefix="", tags=["Pipelines"])

# ✅ Home endpoint
@app.get("/")
def home():
    return {"message": "Welcome to AI Data Pipeline API"}

# ✅ Authenticated user profile
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

# ✅ Manual table init (optional fallback)
@app.get("/init")
def init_tables():
    Base.metadata.create_all(bind=engine)
    return {"message": "Tables created!"}
