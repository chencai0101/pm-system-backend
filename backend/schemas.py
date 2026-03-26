from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, Union


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    note: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    end_date: Optional[date] = None


class TaskStatusUpdate(BaseModel):
    status: str  # in-progress | review | done


class SubtaskToggle(BaseModel):
    completed: Optional[bool] = None
    title: Optional[str] = None


class SubtaskBase(BaseModel):
    id: str
    task_id: str
    title: str
    completed: bool
    completed_at: Optional[date] = None


class Subtask(SubtaskBase):
    created_at: datetime

    class Config:
        from_attributes = True


class SubtaskCreate(BaseModel):
    title: str


class TaskBase(BaseModel):
    id: str
    project_id: str
    title: str
    owner: str
    status: str
    priority: str
    start_date: date
    end_date: date
    completed_at: Optional[date] = None
    note: str = ""


class Task(TaskBase):
    subtasks: list[Subtask] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectBase(BaseModel):
    id: str
    name: str
    owner: str
    members: str = ""
    resources: str = ""
    start_date: date
    end_date: date
    status: str
    description: str = ""


class Project(ProjectBase):
    task_count: int = 0
    completed_count: int = 0
    progress: float = 0.0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ApiResponse(BaseModel):
    data: Optional[Union[dict, list]] = None
    error: Optional[str] = None


class MemberBase(BaseModel):
    name: str
    role: str = "member"
    wecom_user_id: str
    wecom_name: Optional[str] = ""
    wecom_avatar: Optional[str] = ""
    mobile: Optional[str] = ""
    department_id: Optional[str] = "1"


class MemberCreate(MemberBase):
    pass


class MemberUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    wecom_user_id: Optional[str] = None
    wecom_name: Optional[str] = None
    wecom_avatar: Optional[str] = None
    mobile: Optional[str] = None


class Member(BaseModel):
    id: str
    name: str
    role: str
    wecom_user_id: str
    wecom_name: str
    wecom_avatar: str
    mobile: str
    department_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
