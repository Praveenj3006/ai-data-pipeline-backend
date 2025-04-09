from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from auth import auth_router, get_current_user, get_db
from pipeline import pipeline_router
from database import init_db, engine
from models import User, Base

app = FastAPI(
    title="AI Data Pipeline API",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# ✅ CORS Setup
origins = [
    "https://deluxe-churros-d93fea.netlify.app",
    "http://localhost:8081",
    "http://127.0.0.1:8081"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Initialize DB at startup
@app.on_event("startup")
def on_startup():
    try:
        init_db()
    except Exception as e:
        print("DB Init failed:", e)

# ✅ Health check
@app.get("/")
def home():
    return {"message": "Welcome to AI Data Pipeline API"}

# ✅ Register Auth and Pipeline routers
app.include_router(auth_router, tags=["Auth"])
app.include_router(pipeline_router, tags=["Pipelines"])

# ✅ Get logged-in user profile
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

# ✅ Temporary endpoint to ensure tables are created
@app.get("/init")
def init_tables():
    Base.metadata.create_all(bind=engine)
    return {"message": "Tables created!"}
