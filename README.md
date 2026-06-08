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
├── apps/                       # 应用代码（计划中）
│   ├── web/                    # 前端（React + TS + Vite + Tailwind + shadcn/ui）
│   └── api/                    # 后端（NestJS + Prisma + PostgreSQL）
├── docs/
│   ├── design/                 # 设计文档（PRD、架构图）
│   ├── plans/                  # 实施计划
│   └── snapshots/              # 里程碑快照
├── .github/
│   ├── ISSUE_TEMPLATE/
│   └── PULL_REQUEST_TEMPLATE.md
├── .trae/
│   └── rules/project_rules.md  # AI 协作规则
├── .gitignore
├── CONTRIBUTING.md             # 协作规范
├── LICENSE
└── README.md
```

## 协作

- **4 人团队**：幻想（前端）/ 知了、杰（后端）/ 北葵（QA & 产品检测）
- **Git 规范**：Conventional Commits + 分支策略（`main` / `develop` / `feature/*` / `fix/*`）
- **PR 流程**：关联 Issue，至少 1 人 Review 通过，北葵全程 Review 关键 PR

## 快速链接

- 📄 [PRD v0.1](docs/design/event-registration-prd.md)
- 🤝 [协作规范](CONTRIBUTING.md)
- 📜 [项目 AI 规则](.trae/rules/project_rules.md)

## License

见 [LICENSE](LICENSE)。
