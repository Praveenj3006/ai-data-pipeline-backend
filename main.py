from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from auth import auth_router, get_current_user, get_db
from pipeline import pipeline_router
from database import init_db, engine
from models import Base, User

app = FastAPI(
    title="AI Data Pipeline API",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# ✅ CORS
origins = [
    "https://deluxe-churros-d93fea.netlify.app",
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

# ✅ DB initialization
@app.on_event("startup")
def on_startup():
    init_db()

# ✅ Routes
app.include_router(auth_router, prefix="", tags=["Auth"])
app.include_router(pipeline_router, prefix="", tags=["Pipelines"])

# ✅ Home route
@app.get("/")
def home():
    return {"message": "Welcome to AI Data Pipeline API"}

# ✅ /init route to create tables manually if needed
@app.get("/init")
def init_tables():
    Base.metadata.create_all(bind=engine)
    return {"message": "Tables created!"}

# ✅ /me - check token
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

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="AI Data Pipeline API",
        version="1.0.0",
        description="Your FastAPI backend for managing AI data pipelines",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "/login",
                    "scopes": {}
                }
            }
        }
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
