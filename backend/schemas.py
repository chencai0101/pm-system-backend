from pydantic import BaseModel, Field
from typing import Optional, Union
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


# ── Members ──────────────────────────────────────────────────────────────────


class MemberCreate(BaseModel):
    name: str = Field(..., min_length=1)
    role: Optional[str] = Field(default="member")
    wecom_user_id: str = Field(..., min_length=1)
    wecom_name: Optional[str] = Field(default="")
    wecom_avatar: Optional[str] = Field(default="")
    mobile: Optional[str] = Field(default="")
    department_id: Optional[str] = Field(default="1")


class MemberUpdate(BaseModel):
    name: Optional[str] = Field(default=None)
    role: Optional[str] = Field(default=None)
    wecom_user_id: Optional[str] = Field(default=None)
    wecom_name: Optional[str] = Field(default=None)
    wecom_avatar: Optional[str] = Field(default=None)
    mobile: Optional[str] = Field(default=None)
    department_id: Optional[str] = Field(default=None)


class MemberResponse(BaseModel):
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


# ── Tags ─────────────────────────────────────────────────────────────────────


class TagCreate(BaseModel):
    name: str = Field(..., min_length=1)
    color: Optional[str] = Field(default="blue")


class TagUpdate(BaseModel):
    name: Optional[str] = Field(default=None)
    color: Optional[str] = Field(default=None)


class TagResponse(BaseModel):
    id: str
    name: str
    color: str
    task_count: int = 0
    project_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


# ── Permissions ───────────────────────────────────────────────────────────────


class PagePermissionUpdate(BaseModel):
    member_id: str = Field(..., min_length=1)
    page_key: str = Field(..., min_length=1)
    enabled: bool = Field(default=False)


class PagePermissionResponse(BaseModel):
    id: str
    member_id: str
    page_key: str
    enabled: bool
    member_name: Optional[str] = None

    class Config:
        from_attributes = True


class ProjectPermissionUpdate(BaseModel):
    project_id: str = Field(..., min_length=1)
    can_edit: bool = Field(default=True)


class ProjectPermissionResponse(BaseModel):
    id: str
    member_id: str
    project_id: str
    can_edit: bool
    project_name: Optional[str] = None

    class Config:
        from_attributes = True
