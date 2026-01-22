from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from typing import List, Optional
from database import get_session
from models import Task
from pydantic import BaseModel

router = APIRouter(prefix="/tasks", tags=["tasks"])

class TaskUpdate(BaseModel):
    description: Optional[str] = None
    assignee: Optional[str] = None
    due_date: Optional[str] = None # Accepts ISO format

@router.get("/", response_model=List[Task])
def get_tasks(session: Session = Depends(get_session)):
    # Simple list for MVP, maybe filter later
    statement = select(Task).order_by(Task.due_date)
    tasks = session.exec(statement).all()
    return tasks

@router.patch("/{task_id}/toggle")
def toggle_task(task_id: str, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = "done" if task.status == "todo" else "todo"
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@router.patch("/{task_id}")
def update_task(task_id: str, update: TaskUpdate, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if update.description is not None:
        task.description = update.description
    if update.assignee is not None:
        task.assignee = update.assignee
    # Handle due date logic if strictly typed in DB vs string here
    # For now, we assume frontend sends compatible string or None

    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@router.delete("/{task_id}")
def delete_task(task_id: str, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
    return {"status": "deleted"}
