from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Task, Project
from datetime import date, datetime, timedelta
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter(tags=["weekly-report"])


def get_week_range(week_offset: int = 0) -> tuple[date, date]:
    """
    返回指定周的周一和周日日期。
    week_offset=0: 上周 (即本周已过完的那一周)
    week_offset=-1: 再上周
    例如 2026-03-26 (周四) → week_offset=0 → (2026-03-17, 2026-03-23)
    """
    today = date.today()
    # 计算当前是周几 (0=周一, 6=周日)
    days_since_monday = today.weekday()
    # 找到本周一
    this_monday = today - timedelta(days=days_since_monday)
    # 目标周一 = 本周一 + (week_offset - 1) 周
    # week_offset=0 → 上周一 → this_monday - 7
    target_monday = this_monday + timedelta(weeks=week_offset - 1)
    target_sunday = target_monday + timedelta(days=6)
    return target_monday, target_sunday


def get_task_progress_pct(task: Task) -> float:
    """根据 subtasks 计算任务进度百分比"""
    subtasks = task.subtasks or []
    if not subtasks:
        # 无 subtask 时，用 status 估算
        if task.status == "done":
            return 100.0
        elif task.status == "in-progress":
            return 50.0
        elif task.status == "review":
            return 75.0
        return 0.0
    done = sum(1 for s in subtasks if s.completed)
    return round(done / len(subtasks) * 100, 1)


# ── Response Models ──────────────────────────────────

class AlertTask(BaseModel):
    id: str
    project_id: str
    project_name: str
    tags: List[str]
    task_title: str
    owner: str
    days_left: int  # 负数表示已延期
    overdue: bool
    end_date: date

    class Config:
        from_attributes = True


class DoneTaskItem(BaseModel):
    id: str
    title: str
    completed_date: str

    class Config:
        from_attributes = True


class RunningTaskItem(BaseModel):
    id: str
    title: str
    progress_pct: float

    class Config:
        from_attributes = True


class ProjectProgress(BaseModel):
    id: str
    project_name: str
    tags: List[str]
    owner: str
    progress_pct: float
    done_count: int
    total_count: int
    done_tasks: List[DoneTaskItem]
    running_tasks: List[RunningTaskItem]
    note: Optional[str] = ""

    class Config:
        from_attributes = True


class RecentTask(BaseModel):
    id: str
    project_id: str
    project_name: str
    tags: List[str]
    task_title: str
    owner: str
    created_date: str

    class Config:
        from_attributes = True


class WeeklyReportResponse(BaseModel):
    week_label: str
    week_start: date
    week_end: date
    alerts: List[AlertTask]
    progress: List[ProjectProgress]
    recent: List[RecentTask]


# ── Endpoint ─────────────────────────────────────────

@router.get("/weekly-report", response_model=WeeklyReportResponse)
def get_weekly_report(week_offset: int = 0, db: Session = Depends(get_db)):
    """
    获取周报数据。
    week_offset=0 → 上周（本周已过的完整一周）
    week_offset=-1 → 再上周，以此类推
    """
    week_start, week_end = get_week_range(week_offset)
    today = date.today()

    # ── 预期（即将逾期 + 已延期）───────────────────────
    # 条件：在进行中的任务（非done），截止日期 ≤ 7天内 或 已到期
    alert_tasks = (
        db.query(Task)
        .filter(Task.status != "done")
        .filter(Task.end_date <= week_end + timedelta(days=7))
        .filter(Task.end_date >= (today - timedelta(days=30)))  # 避免拉太远
        .order_by(Task.end_date.asc())
        .all()
    )

    alerts = []
    for t in alert_tasks:
        project = db.query(Project).filter(Project.id == t.project_id).first()
        days_left = (t.end_date - today).days
        alerts.append(AlertTask(
            id=t.id,
            project_id=t.project_id,
            project_name=project.name if project else "",
            tags=[],  # TODO: tag model 尚未接入
            task_title=t.title,
            owner=t.owner,
            days_left=days_left,
            overdue=days_left < 0,
            end_date=t.end_date,
        ))

    # ── 进展（按项目聚合本周完成 + 进行中）─────────────
    # 找出本周有完成任务的项目
    done_tasks_this_week = (
        db.query(Task)
        .filter(Task.completed_at >= week_start)
        .filter(Task.completed_at <= week_end)
        .filter(Task.status == "done")
        .all()
    )

    # 按 project_id 分组
    done_project_ids = set(t.project_id for t in done_tasks_this_week)

    # 同时纳入有进行中任务的项目（在该周有活动且未完成的）
    running_tasks = (
        db.query(Task)
        .filter(Task.status.in_(["in-progress", "review", "open"]))
        .filter(Task.start_date <= week_end)                           # 本周已经开始
        .filter(Task.end_date >= week_start)                           # 本周还没截止
        .filter(
            (Task.completed_at.is_(None)) | (Task.completed_at > week_end)  # 未在周前完成
        )
        .all()
    )
    running_project_ids = set(t.project_id for t in running_tasks)

    # 合并：有完成或有进行中任务的项目
    relevant_project_ids = done_project_ids | running_project_ids

    progress_projects = []
    for pid in relevant_project_ids:
        project = db.query(Project).filter(Project.id == pid).first()
        if not project:
            continue

        all_tasks = db.query(Task).filter(Task.project_id == pid).all()
        done_in_week = [
            t for t in all_tasks
            if t.status == "done"
            and t.completed_at
            and week_start <= t.completed_at <= week_end
        ]
        running = [
            t for t in all_tasks
            if t.status in ("in-progress", "review", "open")
            and t.start_date <= week_end                           # 本周已经开始
            and t.end_date >= week_start                          # 本周还没截止
            and (t.completed_at is None or t.completed_at > week_end)  # 未在周前完成
        ]

        # 整体进度 = 本周已完成 / 总任务数
        total = len(all_tasks)
        done_count = len(done_in_week)
        overall_pct = round(done_count / total * 100, 1) if total > 0 else 0.0

        done_items = [
            DoneTaskItem(
                id=t.id,
                title=t.title,
                completed_date=t.completed_at.strftime("%m/%d") if t.completed_at else "",
            )
            for t in done_in_week
        ]

        running_items = [
            RunningTaskItem(
                id=t.id,
                title=t.title,
                progress_pct=get_task_progress_pct(t),
            )
            for t in running
        ]

        progress_projects.append(ProjectProgress(
            id=project.id,
            project_name=project.name,
            tags=[],  # TODO: tag model 尚未接入
            owner=project.owner,
            progress_pct=overall_pct,
            done_count=done_count,
            total_count=total,
            done_tasks=done_items,
            running_tasks=running_items,
            note="",
        ))

    # 按项目进度降序排列
    progress_projects.sort(key=lambda x: x.progress_pct, reverse=True)

    # ── 新增（本周新建的任务）─────────────────────────
    recent_tasks = (
        db.query(Task)
        .filter(Task.created_at >= datetime.combine(week_start, datetime.min.time()))
        .filter(Task.created_at <= datetime.combine(week_end, datetime.max.time()))
        .order_by(Task.created_at.desc())
        .all()
    )

    recent = []
    for t in recent_tasks:
        project = db.query(Project).filter(Project.id == t.project_id).first()
        recent.append(RecentTask(
            id=t.id,
            project_id=t.project_id,
            project_name=project.name if project else "",
            tags=[],
            task_title=t.title,
            owner=t.owner,
            created_date=t.created_at.strftime("%m/%d"),
        ))

    # 周标签
    week_num = week_start.isocalendar()[1]
    week_label = f"{week_start.year}年第{week_num}周（{week_start.strftime('%m/%d')} - {week_end.strftime('%m/%d')}）"

    return WeeklyReportResponse(
        week_label=week_label,
        week_start=week_start,
        week_end=week_end,
        alerts=alerts,
        progress=progress_projects,
        recent=recent,
    )
