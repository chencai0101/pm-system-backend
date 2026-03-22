import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import PagePermission, ProjectPermission, Member, Project

router = APIRouter()


@router.get("/permissions/pages")
def get_page_permissions(db: Session = Depends(get_db)):
    try:
        perms = db.query(PagePermission).all()
        members = {m.id: m.name for m in db.query(Member).all()}
        return {
            "data": [
                {
                    "id": p.id,
                    "member_id": p.member_id,
                    "page_key": p.page_key,
                    "enabled": p.enabled,
                    "member_name": members.get(p.member_id, ""),
                }
                for p in perms
            ],
            "error": None,
        }
    except Exception as e:
        return {"data": None, "error": str(e)}


@router.put("/permissions/pages")
def update_page_permissions(body: list[dict], db: Session = Depends(get_db)):
    try:
        # body: [{"member_id": "...", "page_key": "...", "enabled": true/false}, ...]
        for item in body:
            existing = (
                db.query(PagePermission)
                .filter(
                    PagePermission.member_id == item["member_id"],
                    PagePermission.page_key == item["page_key"],
                )
                .first()
            )
            if existing:
                existing.enabled = item.get("enabled", False)
            else:
                perm = PagePermission(
                    id=uuid.uuid4().hex,
                    member_id=item["member_id"],
                    page_key=item["page_key"],
                    enabled=item.get("enabled", False),
                )
                db.add(perm)
        db.commit()
        return get_page_permissions(db)
    except Exception as e:
        db.rollback()
        return {"data": None, "error": str(e)}


@router.get("/permissions/projects")
def get_project_permissions(db: Session = Depends(get_db)):
    try:
        perms = db.query(ProjectPermission).all()
        projects = {p.id: p.name for p in db.query(Project).all()}
        return {
            "data": [
                {
                    "id": p.id,
                    "member_id": p.member_id,
                    "project_id": p.project_id,
                    "can_edit": p.can_edit,
                    "project_name": projects.get(p.project_id, ""),
                }
                for p in perms
            ],
            "error": None,
        }
    except Exception as e:
        return {"data": None, "error": str(e)}


@router.put("/permissions/projects/{member_id}")
def update_member_project_permissions(member_id: str, body: list[dict], db: Session = Depends(get_db)):
    try:
        member = db.query(Member).filter(Member.id == member_id).first()
        if not member:
            return {"data": None, "error": f"Member {member_id} not found"}

        # Replace-style: delete existing, then insert new
        db.query(ProjectPermission).filter(ProjectPermission.member_id == member_id).delete()

        for item in body:
            perm = ProjectPermission(
                id=uuid.uuid4().hex,
                member_id=member_id,
                project_id=item["project_id"],
                can_edit=item.get("can_edit", True),
            )
            db.add(perm)
        db.commit()
        return get_project_permissions(db)
    except Exception as e:
        db.rollback()
        return {"data": None, "error": str(e)}
