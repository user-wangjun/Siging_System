# 活动报名平台 · WaytoAGI @ 东莞

> 东莞首期活动报名平台底座，后续将拓展到其他城市与区域。

## 项目简介

本项目为 WaytoAGI 社区东莞站点的活动报名平台底座，提供：

- 主办方自助发布活动（meetup / 赛事 / 邀请制）
- 参与者在线报名 + 自定义表单
- 现场签到（扫码 / 手机后 4 位）
- 微信服务通知 + 邮件 + 短信触达
- 多 region 扩展能力

## 仓库结构

```
├── app/                        # Flask 应用代码（计划中）
│   ├── blueprints/             # 业务蓝图：auth / org / activity / registration / checkin / notification / admin
│   ├── templates/              # Jinja2 模板
│   ├── static/                 # 静态资源（含 static/uploads/ 用户上传）
│   ├── db/                     # PyMySQL 工具与 SQL 聚合
│   ├── wsgi.py                 # WSGI 入口（gunicorn / waitress 启动）
│   └── config.py               # 配置加载（python-dotenv）
├── tests/                      # pytest 测试用例
├── docs/
│   ├── design/                 # 设计文档（PRD、架构图）
│   ├── plans/                  # 实施计划
│   └── snapshots/              # 里程碑快照
├── .github/
│   ├── ISSUE_TEMPLATE/
│   └── PULL_REQUEST_TEMPLATE.md
├── .trae/
│   └── rules/project_rules.md  # AI 协作规则
├── .env.example                # 环境变量样例（不含真实密钥）
├── pyproject.toml              # 项目元信息与依赖
├── requirements.txt            # pip 依赖锁定
├── .gitignore
├── CONTRIBUTING.md             # 协作规范
├── LICENSE
└── README.md
```

## 技术栈

- **后端**：Python 3.11+ / Flask 3.x / Jinja2 / PyMySQL
- **数据库**：MySQL 8.0
- **前端**：HTML + Tailwind CSS（CDN）+ Alpine.js（CDN）
- **测试**：pytest + pytest-flask
- **代码规范**：Ruff（lint + format）+ mypy
- **WSGI**：gunicorn（Linux）/ waitress（Windows）

## 协作

- **4 人团队**：幻想（模板 & UI）/ 知了（auth · org · activity）/ 杰（registration · checkin · notification）/ 北葵（QA & 产品检测）
- **Git 规范**：Conventional Commits + 分支策略（`main` / `develop` / `feature/*` / `fix/*`）
- **PR 流程**：关联 Issue，至少 1 人 Review 通过，北葵全程 Review 关键 PR
- **TDD 强制**：所有 Blueprint 业务逻辑必须先写 pytest 测试

## 快速链接

- 📄 [PRD v0.2](docs/design/event-registration-prd.md)
- 🤝 [协作规范](CONTRIBUTING.md)
- 📜 [项目 AI 规则](.trae/rules/project_rules.md)

## License

见 [LICENSE](LICENSE)。
