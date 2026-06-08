# 实施计划：Flask 单体架构迁移（PR 1 / 骨架 + 活动 + 报名）

> **计划版本**：v1.0
> **编写日期**：2026-06-08
> **编写人**：SOLO Coder
> **关联 PRD**：[event-registration-prd.md §7 技术选型](../design/event-registration-prd.md)
> **关联决策**：截图（2026-06-08）—— 前后端统一用 Flask，MySQL + pymysql，静态资源本地

---

## 1. 目标与边界

### 1.1 本 PR 目标

把项目从「React + Vite + NestJS + PostgreSQL + Prisma + OBS」改为 **「Flask + Jinja2 + MySQL（pymysql）+ 本地 static/」**，并跑通「脚手架 + 假账号 + 活动 CRUD + 报名主流程」一条最小主线。

### 1.2 明确不做（留给后续 PR）

- 微信扫码 / 手机号验证码 / 短信 / 邮件通知
- 签到（自报二维码 / 扫群码 / 手机后 4 位）
- 组织两级树
- region 多区域
- 平台运营后台 / 活动模板市场
- 数据导出（Excel/CSV）
- 邀请码 / 队伍报名

### 1.3 后续 PR 排期（草案，需评审）

| PR | 主题 | 预计时间 |
| --- | --- | --- |
| **PR 1（本次）** | 骨架 + 假账号 + 活动 CRUD + 报名 | 1 天 |
| PR 2 | 组织两级树 + 组织成员邀请 | 0.5 天 |
| PR 3 | 微信扫码登录 + 手机号验证码 | 1 天 |
| PR 4 | 通知渠道（邮件 + 微信服务通知 + 短信） | 1 天 |
| PR 5 | 三种签到方式 | 1 天 |
| PR 6 | 数据导出 + 平台运营后台 + 模板 | 1.5 天 |

---

## 2. 技术决策与理由

| 决策点 | 选型 | 理由 |
| --- | --- | --- |
| Web 框架 | **Flask 3.x** | 用户指定；单体简单、模板原生 |
| 模板 | **Jinja2**（Flask 内置） | 用户指定，无需前后端分离 |
| 数据库 | **MySQL 8**（docker） | 用户指定；运维简单、广泛使用 |
| 驱动 | **PyMySQL** | 用户指定；纯 Python，无 C 扩展依赖 |
| ORM | **Flask-SQLAlchemy 3.x** | 团队熟悉、迁移工具有 `flask-migrate`（Alembic） |
| 登录 | **Flask-Login + session** | 假账号阶段够用，后续接入真实登录只改 `auth/` 蓝图 |
| 配置 | **python-dotenv + .env** | 12-factor；密钥不入库 |
| 表单 | **Flask-WTF**（WTForms） | 简单表单 + CSRF 防护 |
| 端口 | **8080** | 用户指定，绑定后不变 |
| 静态资源 | **本地 `app/static/`** | 用户指定；首期不接 OBS |
| 测试 | **pytest + pytest-flask** | 行业标准 |
| 容器 | **docker-compose**（仅 MySQL 服务） | 一键拉起本地库；应用本身 `flask run` |

> **关于 ORM 的补充说明**：用户指定「用 pymysql 库进行链接」。PyMySQL 是 DB-API 驱动，本身不是 ORM。本计划用 `PyMySQL` 作为驱动 + SQLAlchemy 作为 ORM，两者并存不冲突。如果团队坚持「不要 ORM，纯 SQL」，请在 PR Review 时指出，我会删掉 SQLAlchemy 仅留 PyMySQL。

---

## 3. 目录结构

```
活动报名平台/
├── app/
│   ├── __init__.py            # create_app 工厂
│   ├── config.py              # 配置类（Dev / Test / Prod）
│   ├── extensions.py          # db / login_manager 等扩展
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py            # User 模型
│   │   ├── activity.py        # Activity 模型
│   │   └── registration.py    # Registration 模型
│   ├── blueprints/
│   │   ├── __init__.py
│   │   ├── main.py            # 首页
│   │   ├── auth.py            # 假账号登录/登出
│   │   ├── activity.py        # 活动 CRUD
│   │   └── registration.py    # 报名
│   ├── templates/             # Jinja2 模板
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── auth/login.html
│   │   ├── activity/
│   │   │   ├── list.html
│   │   │   ├── detail.html
│   │   │   ├── create.html
│   │   │   └── edit.html
│   │   └── registration/
│   │       ├── new.html
│   │       └── ticket.html
│   └── static/
│       ├── css/style.css
│       └── images/
├── migrations/                # flask-migrate 输出
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_activity.py
│   └── test_registration.py
├── wsgi.py
├── requirements.txt
├── .env.example
├── .gitignore
├── docker-compose.yml         # 仅 MySQL 服务
├── pytest.ini
└── docs/
    └── plans/flask-migration.md   # 本文档
```

---

## 4. 数据模型（仅本轮）

```python
# User
id, username(unique), password_hash, is_admin, created_at

# Activity
id, title, description, cover_image, location, start_time, end_time,
registration_start, registration_end, capacity, status(草稿/上架/下架),
created_by_id(FK→User), created_at, updated_at

# Registration
id, activity_id(FK), user_id(FK), name, phone, company, position,
form_data(JSON), status(待审核/已通过/已拒绝/已签到/已取消),
ticket_code(unique), created_at
```

> `form_data` 存自定义表单答案（PRD 5.4）。本轮先不开放自定义字段，预置 4 个固定字段（name/phone/company/position），后续 PR 升级。

---

## 5. 路由清单

| Method | Path | View | 权限 |
| --- | --- | --- | --- |
| GET | `/` | 首页：活动列表 | 游客 |
| GET | `/activity/` | 活动列表 | 游客 |
| GET | `/activity/<id>` | 活动详情 | 游客 |
| GET/POST | `/activity/new` | 创建活动 | 假账号 |
| GET/POST | `/activity/<id>/edit` | 编辑活动 | 假账号 |
| POST | `/activity/<id>/delete` | 删除活动 | 假账号 |
| GET/POST | `/registration/new/<activity_id>` | 填写报名表 | 假账号 |
| GET | `/registration/<id>/ticket` | 电子票页 | 假账号 |
| GET/POST | `/auth/login` | 登录 | 游客 |
| GET | `/auth/logout` | 登出 | 假账号 |

---

## 6. TDD 任务拆解

> **先 RED 再 GREEN**。每个测试在实现前先写出来，运行确认失败，再写代码让它通过。

### 6.1 必写测试用例（≥ 5 个）

1. `test_auth.py::test_login_success` — 假账号 admin/admin 能登录并跳转
2. `test_auth.py::test_login_failure` — 错误密码不能登录
3. `test_activity.py::test_create_activity` — 登录后 POST 创建活动，成功入库
4. `test_activity.py::test_list_activity` — 活动列表展示
5. `test_registration.py::test_submit_registration` — 报名提交后入库并跳转电子票页
6. `test_registration.py::test_duplicate_registration_forbidden` — 同一用户对同一活动不能重复报名
7. `test_registration.py::test_ticket_page_shows_qr` — 电子票页能渲染（QR 用占位文本）

### 6.2 RED 阶段产物

```
$ pytest
collected 7 items
tests/test_auth.py FF
tests/test_activity.py FF
tests/test_registration.py FFF
```

### 6.3 GREEN 阶段产物

```
$ pytest
collected 7 items
tests/ .......                                                       [100%]
7 passed in 1.23s
```

---

## 7. 验收清单

- [ ] `docker compose up -d` 能拉起 MySQL 8
- [ ] `flask db upgrade` 能创建所有表
- [ ] `flask run --port=8080` 启动后浏览器能打开 http://localhost:8080
- [ ] 假账号 admin/admin 能登录
- [ ] 能创建、编辑、删除活动
- [ ] 游客能浏览活动列表和详情
- [ ] 登录后能报名，看到电子票页（含 ticket_code）
- [ ] 同一用户对同一活动重复报名被拒绝
- [ ] `pytest` 7 条全绿
- [ ] 所有函数有中文注释
- [ ] 函数创建和调用参数名一致、参数完整
- [ ] `.env` 不入库，`.env.example` 入库

---

## 8. 风险与回滚

| 风险 | 缓解 |
| --- | --- |
| 团队成员本机已装了 MySQL 占用 3306 | docker-compose 暴露端口改为 `3307:3306`，.env.example 同步 |
| pymysql 编码问题 | 连接串加 `?charset=utf8mb4` |
| flask-migrate 升级失败 | 提供 `flask db stamp head` + `flask db migrate` 重置流程 |
| 大文件入 Git | `.gitignore` 增加 `__pycache__/` `.env` `instance/` `.venv/` |
| 端口 8080 被占用 | `flask run --port=8080` 启动前 `netstat -ano | findstr :8080` 检测 |

---

## 9. 进度占比

| 阶段 | 占比 | 状态 |
| --- | --- | --- |
| 头脑风暴 | 1/7 | ✅ 完成 |
| 写计划 | 2/7 | 🟡 进行中（本文档） |
| 创建 worktree | 3/7 | ⏳ 待开始 |
| RED（写测试） | 4/7 | ⏳ 待开始 |
| GREEN（写实现） | 5/7 | ⏳ 待开始 |
| 更新项目规则 | 6/7 | ⏳ 待开始 |
| 提交 PR | 7/7 | ⏳ 待开始 |

---

## 10. 评审请求

请 @北葵 @幻想 @知了 @杰 在 PR 提交后 4 小时内 Review，重点关注：

1. **架构**：app factory / blueprint 分层是否符合预期
2. **数据模型**：User / Activity / Registration 字段是否够用
3. **测试**：7 条 pytest 用例是否覆盖本轮关键路径
4. **端口 / 配置**：8080、MySQL 连接串、`.env.example` 字段

> **本文档维护**：达成 PR 1 验收后归档至 `docs/snapshots/pr1-flask-snapshot.md`；如有范围调整追加变更记录。
