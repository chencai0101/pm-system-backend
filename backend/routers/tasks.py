from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Task, Subtask
from backend.schemas import ApiResponse

router = APIRouter()


@router.get("/tasks")
def get_tasks(db: Session = Depends(get_db)):
    try:
        db_tasks = db.query(Task).all()
        tasks_data = []

        for t in db_tasks:
            subtasks = (
                db.query(Subtask).filter(Subtask.task_id == t.id).all()
            )
            subtasks_data = [
                {
                    "id": s.id,
                    "task_id": s.task_id,
                    "title": s.title,
                    "completed": s.completed,
                    "completed_at": s.completed_at,
                    "created_at": s.created_at,
                }
                for s in subtasks
            ]

            tasks_data.append(
                {
                    "id": t.id,
                    "project_id": t.project_id,
                    "title": t.title,
                    "owner": t.owner,
                    "status": t.status,
                    "priority": t.priority,
                    "start_date": t.start_date,
                    "end_date": t.end_date,
                    "completed_at": t.completed_at,
                    "note": t.note or "",
                    "subtasks": subtasks_data,
                    "created_at": t.created_at,
                    "updated_at": t.updated_at,
                }
            )

        return {"data": tasks_data, "error": None}
    except Exception as e:
        return {"data": None, "error": str(e)}
