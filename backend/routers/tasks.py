from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from typing import List
from database import get_session
from models import Task

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.get("/", response_model=List[Task])
def get_tasks(session: Session = Depends(get_session)):
    # Simple list for MVP, maybe filter later
    statement = select(Task).order_by(Task.due_date)
    tasks = session.exec(statement).all()
    return tasks

@router.patch("/{task_id}/toggle")
def toggle_task(task_id: str, session: Session = Depends(get_session)):
    # task_id is UUID but passed as str
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = "done" if task.status == "todo" else "todo"
    session.add(task)
    session.commit()
    session.refresh(task)
    return task
