from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date

from backend.database import get_db
from backend.models import Task, Subtask
from backend.schemas import ApiResponse, TaskUpdate, TaskStatusUpdate, SubtaskToggle

router = APIRouter()


def _build_task_response(t: Task, db: Session) -> dict:
    """Build a full task dict including subtasks."""
    db.expire_all()  # Ensure session sees latest committed data
    subtasks = db.query(Subtask).filter(Subtask.task_id == t.id).all()
    return {
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
        "subtasks": [
            {
                "id": s.id,
                "task_id": s.task_id,
                "title": s.title,
                "completed": s.completed,
                "completed_at": s.completed_at,
                "created_at": s.created_at,
            }
            for s in subtasks
        ],
        "created_at": t.created_at,
        "updated_at": t.updated_at,
    }


@router.get("/tasks")
def get_tasks(db: Session = Depends(get_db)):
    try:
        db_tasks = db.query(Task).all()
        return {"data": [_build_task_response(t, db) for t in db_tasks], "error": None}
    except Exception as e:
        return {"data": None, "error": str(e)}


# T-010: PATCH /api/tasks/{task_id} — 更新任务内容、备注、状态、优先级、截止日期
@router.patch("/tasks/{task_id}")
def update_task(task_id: str, body: TaskUpdate, db: Session = Depends(get_db)):
    try:
        t = db.query(Task).filter(Task.id == task_id).first()
        if not t:
            return {"data": None, "error": f"Task {task_id} not found"}

        if body.title is not None:
            t.title = body.title
        if body.note is not None:
            t.note = body.note
        if body.status is not None:
            t.status = body.status
        if body.priority is not None:
            t.priority = body.priority
        if body.end_date is not None:
            t.end_date = body.end_date

        db.commit()
        db.refresh(t)
        return {"data": _build_task_response(t, db), "error": None}
    except Exception as e:
        db.rollback()
        return {"data": None, "error": str(e)}


# T-011: PATCH /api/tasks/{task_id}/status — 推进任务阶段
@router.patch("/tasks/{task_id}/status")
def advance_task_status(task_id: str, body: TaskStatusUpdate, db: Session = Depends(get_db)):
    try:
        t = db.query(Task).filter(Task.id == task_id).first()
        if not t:
            return {"data": None, "error": f"Task {task_id} not found"}

        t.status = body.status
        if body.status == "done":
            t.completed_at = date.today()

        db.commit()
        db.refresh(t)
        return {"data": _build_task_response(t, db), "error": None}
    except Exception as e:
        db.rollback()
        return {"data": None, "error": str(e)}


# T-012: PATCH /api/subtasks/{subtask_id} — 勾选/取消子任务
# POST /api/tasks/{task_id}/subtasks — 新建子任务
@router.post("/tasks/{task_id}/subtasks")
def create_subtask(task_id: str, body: dict, db: Session = Depends(get_db)):
    try:
        t = db.query(Task).filter(Task.id == task_id).first()
        if not t:
            return {"data": None, "error": f"Task {task_id} not found"}

        import re
        all_ids = db.query(Subtask.id).all()
        max_num = 0
        for (sid,) in all_ids:
            m = re.match(r'ST-(\d+)', sid)
            if m: max_num = max(max_num, int(m.group(1)))
        subtask_id = f"ST-{max_num + 1:03d}"
        new_subtask = Subtask(
            id=subtask_id,
            task_id=task_id,
            title=body.get("title", ""),
            completed=False,
        )
        db.add(new_subtask)
        db.commit()
        db.refresh(new_subtask)
        return {"data": _build_task_response(t, db), "error": None}
    except Exception as e:
        db.rollback()
        return {"data": None, "error": str(e)}


# DELETE /api/subtasks/{subtask_id} — 删除子任务
@router.delete("/subtasks/{subtask_id}")
def delete_subtask(subtask_id: str, db: Session = Depends(get_db)):
    try:
        s = db.query(Subtask).filter(Subtask.id == subtask_id).first()
        if not s:
            return {"data": None, "error": f"Subtask {subtask_id} not found"}

        task_id = s.task_id
        db.delete(s)
        db.commit()

        t = db.query(Task).filter(Task.id == task_id).first()
        return {"data": _build_task_response(t, db) if t else None, "error": None}
    except Exception as e:
        db.rollback()
        return {"data": None, "error": str(e)}


@router.patch("/subtasks/{subtask_id}")
def update_subtask(subtask_id: str, body: SubtaskToggle, db: Session = Depends(get_db)):
    try:
        s = db.query(Subtask).filter(Subtask.id == subtask_id).first()
        if not s:
            return {"data": None, "error": f"Subtask {subtask_id} not found"}

        if body.title is not None:
            s.title = body.title

        if body.completed is not None:
            s.completed = body.completed
            if body.completed:
                s.completed_at = date.today()
            else:
                s.completed_at = None

        db.commit()

        # 自动推进父任务状态（仅当所有 subtask 都 completed 时）
        if body.completed:
            t = db.query(Task).filter(Task.id == s.task_id).first()
            if t:
                all_subtasks = db.query(Subtask).filter(Subtask.task_id == t.id).all()
                if all(st.completed for st in all_subtasks):
                    status_order = ["open", "in-progress", "review", "done"]
                    if t.status in status_order:
                        idx = status_order.index(t.status)
                        if idx < len(status_order) - 1:
                            t.status = status_order[idx + 1]
                            if t.status == "done":
                                t.completed_at = date.today()
                            db.commit()

        db.refresh(s)
        t = db.query(Task).filter(Task.id == s.task_id).first()
        return {"data": _build_task_response(t, db), "error": None}
    except Exception as e:
        db.rollback()
        return {"data": None, "error": str(e)}
