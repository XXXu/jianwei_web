# 见微

见微是一个基于 Horizon 情报引擎的角色化 AI 情报网站。

它的目标不是做新闻聚合站，而是把分散在新闻站、RSS、GitHub、社区、产品发布、融资动态和行业渠道里的信息，重新加工成不同角色可以直接用于判断和行动的情报。

## 产品定位

> 从信息里看见方向。

第一版采用“免费公开网站 + 轻量订阅入口”的方式，让用户先选择“我是谁”，再进入对应的情报流。

计划中的首批角色包括：

- 独立开发者 / AI 产品创业者
- 跨境卖家 / 出海产品人
- 投资 / 融资观察者
- 企业 AI 应用负责人

## 与 Horizon 的关系

`Horizon` 是独立的情报采集与 AI 分析引擎。

`jianwei_web` 是独立的网站产品项目，负责面向用户的 Web 产品层。

职责边界：

```text
Horizon
负责：数据源抓取、去重、AI 打分、AI 富化、摘要生成、数据源扩展

jianwei_web
负责：首页、角色页、详情页、归档页、订阅入口、数据库、API、PWA、部署入口
```

本项目后续会通过适配层调用 Horizon，把 Horizon 产出的内容和分析结果转换成网站自己的数据库记录。

## 第一版目标

第一版优先验证：

1. 哪些角色真的需要这类情报。
2. AI 生成的角色化分析是否足够有价值。
3. 用户是否愿意持续访问或留下订阅方式。

第一版会做：

- 首页角色选择
- 角色情报页
- 情报详情页
- 历史归档页
- 邮箱订阅入口
- SQLite 持久化
- JSON API
- 服务端渲染页面
- PWA 基础支持
- Docker Compose 部署

第一版暂不做：

- 用户注册登录
- 支付订阅
- 个人自定义数据源
- 复杂后台管理
- 收藏夹
- 评论区
- 原生移动 App
- 分钟级实时抓取

## 技术方向

计划采用轻量单机架构，适配 2 核 4G 云服务器：

```text
Nginx
→ FastAPI Web 应用
→ SQLite 数据库
→ Worker 定时任务
→ Horizon 引擎
→ AI API / 数据源
```

计划技术栈：

- FastAPI：网站后端、JSON API、订阅提交
- Jinja2：第一版服务端渲染页面
- SQLite：第一版数据存储
- SQLAlchemy：数据库访问层
- Alembic：数据库迁移
- cron 或 APScheduler：定时任务
- Docker Compose：单机部署
- Nginx：反向代理、HTTPS、静态资源
- PWA：添加到手机桌面的轻量 App 体验

## 前端可替换原则

第一版可以使用 Jinja2 快速上线，但架构上必须保证未来可以替换为 React / Next.js。

原则：

- 业务逻辑不写在模板里。
- 所有核心页面都有对应 JSON API。
- 数据模型独立于页面层。
- Jinja2 页面只是第一版展示层。
- 后续 React / Next.js 可以直接消费已有 API。

## 项目状态

当前项目正在实现 MVP 骨架，已经具备 FastAPI 应用、SQLite 数据模型、角色化页面、JSON API、PWA 基础文件、Horizon artifact 导入链路和历史归档基础。

设计文档位于本项目中：

```text
docs/superpowers/specs/2026-05-11-jianwei-product-design.md
```

实施计划位于：

```text
docs/superpowers/plans/2026-05-12-jianwei-mvp-implementation.md
```

## 本地非 Docker 验证

如果本机已经安装好项目依赖，可以运行：

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check app tests
```

本机没有 Docker 时，可以先跳过 Docker 验证，把 Docker 部分放到 Linux 服务器上执行。

## Linux Docker Compose 验证

在 Linux 服务器上进入项目目录后，先准备环境变量：

```bash
cp .env.example .env
```

首次启动前建议确认 Docker Compose 文件可以解析：

```bash
sudo docker compose config
```

构建并后台启动：

```bash
sudo docker compose up -d --build
```

查看服务日志：

```bash
sudo docker compose logs -f
```

验证健康检查：

```bash
curl http://127.0.0.1:8080/health
```

预期返回：

```json
{"status":"ok","service":"jianwei"}
```

浏览器访问：

```text
http://服务器公网 IP:8080
```

如果公网无法访问，请在腾讯云控制台检查安全组入站规则，至少开放 TCP `8080` 端口。正式上线时建议再接入域名、HTTPS 和更严格的 Nginx 配置。

## 数据库迁移和默认角色

Docker Compose 中的 `web` 服务启动时会自动执行：

```bash
uv run alembic upgrade head
uv run python -m app.seed
```

也就是说，容器启动时会自动创建数据库表，并初始化默认角色。SQLite 数据库会保存在宿主机项目目录的 `data/` 目录中。

## 常用运维命令

停止服务：

```bash
sudo docker compose down
```

重新构建：

```bash
sudo docker compose up -d --build
```

查看容器状态：

```bash
sudo docker compose ps
```

进入 Web 容器：

```bash
sudo docker compose exec web sh
```
