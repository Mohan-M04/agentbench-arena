from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import BenchmarkTask
from schemas import BenchmarkTaskCreate, BenchmarkTaskOut

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])

@router.get("", response_model=List[BenchmarkTaskOut])
def list_tasks(db: Session = Depends(get_db)):
    return db.query(BenchmarkTask).all()

@router.post("", response_model=BenchmarkTaskOut)
def create_task(task: BenchmarkTaskCreate, db: Session = Depends(get_db)):
    db_task = db.query(BenchmarkTask).filter(BenchmarkTask.id == task.id).first()
    if db_task:
        raise HTTPException(status_code=400, detail="Task ID already exists")
    new_task = BenchmarkTask(**task.dict())
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@router.get("/{task_id}", response_model=BenchmarkTaskOut)
def get_task(task_id: str, db: Session = Depends(get_db)):
    task = db.query(BenchmarkTask).filter(BenchmarkTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
