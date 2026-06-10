# 协作规范 · WaytoAGI 活动报名平台

## 团队分工

| 成员 | 主职责 | 次职责 |
| --- | --- | --- |
| 幻想 | 前端架构 + 核心组件 + 业务页面 | UI/UX 走查 |
| 知了 | 后端核心模块（auth / org / activity） | 数据库设计、API 文档 |
| 杰 | 后端支撑模块（registration / checkin / notification） | 第三方对接、运维 |
| 北葵 | 产品检测（QA / 验收） | 验收用例、UAT、Bug 跟踪 |

## 分支策略

| 分支 | 用途 | 受保护 |
| --- | --- | :---: |
| `main` | 生产可用版本 | ✅ |
| `develop` | 集成分支 | ✅ |
| `feature/*` | 功能开发（如 `feature/frontend-registration-form`） | ❌ |
| `fix/*` | 缺陷修复 | ❌ |
| `release/*` | 发布准备 | ❌ |
| `docs/*` | 文档变更 | ❌ |

**严禁**：直接 push 到 `main` / `develop`、在主分支上直接编码。

## 提交规范（Conventional Commits）

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

常用 type：`feat` / `fix` / `docs` / `style` / `refactor` / `test` / `chore` / `perf` / `ci`

示例：
- `feat(web): add registration form with custom fields`
- `fix(api): handle ticket QR expired edge case`
- `docs(prd): update MVP scope based on team review`

## PR 流程

1. 从 `develop` 切出 `feature/*` 或 `fix/*` 分支
2. 提交时遵循 Conventional Commits
3. 推送前确保本地测试通过、lint 通过
4. 创建 PR，**PR 描述必须包含**：
   - 实现思路（What & Why）
   - 测试方法（How to verify）
   - 影响范围（Side effects / migrations）
5. 关联对应 Issue（用 `Closes #123` / `Refs #456`）
6. 至少 1 人 Review 通过 + CI 通过 → Squash 合并
7. **北葵 Review 范围**：所有影响功能与体验的 PR（按团队约定）

## Worktree 推荐

每个功能分支建议使用独立 worktree，避免开发冲突：

```powershell
git worktree add ../Siging_System-feature-xxx -b feature/xxx develop
```

完成后用 `git worktree remove` 清理。

## 沟通节奏

- **每日站会** 15 min：昨日完成 / 今日计划 / 阻塞项
- **周会** 1 h：里程碑回顾 + 下周计划
- **PR Review SLA**：工作日 4h 内首响，24h 内完成
- **Bug 等级**：P0（线上，1h）/ P1（功能阻塞，4h）/ P2（一般，1 工作日）/ P3（建议，1 周）

## Issue 模板

- 提需求：用 Feature Request 模板
- 提 Bug：用 Bug Report 模板
- 任务拆解：用 Task 模板，关联 PRD 章节

## 技术栈（v0.2 锁定）

| 层 | 选型 | 说明 |
| --- | --- | --- |
| 运行时 | Python 3.11+ | 团队主语言 |
| Web 框架 | Flask 3.x + Jinja2 | 单体应用，模板原生 |
| 数据库 | **MySQL 8.0** | 团队运维熟悉，InnoDB 事务稳定 |
| 数据库驱动 | **PyMySQL** | 纯 Python，零原生依赖，**首期不引入 SQLAlchemy ORM** |
| 表单 | Flask-WTF（WTForms） | CSRF 内置，模板友好 |
| 静态资源 | 本地 `static/` | 用户上传走 `static/uploads/` |
| WSGI | gunicorn（Linux）/ waitress（Windows） | 跨平台 |
| 测试 | pytest + pytest-flask | TDD 强制 |
| 代码规范 | Ruff（lint + format）+ mypy | 单工具替代原 ESLint+Prettier 角色 |
| 端口 | **8080** | 绑定后不变 |

> **决策记录（2026-06-08，北葵确认）**：
> - **数据库用 mysql** —— 全栈统一 MySQL 8.0。
> - **Python 用 pymysql 库进行链接** —— 数据访问层**仅**使用 PyMySQL 直连 + 手写 SQL（封装在 `app/db/` 工具模块），**不引入 SQLAlchemy ORM**。Schema 变更走 `sql/` 目录下的版本化脚本 + 回滚脚本。
>
> 与 PRD §7.2、[project_rules.md §4](./.trae/rules/project_rules.md) 保持一致；如有调整需经 4 人团队评审。

## 代码风格

- 后端（Python）：Ruff（lint + format）+ mypy
- 前端：Tailwind CSS（CDN）+ Alpine.js（CDN），首期不引入构建工具
- 命名：驼峰命名法（用户约定）
- 注释：解释「为什么」而非「做什么」；函数级中文注释
- 函数创建与调用必须**参数名一致 + 参数完整**

## 快速链接

- 📄 [PRD v0.2](docs/design/event-registration-prd.md)
- 📋 [Flask 迁移计划 v1.0](docs/plans/flask-migration.md)
- 📜 [项目 AI 规则](.trae/rules/project_rules.md)
