from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Project, Task, Member, ProjectPermission
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


@router.patch("/projects/{project_id}")
def update_project(project_id: str, body: dict, db: Session = Depends(get_db)):
    try:
        proj = db.query(Project).filter(Project.id == project_id).first()
        if not proj:
            return {"data": None, "error": f"Project {project_id} not found"}

        if "name" in body:
            proj.name = body["name"]
        if "owner" in body:
            proj.owner = body["owner"]
        if "start_date" in body:
            from datetime import date as date_cls
            proj.start_date = date_cls.fromisoformat(body["start_date"])
        if "end_date" in body:
            from datetime import date as date_cls
            proj.end_date = date_cls.fromisoformat(body["end_date"])
        if "description" in body:
            proj.description = body["description"]
        if "status" in body:
            proj.status = body["status"]

        db.commit()
        db.refresh(proj)

        total = db.query(Task).filter(Task.project_id == proj.id).count()
        completed = (
            db.query(Task)
            .filter(Task.project_id == proj.id, Task.status == "done")
            .count()
        )
        progress = completed / total if total > 0 else 0.0

        return {
            "data": {
                "id": proj.id,
                "name": proj.name,
                "owner": proj.owner,
                "start_date": proj.start_date,
                "end_date": proj.end_date,
                "status": proj.status,
                "description": proj.description or "",
                "task_count": total,
                "completed_count": completed,
                "progress": round(progress, 3),
                "created_at": proj.created_at,
                "updated_at": proj.updated_at,
            },
            "error": None,
        }
    except Exception as e:
        db.rollback()
        return {"data": None, "error": str(e)}


@router.post("/projects")
def create_project(body: dict, db: Session = Depends(get_db)):
    try:
        import re
        import uuid
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

        # Auto-create ProjectPermission for the project owner
        owner_name = body.get("owner", "")
        if owner_name:
            owner_member = db.query(Member).filter(Member.name == owner_name).first()
            if owner_member:
                perm = ProjectPermission(
                    id=uuid.uuid4().hex,
                    member_id=owner_member.id,
                    project_id=project.id,
                    can_edit=True,
                )
                db.add(perm)
                db.commit()

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


@router.delete("/projects/{project_id}")
def delete_project(project_id: str, db: Session = Depends(get_db)):
    """Delete a project. Allowed for admins or the project owner."""
    try:
        from backend.models import Member

        proj = db.query(Project).filter(Project.id == project_id).first()
        if not proj:
            return {"data": None, "error": f"Project {project_id} not found"}

        # Check: if any admin exists, allow deletion (simple permission model)
        admin_exists = db.query(Member).filter(Member.role == "admin").first() is not None
        # Also allow if the project owner is a registered member
        owner_is_member = (
            db.query(Member).filter(Member.name == proj.owner).first() is not None
        )

        if not admin_exists and not owner_is_member:
            return {"data": None, "error": "只有管理员或项目负责人（已在成员列表中）可以删除该项目"}

        db.delete(proj)
        db.commit()
        return {"data": {"deleted": project_id}, "error": None}
    except Exception as e:
        db.rollback()
        return {"data": None, "error": str(e)}
