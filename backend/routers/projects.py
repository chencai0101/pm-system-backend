from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Project, Task
from backend.schemas import ApiResponse, Project as ProjectSchema

router = APIRouter()


@router.get("/projects")
def get_projects(db: Session = Depends(get_db)):
    try:
        db_projects = db.query(Project).all()
        projects_data = []
        for p in db_projects:
            total = db.query(Task).filter(Task.project_id == p.id).count()
            completed = (
                db.query(Task)
                .filter(Task.project_id == p.id, Task.status == "done")
                .count()
            )
            progress = completed / total if total > 0 else 0.0

            projects_data.append(
                {
                    "id": p.id,
                    "name": p.name,
                    "owner": p.owner,
                    "start_date": p.start_date,
                    "end_date": p.end_date,
                    "status": p.status,
                    "description": p.description or "",
                    "task_count": total,
                    "completed_count": completed,
                    "progress": round(progress, 3),
                    "created_at": p.created_at,
                    "updated_at": p.updated_at,
                }
            )

        return {"data": projects_data, "error": None}
    except Exception as e:
        return {"data": None, "error": str(e)}
