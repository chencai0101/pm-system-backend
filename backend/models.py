from sqlalchemy import Column, String, Date, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from backend.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    owner = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(String, default="未开始")
    description = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    title = Column(String, nullable=False)
    owner = Column(String, nullable=False)
    status = Column(String, default="open")
    priority = Column(String, default="medium")
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    completed_at = Column(Date, nullable=True)
    note = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", back_populates="tasks")
    subtasks = relationship("Subtask", back_populates="task", cascade="all, delete-orphan")


class Subtask(Base):
    __tablename__ = "subtasks"

    id = Column(String, primary_key=True)
    task_id = Column(String, ForeignKey("tasks.id"), nullable=False)
    title = Column(String, nullable=False)
    completed = Column(Boolean, default=False)
    completed_at = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    task = relationship("Task", back_populates="subtasks")


class Member(Base):
    __tablename__ = "members"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    role = Column(String, default="member")  # "admin" | "member"
    wecom_user_id = Column(String, unique=True, nullable=False)
    wecom_name = Column(String, default="")
    wecom_avatar = Column(String, default="")
    mobile = Column(String, default="")
    department_id = Column(String, default="1")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ProjectPermission(Base):
    __tablename__ = "project_permissions"

    id = Column(String, primary_key=True)
    member_id = Column(String, ForeignKey("members.id"), nullable=False)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    can_edit = Column(Boolean, default=True)
    member = relationship("Member")
    project = relationship("Project")
