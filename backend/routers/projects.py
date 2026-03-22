from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Project, Task
from backend.schemas import ApiResponse, Project as ProjectSchema

router = APIRouter()


def build_task_response(task: Task) -> dict:
    """Build a task response with subtasks."""
    subtasks = []
    for st in task.subtasks:
        subtasks.append({
            "id": st.id,
            "task_id": st.task_id,
            "title": st.title,
            "completed": st.completed,
            "completed_at": st.completed_at,
            "created_at": st.created_at,
        })
    return {
        "id": task.id,
        "project_id": task.project_id,
        "parent_id": None,
        "title": task.title,
        "owner": task.owner,
        "status": task.status,
        "priority": task.priority,
        "start_date": task.start_date,
        "end_date": task.end_date,
        "completed_at": task.completed_at,
        "note": task.note or "",
        "subtasks": subtasks,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
    }


@router.get("/projects/{project_id}/tasks")
def get_project_tasks(project_id: str, db: Session = Depends(get_db)):
    try:
        tasks = db.query(Task).filter(Task.project_id == project_id).all()
        return {"data": [build_task_response(t) for t in tasks], "error": None}
    except Exception as e:
        return {"data": None, "error": str(e)}


@router.post("/projects/{project_id}/tasks")
def create_project_task(project_id: str, body: dict, db: Session = Depends(get_db)):
    try:
        proj = db.query(Project).filter(Project.id == project_id).first()
        if not proj:
            return {"data": None, "error": f"Project {project_id} not found"}

        import re
        all_task_ids = db.query(Task.id).all()
        max_num = 0
        for (tid,) in all_task_ids:
            m = re.match(r'T-(\d+)', tid)
            if m: max_num = max(max_num, int(m.group(1)))
        task_id = f"T-{max_num + 1:03d}"

        task = Task(
            id=task_id,
            project_id=project_id,
            title=body.get("title", ""),
            owner=body.get("owner", proj.owner),
            status=body.get("status", "open"),
            priority=body.get("priority", "medium"),
            start_date=proj.start_date,
            end_date=body.get("end_date") or proj.end_date,
            note=body.get("note", ""),
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return {"data": build_task_response(task), "error": None}
    except Exception as e:
        db.rollback()
        return {"data": None, "error": str(e)}


@router.post("/projects")
def create_project(body: dict, db: Session = Depends(get_db)):
    try:
        import re
        from datetime import datetime

        all_project_ids = db.query(Project.id).all()
        max_num = 0
        for (pid,) in all_project_ids:
            m = re.match(r'P-(\d+)', pid)
            if m:
                max_num = max(max_num, int(m.group(1)))
        project_id = f"P-{max_num + 1:03d}"

        from datetime import date as date_cls
        project = Project(
            id=project_id,
            name=body.get("name", ""),
            owner=body.get("owner", ""),
            start_date=date_cls.fromisoformat(body.get("start_date", "")),
            end_date=date_cls.fromisoformat(body.get("end_date", "")),
            status="open",
            description=body.get("description", ""),
        )
        db.add(project)
        db.commit()
        db.refresh(project)

        return {
            "data": {
                "id": project.id,
                "name": project.name,
                "owner": project.owner,
                "start_date": project.start_date,
                "end_date": project.end_date,
                "status": project.status,
                "description": project.description or "",
                "task_count": 0,
                "completed_count": 0,
                "progress": 0.0,
                "created_at": project.created_at,
                "updated_at": project.updated_at,
            },
            "error": None,
        }
    except Exception as e:
        db.rollback()
        return {"data": None, "error": str(e)}


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
