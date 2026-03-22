import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database import get_db
from backend.models import Tag, Task, Project

router = APIRouter()


@router.get("/tags")
def get_tags(db: Session = Depends(get_db)):
    try:
        tags = db.query(Tag).order_by(Tag.created_at.desc()).all()
        # Count task associations via task.tags if it existed; since no direct link,
        # project_count is the primary metric. Return task_count as 0 placeholder.
        result = []
        for t in tags:
            project_count = db.query(Project).filter(
                Project.tags.any(Tag.id == t.id)
            ).count()
            result.append({
                "id": t.id,
                "name": t.name,
                "color": t.color,
                "task_count": 0,
                "project_count": project_count,
                "created_at": t.created_at,
            })
        return {"data": result, "error": None}
    except Exception as e:
        return {"data": None, "error": str(e)}


@router.post("/tags")
def create_tag(body: dict, db: Session = Depends(get_db)):
    try:
        # Unique name check
        existing = db.query(Tag).filter(Tag.name == body.get("name", "")).first()
        if existing:
            return {"data": None, "error": f"Tag '{body.get('name')}' already exists"}

        tag = Tag(
            id=uuid.uuid4().hex,
            name=body.get("name", ""),
            color=body.get("color", "blue"),
        )
        db.add(tag)
        db.commit()
        db.refresh(tag)
        return {
            "data": {
                "id": tag.id,
                "name": tag.name,
                "color": tag.color,
                "task_count": 0,
                "project_count": 0,
                "created_at": tag.created_at,
            },
            "error": None,
        }
    except Exception as e:
        db.rollback()
        return {"data": None, "error": str(e)}


@router.put("/tags/{tag_id}")
def update_tag(tag_id: str, body: dict, db: Session = Depends(get_db)):
    try:
        tag = db.query(Tag).filter(Tag.id == tag_id).first()
        if not tag:
            return {"data": None, "error": f"Tag {tag_id} not found"}

        if "name" in body:
            # Unique name check
            existing = db.query(Tag).filter(Tag.name == body["name"], Tag.id != tag_id).first()
            if existing:
                return {"data": None, "error": f"Tag '{body['name']}' already exists"}
            tag.name = body["name"]
        if "color" in body:
            tag.color = body["color"]

        db.commit()
        db.refresh(tag)
        project_count = db.query(Project).filter(
            Project.tags.any(Tag.id == tag.id)
        ).count()
        return {
            "data": {
                "id": tag.id,
                "name": tag.name,
                "color": tag.color,
                "task_count": 0,
                "project_count": project_count,
                "created_at": tag.created_at,
            },
            "error": None,
        }
    except Exception as e:
        db.rollback()
        return {"data": None, "error": str(e)}


@router.delete("/tags/{tag_id}")
def delete_tag(tag_id: str, db: Session = Depends(get_db)):
    try:
        tag = db.query(Tag).filter(Tag.id == tag_id).first()
        if not tag:
            return {"data": None, "error": f"Tag {tag_id} not found"}

        # Check project associations
        project_count = db.query(Project).filter(
            Project.tags.any(Tag.id == tag.id)
        ).count()
        if project_count > 0:
            return {
                "data": None,
                "error": f"Cannot delete tag: {project_count} project(s) are using it",
            }

        db.delete(tag)
        db.commit()
        return {"data": {"id": tag_id}, "error": None}
    except Exception as e:
        db.rollback()
        return {"data": None, "error": str(e)}
