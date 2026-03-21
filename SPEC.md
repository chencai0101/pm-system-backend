# 项目管理系统 v3 产品规格书（MVP）

> 基于 2026-03-21 讨论定稿
> 版本：v3.0 MVP
> 状态：规划中

---

## 一、产品定位

**一句话：** 部门重点工作全生命周期管理系统，服务于年底考核。

MVP 只做两件事：展示进度、管理任务。

---

## 二、MVP 交付范围

### 页面1：部门看板（领导/全员看）

- Notion 风格，项目卡片墙，全量平铺展示
- 白/暗双模式
- 项目卡片：名称、牵头人、截止日期（过期红色）、状态标签、进度条背景
- **纯展示，只读**，打开时拉一次数据

### 页面2：项目-任务详情（员工执行用）

- 左侧项目列表
- 右侧该项目的任务详情（看板撕裂、任务卡片、子任务勾选）
- 任务操作：编辑内容、备注（感知/反思/复盘）
- 附件挂在项目层（不做任务附件）
- 子任务可勾选，阶段一步步推进，到 Done 才算完成
- 阶段分组指标：待 My lord 确认后开发

### 不在 MVP 范围内

- 标签系统
- 参与人/权限控制
- 操作日志
- 周报
- AI 能力
- 企业微信集成

---

## 三、数据模型（MVP）

### 3.1 项目（Project）

```json
{
  "id": "P-xxx",
  "name": "重点工作名称",
  "owner": "牵头人",
  "members": ["参与人"],
  "startDate": "YYYY-MM-DD",
  "endDate": "YYYY-MM-DD",
  "progress": 0,
  "status": "未开始 | 进行中 | 已完成 | 已延期",
  "description": "",
  "createdAt": "timestamp",
  "updatedAt": "timestamp"
}
```

### 3.2 任务（Task）

```json
{
  "id": "T-xxx",
  "projectId": "P-xxx",
  "title": "任务名称",
  "owner": "责任人",
  "status": "open | in-progress | review | done",
  "priority": "low | medium | high",
  "startDate": "YYYY-MM-DD",
  "endDate": "YYYY-MM-DD",
  "completedAt": "YYYY-MM-DD | null",
  "note": "备注（感知/反思/复盘）",
  "createdAt": "timestamp",
  "updatedAt": "timestamp"
}
```

### 3.3 子任务（Subtask）

```json
{
  "id": "ST-xxx",
  "taskId": "T-xxx",
  "title": "子任务名称",
  "completed": false,
  "completedAt": "YYYY-MM-DD | null",
  "createdAt": "timestamp"
}
```

> 子任务完成后，父任务状态推进：open → in-progress → review → done

---

## 四、UI 参考

### 4.1 风格

- 参考 FlowBoard 视觉系统
- CSS Variables 实现白/暗双模式
- 大量留白、克制用色、精致阴影
- 字体：Space Grotesk + JetBrains Mono

### 4.2 任务卡片要素

```
┌──────────────────────────┐
│ T-001          [优先] [日期]│
│ 任务标题                      │
│ ████████░░░░░  3/5          │  ← 进度（子任务完成比例）
│ [备注：感知/反思...]         │
└──────────────────────────┘
```

### 4.3 看板四列

| 列 | 颜色 |
|----|------|
| Open | 灰 |
| In Progress | 黄 |
| Review | 橙 |
| Done | 绿 |

---

## 五、技术栈（MVP）

**前端**
- 框架：Vue 3 + Vite + TypeScript
- UI 库：Naive UI（参考 FlowBoard 风格定制）
- CSS Variables 白/暗切换

**后端**
- 框架：Python + FastAPI
- ORM：SQLAlchemy 2.0
- 数据验证：Pydantic v2
- 认证：JWT

**数据库**
- PostgreSQL（Docker）

**部署**
- Docker Compose，内网运行

---

## 六、技术栈待学清单

| 概念 | 笔记路径 | 状态 |
|------|---------|------|
| FastAPI | 后端开发/FastAPI/FastAPI.md | 待学 |
| PostgreSQL | 数据库/PostgreSQL/PostgreSQL.md | 待学 |

---

## 七、讨论记录

### MVP 已确认
- 页面1：部门看板（Notion 风格，白/暗双模式，四列看板）
- 页面2：项目-任务详情（左侧项目，右侧任务详情）
- 任务操作：编辑内容、备注（感知/反思）
- 附件在项目层，不在任务层
- 子任务勾选后推进父任务阶段
- MVP 先不做：标签、权限、日志、周报、AI、企业微信

### 待确认
- 页面2（项目-任务详情）的分组指标

### 待学
- FastAPI
- PostgreSQL
