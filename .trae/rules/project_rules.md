# 项目规则 · 活动报名平台

> 适用于本项目所有 AI 协作（Trae / Cursor / 其他）的强制规则。
> 新规则须经 4 人团队评审通过后追加。

## 1. 通用规则

- 所有 AI 回答默认使用 **简体中文**。
- 函数创建与调用必须**参数名一致 + 参数完整**。
- Web 端绑定端口后，除用户主动要求，**保证端口不变**。
- 命名规范：**驼峰命名法**（变量、函数、文件名）。
- 注释与文档：
  - 解释「为什么」而非「做什么」
  - 函数级**中文注释**
  - 临时文档任务完成后删除；长期文档需持续维护
- 删除文件前**明确告知后果**，不留模糊表述。

## 2. 开发流程

- 严格遵循 **Superpowers 七阶段**（头脑风暴 → 工作树 → 计划 → 子代理开发 → TDD → 审查 → 完成分支）。
- 修改生产代码前**必须先写测试**（TDD RED-GREEN-REFACTOR）。
- 不在主分支直接开发，所有改动通过 PR 合入。
- 时间优化：避免不必要循环/递归；多阶段任务给出完成占比。
- 并行化：独立任务可派发给不同子代理，但**避免并行实现同一模块**。

## 3. Git 与协作

- Conventional Commits 提交信息。
- 功能分支：`feature/<scope>-<short-desc>`（如 `feature/api-registration-module`）。
- PR 描述必须包含：**实现思路 / 测试方法 / 影响范围**。
- 至少 1 人 Review 通过；北葵全程 Review 关键功能 PR。

## 4. 技术栈约束

- 后端：Python 3.11+ + Flask 3.x + Jinja2（Flask 内置）
- 前端：Flask 模板渲染（HTML + Jinja2 + Tailwind CSS CDN + Alpine.js CDN），首期不引入 SPA 框架
- 数据库：MySQL 8.0
- 数据库驱动：PyMySQL（首期不引入 SQLAlchemy ORM）
- 表单与校验：Flask-WTF + WTForms
- 静态资源：本地 `static/` 目录（用户上传走 `static/uploads/`）
- WSGI 容器：gunicorn（Linux）/ waitress（Windows）
- 测试：pytest + pytest-flask
- 代码规范：Ruff（lint + format）+ mypy
- 配置管理：python-dotenv
- 包管理：pip + venv（可选 uv）
- 工具替代说明：Ruff 单工具替代原 ESLint+Prettier 角色

## 5. 文档约定

- PRD / 设计文档：`docs/design/`
- 实施计划：`docs/plans/`
- 里程碑快照：`docs/snapshots/`
- 长期文档须写明维护责任人；临时文档不进入 `docs/`，随代码提交。

## 6. QA 与验收

- 北葵（产品检测）负责：验收用例设计、UAT 主导、Bug 跟踪、关键 PR Review。
- 每个 P0/P1 Bug 必须有回归测试。

## 7. 风险与回滚

- 涉及数据库 schema 变更：必须写 migration + 回滚脚本。
- 涉及第三方 API（微信/短信/邮件）：先在沙箱验证再上生产。
- 涉及 `static/uploads/` 文件存储：单实例方案下，部署前明确备份策略；多实例化时需引入共享存储。

---

**变更记录**

| 日期 | 变更 | 作者 |
| --- | --- | --- |
| 2026-06-08 | v0.1 初稿，固化 Superpowers 流程与团队分工 | 幻想 |
| 2026-06-08 | v0.2 技术栈重写：NestJS+React → Flask 单体；PostgreSQL+Prisma → MySQL+PyMySQL；OBS → 本地 static/；工具链替换为 Ruff + pytest | 幻想 |
