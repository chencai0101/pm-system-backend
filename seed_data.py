"""Seed data script for pm-system-backend MVP."""

from datetime import date, datetime, timedelta
from backend.database import SessionLocal, init_db
from backend.models import Project, Task, Subtask

init_db()
db = SessionLocal()

# Clear existing data
db.query(Subtask).delete()
db.query(Task).delete()
db.query(Project).delete()
db.commit()

today = date.today()

projects_data = [
    {
        "id": "P-001",
        "name": "部门数字化转型项目",
        "owner": "张明",
        "start_date": today,
        "end_date": today + timedelta(days=90),
        "status": "进行中",
        "description": "推动部门业务流程数字化，提升运营效率。",
    },
    {
        "id": "P-002",
        "name": "年度考核系统优化",
        "owner": "李华",
        "start_date": today,
        "end_date": today + timedelta(days=60),
        "status": "进行中",
        "description": "优化年度考核流程，实现自动化评分。",
    },
    {
        "id": "P-003",
        "name": "知识库建设",
        "owner": "王芳",
        "start_date": today - timedelta(days=10),
        "end_date": today + timedelta(days=45),
        "status": "未开始",
        "description": "搭建部门知识库，实现经验沉淀与共享。",
    },
    {
        "id": "P-004",
        "name": "培训体系建设",
        "owner": "赵强",
        "start_date": today - timedelta(days=30),
        "end_date": today + timedelta(days=20),
        "status": "已完成",
        "description": "建立新员工培训体系与在职提升计划。",
    },
    {
        "id": "P-005",
        "name": "内部协作平台升级",
        "owner": "陈晨",
        "start_date": today,
        "end_date": today + timedelta(days=120),
        "status": "已延期",
        "description": "升级协作平台功能，打通信息孤岛。",
    },
]

tasks_data = [
    # P-001 tasks
    {
        "id": "T-001",
        "project_id": "P-001",
        "title": "流程现状调研",
        "owner": "张明",
        "status": "done",
        "priority": "high",
        "start_date": today,
        "end_date": today + timedelta(days=14),
        "completed_at": today - timedelta(days=5),
        "note": "已完成调研报告，发现3个关键瓶颈。",
    },
    {
        "id": "T-002",
        "project_id": "P-001",
        "title": "数字化方案设计",
        "owner": "刘伟",
        "status": "in-progress",
        "priority": "high",
        "start_date": today - timedelta(days=5),
        "end_date": today + timedelta(days=30),
        "completed_at": None,
        "note": "方案初稿已完成，正在内部评审。",
    },
    {
        "id": "T-003",
        "project_id": "P-001",
        "title": "供应商选型",
        "owner": "张明",
        "status": "open",
        "priority": "medium",
        "start_date": today + timedelta(days=30),
        "end_date": today + timedelta(days=60),
        "completed_at": None,
        "note": "",
    },
    {
        "id": "T-004",
        "project_id": "P-001",
        "title": "系统实施与部署",
        "owner": "刘伟",
        "status": "open",
        "priority": "high",
        "start_date": today + timedelta(days=60),
        "end_date": today + timedelta(days=90),
        "completed_at": None,
        "note": "",
    },
    # P-002 tasks
    {
        "id": "T-005",
        "project_id": "P-002",
        "title": "需求收集与整理",
        "owner": "李华",
        "status": "done",
        "priority": "high",
        "start_date": today,
        "end_date": today + timedelta(days=10),
        "completed_at": today - timedelta(days=3),
        "note": "收集了12个部门的考核需求。",
    },
    {
        "id": "T-006",
        "project_id": "P-002",
        "title": "考核指标体系设计",
        "owner": "李华",
        "status": "review",
        "priority": "high",
        "start_date": today - timedelta(days=3),
        "end_date": today + timedelta(days=20),
        "completed_at": None,
        "note": "指标体系已出第二版，待领导确认。",
    },
    {
        "id": "T-007",
        "project_id": "P-002",
        "title": "评分算法开发",
        "owner": "孙鹏",
        "status": "open",
        "priority": "medium",
        "start_date": today + timedelta(days=20),
        "end_date": today + timedelta(days=45),
        "completed_at": None,
        "note": "",
    },
    # P-003 tasks
    {
        "id": "T-008",
        "project_id": "P-003",
        "title": "知识分类体系设计",
        "owner": "王芳",
        "status": "open",
        "priority": "medium",
        "start_date": today,
        "end_date": today + timedelta(days=15),
        "completed_at": None,
        "note": "",
    },
    {
        "id": "T-009",
        "project_id": "P-003",
        "title": "平台选型",
        "owner": "王芳",
        "status": "open",
        "priority": "low",
        "start_date": today + timedelta(days=15),
        "end_date": today + timedelta(days=30),
        "completed_at": None,
        "note": "",
    },
    {
        "id": "T-010",
        "project_id": "P-003",
        "title": "内容迁移",
        "owner": "周琳",
        "status": "open",
        "priority": "low",
        "start_date": today + timedelta(days=30),
        "end_date": today + timedelta(days=45),
        "completed_at": None,
        "note": "",
    },
    # P-004 tasks
    {
        "id": "T-011",
        "project_id": "P-004",
        "title": "培训课程设计",
        "owner": "赵强",
        "status": "done",
        "priority": "high",
        "start_date": today - timedelta(days=30),
        "end_date": today - timedelta(days=15),
        "completed_at": today - timedelta(days=15),
        "note": "设计了12门入职培训课程。",
    },
    {
        "id": "T-012",
        "project_id": "P-004",
        "title": "培训讲师招募",
        "owner": "赵强",
        "status": "done",
        "priority": "medium",
        "start_date": today - timedelta(days=15),
        "end_date": today - timedelta(days=5),
        "completed_at": today - timedelta(days=5),
        "note": "招募了8名内部讲师。",
    },
    {
        "id": "T-013",
        "project_id": "P-004",
        "title": "试讲与反馈",
        "owner": "赵强",
        "status": "done",
        "priority": "high",
        "start_date": today - timedelta(days=5),
        "end_date": today + timedelta(days=5),
        "completed_at": today - timedelta(days=1),
        "note": "试讲完成，满意度评分4.8/5。",
    },
    # P-005 tasks
    {
        "id": "T-014",
        "project_id": "P-005",
        "title": "需求调研",
        "owner": "陈晨",
        "status": "done",
        "priority": "high",
        "start_date": today - timedelta(days=60),
        "end_date": today - timedelta(days=40),
        "completed_at": today - timedelta(days=40),
        "note": "调研了各部门的协作痛点。",
    },
    {
        "id": "T-015",
        "project_id": "P-005",
        "title": "技术方案设计",
        "owner": "陈晨",
        "status": "in-progress",
        "priority": "high",
        "start_date": today - timedelta(days=40),
        "end_date": today + timedelta(days=20),
        "completed_at": None,
        "note": "因架构调整，设计方案延期两次。",
    },
    {
        "id": "T-016",
        "project_id": "P-005",
        "title": "平台开发",
        "owner": "吴涛",
        "status": "open",
        "priority": "high",
        "start_date": today + timedelta(days=20),
        "end_date": today + timedelta(days=80),
        "completed_at": None,
        "note": "",
    },
    {
        "id": "T-017",
        "project_id": "P-005",
        "title": "UAT 测试",
        "owner": "陈晨",
        "status": "open",
        "priority": "medium",
        "start_date": today + timedelta(days=80),
        "end_date": today + timedelta(days=100),
        "completed_at": None,
        "note": "",
    },
    {
        "id": "T-018",
        "project_id": "P-005",
        "title": "上线与推广",
        "owner": "陈晨",
        "status": "open",
        "priority": "medium",
        "start_date": today + timedelta(days=100),
        "end_date": today + timedelta(days=120),
        "completed_at": None,
        "note": "",
    },
]

subtasks_data = [
    # T-001 subtasks
    {"id": "ST-001", "task_id": "T-001", "title": "访谈部门负责人", "completed": True, "completed_at": today - timedelta(days=10)},
    {"id": "ST-002", "task_id": "T-001", "title": "收集现有流程文档", "completed": True, "completed_at": today - timedelta(days=8)},
    {"id": "ST-003", "task_id": "T-001", "title": "绘制流程图", "completed": True, "completed_at": today - timedelta(days=5)},
    {"id": "ST-004", "task_id": "T-001", "title": "输出调研报告", "completed": True, "completed_at": today - timedelta(days=3)},
    # T-002 subtasks
    {"id": "ST-005", "task_id": "T-002", "title": "方案架构设计", "completed": True, "completed_at": today - timedelta(days=2)},
    {"id": "ST-006", "task_id": "T-002", "title": "详细方案撰写", "completed": True, "completed_at": today - timedelta(days=1)},
    {"id": "ST-007", "task_id": "T-002", "title": "内部评审", "completed": False, "completed_at": None},
    {"id": "ST-008", "task_id": "T-002", "title": "方案定稿", "completed": False, "completed_at": None},
    # T-006 subtasks
    {"id": "ST-009", "task_id": "T-006", "title": "梳理考核维度", "completed": True, "completed_at": today - timedelta(days=5)},
    {"id": "ST-010", "task_id": "T-006", "title": "设计权重体系", "completed": True, "completed_at": today - timedelta(days=3)},
    {"id": "ST-011", "task_id": "T-006", "title": "领导评审", "completed": False, "completed_at": None},
    # T-011 subtasks
    {"id": "ST-012", "task_id": "T-011", "title": "课程大纲设计", "completed": True, "completed_at": today - timedelta(days=25)},
    {"id": "ST-013", "task_id": "T-011", "title": "PPT 制作", "completed": True, "completed_at": today - timedelta(days=20)},
    {"id": "ST-014", "task_id": "T-011", "title": "案例整理", "completed": True, "completed_at": today - timedelta(days=15)},
    # T-015 subtasks
    {"id": "ST-015", "task_id": "T-015", "title": "技术选型", "completed": True, "completed_at": today - timedelta(days=20)},
    {"id": "ST-016", "task_id": "T-015", "title": "架构设计", "completed": True, "completed_at": today - timedelta(days=10)},
    {"id": "ST-017", "task_id": "T-015", "title": "接口设计", "completed": False, "completed_at": None},
    {"id": "ST-018", "task_id": "T-015", "title": "评审修订", "completed": False, "completed_at": None},
]

print("Seeding projects...")
for p in projects_data:
    db.add(Project(**p))
db.commit()

print("Seeding tasks...")
for t in tasks_data:
    db.add(Task(**t))
db.commit()

print("Seeding subtasks...")
for s in subtasks_data:
    db.add(Subtask(**s))
db.commit()

print(f"✅ Done: {len(projects_data)} projects, {len(tasks_data)} tasks, {len(subtasks_data)} subtasks inserted.")

db.close()
