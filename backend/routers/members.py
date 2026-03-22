import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Member, ProjectPermission, Project

router = APIRouter()


@router.get("/members")
def get_members(name: str = "", db: Session = Depends(get_db)):
    try:
        query = db.query(Member)
        if name:
            query = query.filter(Member.name.ilike(f"%{name}%"))
        members = query.order_by(Member.created_at.desc()).all()
        return {
            "data": [
                {
                    "id": m.id,
                    "name": m.name,
                    "role": m.role,
                    "wecom_user_id": m.wecom_user_id,
                    "wecom_name": m.wecom_name,
                    "wecom_avatar": m.wecom_avatar,
                    "mobile": m.mobile,
                    "department_id": m.department_id,
                    "created_at": m.created_at,
                    "updated_at": m.updated_at,
                }
                for m in members
            ],
            "error": None,
        }
    except Exception as e:
        return {"data": None, "error": str(e)}


@router.post("/members")
def create_member(body: dict, db: Session = Depends(get_db)):
    try:
        # Check uniqueness of wecom_user_id
        existing = db.query(Member).filter(Member.wecom_user_id == body.get("wecom_user_id")).first()
        if existing:
            return {"data": None, "error": f"wecom_user_id {body.get('wecom_user_id')} already exists"}

        member = Member(
            id=uuid.uuid4().hex,
            name=body.get("name", ""),
            role=body.get("role", "member"),
            wecom_user_id=body.get("wecom_user_id", ""),
            wecom_name=body.get("wecom_name", ""),
            wecom_avatar=body.get("wecom_avatar", ""),
            mobile=body.get("mobile", ""),
            department_id=body.get("department_id", "1"),
        )
        db.add(member)
        db.commit()
        db.refresh(member)
        return {
            "data": {
                "id": member.id,
                "name": member.name,
                "role": member.role,
                "wecom_user_id": member.wecom_user_id,
                "wecom_name": member.wecom_name,
                "wecom_avatar": member.wecom_avatar,
                "mobile": member.mobile,
                "department_id": member.department_id,
                "created_at": member.created_at,
                "updated_at": member.updated_at,
            },
            "error": None,
        }
    except Exception as e:
        db.rollback()
        return {"data": None, "error": str(e)}


@router.put("/members/{member_id}")
def update_member(member_id: str, body: dict, db: Session = Depends(get_db)):
    try:
        member = db.query(Member).filter(Member.id == member_id).first()
        if not member:
            return {"data": None, "error": f"Member {member_id} not found"}

        if "name" in body:
            member.name = body["name"]
        if "role" in body:
            member.role = body["role"]
        if "wecom_user_id" in body:
            # Check uniqueness
            existing = (
                db.query(Member)
                .filter(Member.wecom_user_id == body["wecom_user_id"], Member.id != member_id)
                .first()
            )
            if existing:
                return {"data": None, "error": f"wecom_user_id {body['wecom_user_id']} already exists"}
            member.wecom_user_id = body["wecom_user_id"]
        if "wecom_name" in body:
            member.wecom_name = body["wecom_name"]
        if "wecom_avatar" in body:
            member.wecom_avatar = body["wecom_avatar"]
        if "mobile" in body:
            member.mobile = body["mobile"]
        if "department_id" in body:
            member.department_id = body["department_id"]

        db.commit()
        db.refresh(member)
        return {
            "data": {
                "id": member.id,
                "name": member.name,
                "role": member.role,
                "wecom_user_id": member.wecom_user_id,
                "wecom_name": member.wecom_name,
                "wecom_avatar": member.wecom_avatar,
                "mobile": member.mobile,
                "department_id": member.department_id,
                "created_at": member.created_at,
                "updated_at": member.updated_at,
            },
            "error": None,
        }
    except Exception as e:
        db.rollback()
        return {"data": None, "error": str(e)}


@router.delete("/members/{member_id}")
def delete_member(member_id: str, db: Session = Depends(get_db)):
    try:
        member = db.query(Member).filter(Member.id == member_id).first()
        if not member:
            return {"data": None, "error": f"Member {member_id} not found"}

        # Check if member has any project permissions
        linked = db.query(ProjectPermission).filter(ProjectPermission.member_id == member_id).first()
        if linked:
            return {"data": None, "error": "Cannot delete member with existing project permissions"}

        db.delete(member)
        db.commit()
        return {"data": {"id": member_id}, "error": None}
    except Exception as e:
        db.rollback()
        return {"data": None, "error": str(e)}


@router.get("/members/{member_id}/projects")
def get_member_projects(member_id: str, db: Session = Depends(get_db)):
    try:
        member = db.query(Member).filter(Member.id == member_id).first()
        if not member:
            return {"data": None, "error": f"Member {member_id} not found"}

        perms = db.query(ProjectPermission).filter(ProjectPermission.member_id == member_id).all()
        projects = []
        for p in perms:
            proj = db.query(Project).filter(Project.id == p.project_id).first()
            if proj:
                projects.append({
                    "project_id": proj.id,
                    "project_name": proj.name,
                    "can_edit": p.can_edit,
                    "permission_id": p.id,
                })
        return {"data": projects, "error": None}
    except Exception as e:
        return {"data": None, "error": str(e)}
