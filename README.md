# WaytoAGI 活动报名平台 v1.1.0

> 后端版本：Flask + MySQL + Redis + JWT + 邮箱验证码认证
> 目标仓库：https://github.com/user-wangjun/Siging_System

## 技术栈

- **Python 3.10+** + Flask 3.x
- **MySQL 8.0** + PyMySQL + SQLAlchemy 2.0 + Flask-Migrate
- **Redis**（验证码缓存、发送频率限制、Token 黑名单）
- **JWT 认证**（Flask-JWT-Extended，Access Token 2h + Refresh Token 30d，支持 Token 黑名单/登出）
- **邮箱验证码登录**（支持 Gmail / QQ / 163 / 企业邮箱等主流邮箱）
- **Flask-Mail** SMTP 邮件发送
- **二维码生成**（qrcode，签到二维码）
- **前端**：Flask Jinja2 模板（预留 REST API 供后续前后端分离）

## 功能介绍

### 🔐 认证系统
- 邮箱验证码登录/注册（自动注册）
- JWT Token 认证（Access Token + Refresh Token）
- Token 黑名单（登出后 Token 立即失效）
- 发送频率限制（60秒内不可重复发送验证码）
- 验证码 30 分钟有效期

### 👤 用户管理
- 个人资料查看与更新（昵称、手机号、真实姓名、头像）
- 我的报名记录查看（支持按状态筛选）
- 用户状态管理（管理员可禁用/启用用户）

### 🏢 组织管理
- 创建/更新/解散组织
- 组织成员邀请（自动发送通知）
- 成员角色管理（owner / admin / member）
- 移除成员
- 组织权限校验（基于角色的访问控制）

### 📅 活动管理
- 创建/更新/删除活动
- 活动发布与审核流程（草稿 → 待审核 → 已发布）
- 活动场次管理（多场次支持）
- 活动模板管理（创建/更新/删除/应用模板）
- 报名表单自定义（创建活动时配置报名字段）
- 活动列表查询（支持按组织、状态筛选）
- 活动状态自动流转（草稿/待审核/已发布/进行中/已结束/已取消）

### 📝 报名管理
- 提交报名（支持自定义表单数据）
- 取消报名（自动回退名额）
- 报名审核（通过/拒绝，自动发送通知）
- 候补机制（名额满后自动进入候补）
- 报名列表查看
- 签到二维码获取（Base64 PNG 图片）

### ✅ 签到核销
- 二维码扫码签到（解析 CHECKIN:xxx 格式）
- 手动搜索签到（按姓名/手机号搜索）
- 签到统计（签到率、签到人数）
- 签到权限校验（仅组织管理员可操作）
- 签到成功自动通知

### 🔔 通知系统
- 报名成功通知
- 报名审核结果通知（通过/拒绝）
- 活动审核结果通知（通过/拒绝，含拒绝原因）
- 组织邀请通知
- 签到成功通知
- 未读通知数量查询
- 全部标记已读
- 单条标记已读

### 🛠 运营后台
- 平台数据看板（用户数、活动数、报名数、签到数、签到率）
- 待审核活动列表与审核操作
- 用户管理（查看列表、禁用/启用）

### 📦 部署支持
- Docker 一键部署（docker-compose.yml + Dockerfile）
- 邮件配置测试脚本（test_email.py）
- Gunicorn 生产部署配置
- Nginx 反向代理配置示例

---

## 快速开始

### 方式一：Docker 一键部署（推荐）

```bash
cd Siging_System

# 1. 配置环境变量
cp .env.example .env
# 编辑 .env，填写 SECRET_KEY、JWT_SECRET_KEY、邮件配置等

# 2. 一键启动
docker-compose up -d

# 3. 访问应用
# 首页: http://localhost:5000/
# 登录页: http://localhost:5000/login
```

### 方式二：本地开发

#### 1. 环境要求

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y mysql-server redis-server

# 创建 MySQL 数据库和用户
sudo mysql -e "CREATE DATABASE IF NOT EXISTS waytoagi_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
sudo mysql -e "CREATE USER IF NOT EXISTS 'waytoagi'@'localhost' IDENTIFIED BY 'waytoagi123';"
sudo mysql -e "GRANT ALL PRIVILEGES ON waytoagi_dev.* TO 'waytoagi'@'localhost'; FLUSH PRIVILEGES;"
```

#### 2. 克隆项目

```bash
git clone https://github.com/user-wangjun/Siging_System.git
cd Siging_System
```

#### 3. 环境配置

```bash
cp .env.example .env
# 编辑 .env 配置以下关键项：
```

**必须配置的环境变量：**

| 变量 | 说明 | 示例 |
|------|------|------|
| `SECRET_KEY` | Flask 密钥 | `your-secret-key` |
| `JWT_SECRET_KEY` | JWT 密钥 | `your-jwt-secret` |
| `DATABASE_URL` | MySQL 连接 | `mysql+pymysql://waytoagi:waytoagi123@localhost:3306/waytoagi_dev?charset=utf8mb4` |
| `REDIS_URL` | Redis 连接 | `redis://localhost:6379/0` |
| `MAIL_SERVER` | SMTP 服务器 | `smtp.gmail.com` 或 `smtp.qq.com` |
| `MAIL_PORT` | SMTP 端口 | `587` (TLS) 或 `465` (SSL) |
| `MAIL_USERNAME` | 发件邮箱 | `your-email@gmail.com` |
| `MAIL_PASSWORD` | 邮箱授权码/密码 | `your-app-password` |
| `MAIL_DEFAULT_SENDER` | 默认发件人 | `your-email@gmail.com` |

> **注意**：QQ/163/Gmail 等邮箱需使用「授权码」而非登录密码。详细配置见下方「邮件配置指南」。

#### 4. 安装依赖

```bash
pip install -r requirements.txt
# 如遇权限问题，添加 --break-system-packages
```

#### 5. 初始化数据库

```bash
export FLASK_APP=run.py
export FLASK_ENV=development

flask db init          # 首次执行
flask db migrate -m "init"
flask db upgrade
```

#### 6. 测试邮件配置（可选）

```bash
python test_email.py
```

#### 7. 启动开发服务器

```bash
python run.py
# 或
flask run --host=0.0.0.0 --port=5000
```

#### 8. 访问应用

| 页面 | 地址 |
|------|------|
| 首页 | http://localhost:5000/ |
| 登录页 | http://localhost:5000/login |
| 活动列表 | http://localhost:5000/activities |
| 活动详情 | http://localhost:5000/activities/{id} |
| 我的组织 | http://localhost:5000/orgs |
| 我的报名 | http://localhost:5000/my/registrations |
| 运营后台 | http://localhost:5000/admin |

---

## API 文档

### 统一响应格式

```json
{
  "code": 200,
  "message": "success",
  "data": {},
  "timestamp": "2026-06-08T15:20:02",
  "request_id": "uuid"
}
```

### 认证模块

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/v1/auth/email/code` | 发送邮箱验证码 | 否 |
| POST | `/api/v1/auth/email/login` | 邮箱验证码登录/注册 | 否 |
| POST | `/api/v1/auth/refresh` | 刷新 JWT Token | Refresh Token |
| GET | `/api/v1/auth/me` | 获取当前用户信息 | Access Token |
| POST | `/api/v1/auth/logout` | 登出（Token 加入黑名单） | Access Token |

**发送验证码请求：**
```bash
curl -X POST http://localhost:5000/api/v1/auth/email/code \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
```

**登录请求：**
```bash
curl -X POST http://localhost:5000/api/v1/auth/email/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "code": "123456"}'
```

**登录成功响应：**
```json
{
  "code": 200,
  "data": {
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "user": {
      "id": 1,
      "email": "user@example.com",
      "nickname": "用户user",
      "role": "user",
      "status": 1
    }
  },
  "message": "登录成功"
}
```

### 用户模块

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | `/api/v1/users/me` | 获取个人资料 | Access Token |
| PUT | `/api/v1/users/me` | 更新个人资料 | Access Token |
| GET | `/api/v1/users/me/registrations` | 我的报名列表 | Access Token |

### 组织模块

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/v1/orgs` | 创建组织 | Access Token |
| GET | `/api/v1/orgs` | 我的组织列表 | Access Token |
| GET | `/api/v1/orgs/{id}` | 组织详情 | Access Token |
| PUT | `/api/v1/orgs/{id}` | 更新组织 | Access Token |
| DELETE | `/api/v1/orgs/{id}` | 解散组织 | Access Token |
| POST | `/api/v1/orgs/{id}/members` | 邀请成员 | Access Token |
| PUT | `/api/v1/orgs/{id}/members/{uid}` | 更新成员角色 | Access Token |
| DELETE | `/api/v1/orgs/{id}/members/{uid}` | 移除成员 | Access Token |

### 活动模块

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/v1/activities` | 创建活动（支持 form_fields 和 template_id） | Access Token |
| GET | `/api/v1/activities` | 活动列表 | 可选 |
| GET | `/api/v1/activities/{id}` | 活动详情 | 可选 |
| PUT | `/api/v1/activities/{id}` | 更新活动 | Access Token |
| DELETE | `/api/v1/activities/{id}` | 取消/删除活动 | Access Token |
| POST | `/api/v1/activities/{id}/publish` | 发布活动 | Access Token |

**创建活动（含自定义表单）请求示例：**
```bash
curl -X POST http://localhost:5000/api/v1/activities \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "org_id": 1,
    "title": "AI 技术分享会",
    "description": "一起探讨 AI 前沿技术",
    "location": "北京市海淀区",
    "start_time": "2026-07-01T14:00:00",
    "end_time": "2026-07-01T17:00:00",
    "max_participants": 50,
    "form_fields": [
      {"name": "姓名", "type": "text", "required": true},
      {"name": "手机号", "type": "phone", "required": true},
      {"name": "公司/学校", "type": "text", "required": false},
      {"name": "是否首次参加", "type": "select", "options": ["是", "否"], "required": true}
    ],
    "template_id": null
  }'
```

### 活动模板模块

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/v1/templates` | 创建活动模板 | Access Token |
| GET | `/api/v1/templates/org/{org_id}` | 组织模板列表 | Access Token |
| GET | `/api/v1/templates/{id}` | 模板详情 | Access Token |
| PUT | `/api/v1/templates/{id}` | 更新模板 | Access Token |
| DELETE | `/api/v1/templates/{id}` | 删除模板 | Access Token |
| POST | `/api/v1/templates/{id}/apply/{activity_id}` | 应用模板到活动 | Access Token |

### 报名模块

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/v1/activities/{id}/register` | 提交报名 | Access Token |
| GET | `/api/v1/registrations/{id}` | 报名详情 | Access Token |
| PUT | `/api/v1/registrations/{id}` | 修改报名 | Access Token |
| DELETE | `/api/v1/registrations/{id}` | 取消报名 | Access Token |
| GET | `/api/v1/activities/{id}/registrations` | 活动报名列表 | Access Token |
| PUT | `/api/v1/registrations/{id}/status` | 审核报名 | Access Token |
| GET | `/api/v1/registrations/{id}/qrcode` | 获取签到二维码 | Access Token |

**获取签到二维码响应示例：**
```json
{
  "code": 200,
  "data": {
    "qrcode_image": "data:image/png;base64,iVBORw0KGgo...",
    "checkin_code": "CHECKIN:abc123..."
  }
}
```

### 签到模块

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/v1/checkin/qrcode` | 二维码签到 | Access Token |
| POST | `/api/v1/checkin/manual` | 手动搜索签到 | Access Token |
| GET | `/api/v1/checkin/activities/{id}/stats` | 签到统计 | Access Token |

### 通知模块

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | `/api/v1/notifications` | 通知列表 | Access Token |
| GET | `/api/v1/notifications/unread-count` | 未读通知数量 | Access Token |
| PUT | `/api/v1/notifications/read-all` | 全部标记已读 | Access Token |
| PUT | `/api/v1/notifications/{id}/read` | 标记已读 | Access Token |

### 运营模块（平台管理员）

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | `/api/v1/admin/activities/pending` | 待审核活动列表 | Access Token + admin |
| PUT | `/api/v1/admin/activities/{id}/audit` | 审核活动 | Access Token + admin |
| GET | `/api/v1/admin/stats` | 数据看板 | Access Token + admin |
| GET | `/api/v1/admin/users` | 用户管理列表 | Access Token + admin |
| PUT | `/api/v1/admin/users/{id}/status` | 更新用户状态（禁用/启用） | Access Token + admin |

---

## 项目结构

```
Siging_System/
├── app/
│   ├── __init__.py           # Application Factory
│   ├── config.py             # 配置（开发/测试/生产）
│   ├── extensions.py         # Flask 扩展初始化
│   ├── api/v1/               # REST API Blueprints
│   │   ├── auth.py           # 认证接口（邮箱验证码、登出）
│   │   ├── user.py           # 用户接口（个人资料、我的报名）
│   │   ├── organization.py   # 组织接口
│   │   ├── activity.py       # 活动接口
│   │   ├── registration.py   # 报名接口（含签到二维码）
│   │   ├── checkin.py        # 签到接口
│   │   ├── notification.py   # 通知接口
│   │   ├── template.py       # 活动模板接口
│   │   └── admin.py          # 运营接口（含用户管理）
│   ├── models/               # SQLAlchemy 模型
│   │   ├── user.py           # User, UserAuth
│   │   ├── organization.py   # Organization, OrgMember
│   │   ├── activity.py       # Activity, ActivitySession, ActivityTemplate
│   │   ├── registration.py   # Registration, RegistrationForm
│   │   ├── checkin.py        # CheckinLog
│   │   └── notification.py   # Notification, NotificationTemplate
│   ├── services/             # 业务逻辑层
│   │   ├── auth_service.py   # 邮箱验证码认证逻辑
│   │   ├── user_service.py   # 用户资料管理
│   │   ├── org_service.py    # 组织管理（含邀请通知）
│   │   ├── activity_service.py # 活动管理（含表单自定义）
│   │   ├── registration_service.py # 报名管理（含审核通知）
│   │   ├── checkin_service.py # 签到管理（含权限校验、通知）
│   │   ├── notification_service.py # 通知服务（含业务通知便捷方法）
│   │   ├── template_service.py # 活动模板管理
│   │   └── admin_service.py  # 平台运营（含审核通知）
│   ├── utils/                # 工具函数
│   │   ├── response.py       # 统一响应封装
│   │   ├── exceptions.py     # 自定义异常
│   │   ├── validators.py     # 验证器（邮箱、手机号）
│   │   ├── decorators.py     # 权限装饰器（角色、组织、活动权限）
│   │   ├── email_sender.py   # 邮件发送/验证码管理
│   │   └── qrcode_generator.py # 二维码生成工具
│   └── web/                  # Jinja2 模板页面
│       ├── routes.py         # Web 路由
│       └── templates/        # HTML 模板
│           ├── base.html
│           ├── index.html
│           ├── auth/login.html
│           ├── activity/list.html
│           ├── activity/detail.html
│           ├── org/list.html
│           ├── registration/my.html
│           └── admin/dashboard.html
├── migrations/               # Alembic 数据库迁移
├── tests/                    # 测试（待补充）
├── requirements.txt          # Python 依赖
├── .env.example              # 环境变量模板
├── Dockerfile                # Docker 镜像配置
├── docker-compose.yml        # Docker Compose 编排
├── .dockerignore             # Docker 忽略文件
├── test_email.py             # 邮件配置测试脚本
├── run.py                    # 开发启动入口
└── wsgi.py                   # WSGI 生产入口
```

---

## 邮件配置指南

### Gmail

```bash
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USE_SSL=false
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password  # 需开启两步验证，生成应用专用密码
```

### QQ 邮箱

```bash
MAIL_SERVER=smtp.qq.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USE_SSL=false
MAIL_USERNAME=your-qq@qq.com
MAIL_PASSWORD=your-auth-code     # QQ邮箱设置 → 账户 → 生成授权码
```

### 163 邮箱

```bash
MAIL_SERVER=smtp.163.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USE_SSL=false
MAIL_USERNAME=your-email@163.com
MAIL_PASSWORD=your-auth-code     # 163邮箱设置 → POP3/SMTP → 授权码
```

### 企业邮箱（腾讯/阿里/网易）

```bash
MAIL_SERVER=smtp.exmail.qq.com   # 腾讯企业邮
MAIL_PORT=465
MAIL_USE_TLS=false
MAIL_USE_SSL=true
MAIL_USERNAME=your-name@company.com
MAIL_PASSWORD=your-password
```

---

## 认证流程说明

### 邮箱验证码登录流程

1. 用户在登录页输入邮箱，点击「获取验证码」
2. 后端校验邮箱格式 → 检查发送频率（60秒限制）→ 生成6位数字验证码
3. 验证码存入 Redis，有效期 30 分钟
4. 通过 SMTP 发送验证码邮件到用户邮箱
5. 用户输入验证码，点击「登录/注册」
6. 后端校验验证码 → 若用户不存在则自动注册 → 生成 JWT Token
7. 返回 access_token + refresh_token + 用户信息

### Token 机制

- **Access Token**: 有效期 2 小时，用于 API 认证
- **Refresh Token**: 有效期 30 天，用于刷新 Access Token
- Token 通过 `Authorization: Bearer <token>` 头部传递
- **登出**：调用 `/api/v1/auth/logout` 将 Token 加入 Redis 黑名单，立即失效

---

## 权限体系

### 用户角色

| 角色 | 说明 |
|------|------|
| `user` | 普通用户 |
| `platform_admin` | 平台管理员 |

### 组织角色

| 角色 | 说明 | 权限 |
|------|------|------|
| `owner` | 组织所有者 | 全部权限 |
| `admin` | 管理员 | 创建活动、审核报名、执行签到 |
| `member` | 普通成员 | 查看组织、报名活动 |

### 权限装饰器

| 装饰器 | 用途 |
|--------|------|
| `@role_required('platform_admin')` | 校验用户全局角色 |
| `@org_permission_required('admin')` | 校验组织权限（member/admin/owner） |
| `@activity_permission_required('admin')` | 校验活动权限（需为活动组织的管理员） |

---

## 开发规范

### Git 工作流

- `main` — 生产分支
- `develop` — 开发主分支
- `feature/*` — 功能分支
- `release/v1.x.x` — 版本发布分支

### 提交规范

- `feat:` 新功能
- `fix:` 修复
- `docs:` 文档
- `refactor:` 重构
- `chore:` 构建/工具

---

## 部署指南

### Docker 部署（推荐）

```bash
cd Siging_System
docker-compose up -d
```

docker-compose 包含：
- **MySQL 8.0**：数据库服务
- **Redis 7**：缓存服务
- **Flask + Gunicorn**：Web 应用（自动执行数据库迁移）

### 生产环境配置

```bash
export FLASK_ENV=production
export SECRET_KEY="your-strong-secret-key"
export JWT_SECRET_KEY="your-strong-jwt-key"
export DATABASE_URL="mysql+pymysql://user:pass@host:3306/waytoagi_prod?charset=utf8mb4"
export REDIS_URL="redis://host:6379/0"
# 邮件配置...
```

### Gunicorn 启动

```bash
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
```

### Nginx 反向代理（推荐）

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 版本历史

### v1.1.0 (2026-06-09)

**新增功能：**
- 通知系统打通（报名成功/审核结果/活动审核/组织邀请/签到成功 自动发送通知）
- 二维码生成（报名后获取签到二维码图片）
- 活动模板管理（创建/查询/更新/删除/应用模板）
- 报名表单自定义（创建活动时配置报名字段）
- JWT Token 黑名单（登出功能）
- 我的报名页面（按状态筛选、取消报名、查看签到码）
- 用户管理接口（admin 禁用/启用用户）
- 未读通知数量 / 全部已读接口
- Docker 部署配置（Dockerfile + docker-compose.yml）
- 邮件配置测试脚本（test_email.py）

**Bug 修复：**
- 修复报名名额判断逻辑（status 永远为 'approved' 的问题）
- 修复通知服务 ValidationError 未导入
- 修复 email_sender TTL 取错 key

**权限增强：**
- 报名审核权限校验（仅组织管理员可审核）
- 签到操作权限校验（仅组织管理员可执行）
- 新增 activity_permission_required 装饰器

### v1.0.0 (2026-06-08)

- 项目初始化，完整后端架构搭建
- 用户认证：邮箱验证码登录/注册（支持主流邮箱）
- 组织管理：创建、成员邀请、角色管理
- 活动管理：创建、发布、场次管理
- 报名管理：表单、提交、审核、取消
- 签到核销：二维码签到、手动签到
- 通知系统：站内通知
- 运营后台：活动审核、数据统计
- Web 前端：Jinja2 模板页面
- 预留 REST API 接口供后续前后端分离

---

## 待办事项（给下一位开发者）

- [ ] 补充单元测试和集成测试
- [ ] 完善 Celery 异步任务（邮件发送、通知推送）
- [ ] 接入微信扫码登录（保留 email 认证作为备选）
- [ ] 文件上传功能（头像、活动封面、组织 Logo）
- [ ] 前端 Vue/React 重构（当前为 Jinja2 模板）
- [ ] API 限流和防刷机制完善（按用户/IP 区分）
- [ ] 日志收集和监控告警
- [ ] 数据导出功能（报名列表、签到记录导出 Excel）
- [ ] 活动搜索/关键词筛选
- [ ] 活动状态自动流转（定时任务）

---

## 联系方式

- 项目仓库：https://github.com/user-wangjun/Siging_System
- 技术栈：Python + Flask + MySQL + Redis
