from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import uuid

from backend.database import get_db
from backend.models import Member
from backend.schemas import MemberCreate, MemberUpdate

router = APIRouter()


def member_to_dict(m: Member) -> dict:
    return {
        "id": m.id,
        "name": m.name,
        "role": m.role,
        "wecom_user_id": m.wecom_user_id,
        "wecom_name": m.wecom_name or "",
        "wecom_avatar": m.wecom_avatar or "",
        "mobile": m.mobile or "",
        "department_id": m.department_id,
        "created_at": m.created_at,
        "updated_at": m.updated_at,
    }


@router.get("/members")
def get_members(name: str = "", db: Session = Depends(get_db)):
    """List members, optionally filter by name (fuzzy search)."""
    try:
        query = db.query(Member)
        if name:
            query = query.filter(Member.name.contains(name))
        members = query.order_by(Member.created_at.desc()).all()
        return {"data": [member_to_dict(m) for m in members], "error": None}
    except Exception as e:
        return {"data": None, "error": str(e)}


@router.post("/members")
def create_member(body: MemberCreate, db: Session = Depends(get_db)):
    """Create a new member. wecom_user_id must be unique."""
    try:
        # Check uniqueness of wecom_user_id
        existing = db.query(Member).filter(Member.wecom_user_id == body.wecom_user_id).first()
        if existing:
            return {"data": None, "error": f"wecom_user_id '{body.wecom_user_id}' already exists"}

        member = Member(
            id=uuid.uuid4().hex,
            name=body.name,
            role=body.role,
            wecom_user_id=body.wecom_user_id,
            wecom_name=body.wecom_name or "",
            wecom_avatar=body.wecom_avatar or "",
            mobile=body.mobile or "",
            department_id=body.department_id or "1",
        )
        db.add(member)
        db.commit()
        db.refresh(member)
        return {"data": member_to_dict(member), "error": None}
    except Exception as e:
        db.rollback()
        return {"data": None, "error": str(e)}


@router.put("/members/{member_id}")
def update_member(member_id: str, body: MemberUpdate, db: Session = Depends(get_db)):
    """Update a member's fields."""
    try:
        member = db.query(Member).filter(Member.id == member_id).first()
        if not member:
            return {"data": None, "error": f"Member {member_id} not found"}

        if body.name is not None:
            member.name = body.name
        if body.role is not None:
            member.role = body.role
        if body.wecom_user_id is not None:
            # Check uniqueness
            existing = (
                db.query(Member)
                .filter(Member.wecom_user_id == body.wecom_user_id, Member.id != member_id)
                .first()
            )
            if existing:
                return {"data": None, "error": f"wecom_user_id '{body.wecom_user_id}' already taken"}
            member.wecom_user_id = body.wecom_user_id
        if body.wecom_name is not None:
            member.wecom_name = body.wecom_name
        if body.wecom_avatar is not None:
            member.wecom_avatar = body.wecom_avatar
        if body.mobile is not None:
            member.mobile = body.mobile

        db.commit()
        db.refresh(member)
        return {"data": member_to_dict(member), "error": None}
    except Exception as e:
        db.rollback()
        return {"data": None, "error": str(e)}


@router.delete("/members/{member_id}")
def delete_member(member_id: str, db: Session = Depends(get_db)):
    """Delete a member. Returns error if member has associated project permissions."""
    try:
        member = db.query(Member).filter(Member.id == member_id).first()
        if not member:
            return {"data": None, "error": f"Member {member_id} not found"}

        db.delete(member)
        db.commit()
        return {"data": {"deleted": member_id}, "error": None}
    except Exception as e:
        db.rollback()
        return {"data": None, "error": str(e)}


@router.get("/members/{member_id}/projects")
def get_member_projects(member_id: str, db: Session = Depends(get_db)):
    """Return projects associated with this member via project_permissions."""
    try:
        from backend.models import ProjectPermission, Project
        perms = (
            db.query(ProjectPermission)
            .filter(ProjectPermission.member_id == member_id)
            .all()
        )
        projects = []
        for p in perms:
            proj = db.query(Project).filter(Project.id == p.project_id).first()
            if proj:
                projects.append({
                    "id": proj.id,
                    "name": proj.name,
                    "can_edit": p.can_edit,
                })
        return {"data": projects, "error": None}
    except Exception as e:
        return {"data": None, "error": str(e)}
