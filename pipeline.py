from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from database import get_db
from models import Pipeline, User
from auth import get_current_user

pipeline_router = APIRouter()

# 🔧 Request body models
class PipelineCreate(BaseModel):
    name: str
    status: str

class PipelineUpdate(BaseModel):
    name: str
    status: str

# ✅ Create pipeline
@pipeline_router.post("/pipelines")
def create_pipeline(
    payload: PipelineCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    user = db.query(User).filter(User.username == current_user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    pipeline = Pipeline(name=payload.name, status=payload.status, owner=user)
    db.add(pipeline)
    db.commit()
    db.refresh(pipeline)
    return {"message": "Pipeline created", "id": pipeline.id}

# ✅ Get all pipelines for the current user
@pipeline_router.get("/pipelines")
def get_pipelines(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    user = db.query(User).filter(User.username == current_user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    pipelines = db.query(Pipeline).filter(Pipeline.owner_id == user.id).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "status": p.status,
            "created_at": p.timestamp.isoformat() if p.timestamp else None
        }
        for p in pipelines
    ]

# ✅ Update a pipeline
@pipeline_router.put("/pipelines/{pipeline_id}")
def update_pipeline(
    pipeline_id: int,
    payload: PipelineUpdate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()

    if not pipeline or pipeline.owner.username != current_user:
        raise HTTPException(status_code=404, detail="Pipeline not found or unauthorized")

    pipeline.name = payload.name
    pipeline.status = payload.status
    db.commit()
    return {"message": "Pipeline updated"}

# ✅ Delete a pipeline
@pipeline_router.delete("/pipelines/{pipeline_id}")
def delete_pipeline(
    pipeline_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()

    if not pipeline or pipeline.owner.username != current_user:
        raise HTTPException(status_code=404, detail="Pipeline not found or unauthorized")

    db.delete(pipeline)
    db.commit()
    return {"message": "Pipeline deleted"}
