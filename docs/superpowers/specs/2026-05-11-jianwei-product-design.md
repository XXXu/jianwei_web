# 见微网站产品设计文档

## 1. 产品目的

见微的目标不是做一个普通新闻聚合站，而是基于 Horizon 的采集与 AI 分析能力，构建一个面向不同角色的 AI 情报订阅平台。

核心价值是：把分散在新闻站、RSS、GitHub、社区、产品发布、融资动态和行业渠道里的信息，重新加工成用户能直接用于判断和行动的情报。

第一版重点验证三件事：

1. 哪些角色真的需要这类情报。
2. AI 生成的角色化分析是否足够有价值。
3. 用户是否愿意持续访问或留下订阅方式。

长期目标是从免费公开情报站，逐步升级为订阅付费产品，提供完整日报、机会库、关键词提醒、竞品监控、行业定制报告等能力。

## 1.1 项目边界

Horizon 应保持为一个独立项目，定位是“情报采集与 AI 分析引擎”。见微网站应作为另一个独立项目，定位是“面向用户的 Web 产品”。

两个项目的职责边界如下：

```text
Horizon 项目
负责：数据源抓取、去重、AI 打分、AI 富化、摘要生成、数据源扩展

见微网站项目
负责：首页、角色页、详情页、归档页、订阅入口、数据库、API、PWA、部署入口
```

网站项目可以通过三种方式使用 Horizon：

1. 作为 Python 包或本地路径依赖调用 Horizon 的模块。
2. 通过 Horizon CLI / worker 命令触发采集任务并读取输出。
3. 后续通过 Horizon MCP 或独立 API 做更松耦合的集成。

第一版推荐使用“网站项目内的适配层调用 Horizon 能力”的方式。适配层负责把 Horizon 的 `ContentItem` 和分析结果转换成网站项目自己的数据库记录。

因此，后续 Web、数据库、页面模板和订阅相关代码不放进 Horizon 项目，而是放在见微网站项目中，避免把 Horizon 从通用引擎变成单一产品代码库。

## 2. 产品定位

见微第一版定位为：

> 面向不同职业和业务角色的 AI 情报雷达，把“新闻”加工成“决策价值”。

首页不做泛新闻流，而是让用户先选择“我是谁”。每个角色背后对应不同的信息源、分析 Prompt、情报模板和输出重点。

第一版建议预设 4 个角色：

1. 独立开发者 / AI 产品创业者
2. 跨境卖家 / 出海产品人
3. 投资 / 融资观察者
4. 企业 AI 应用负责人

这些角色不代表产品只能服务这几类人，而是作为第一版验证入口。底层架构需要支持后续新增角色。

## 3. MVP 形态

第一版采用“免费公开网站 + 轻量订阅入口”的方式，不做登录和付费墙。

用户路径如下：

```text
首页
→ 选择“我是谁”
→ 进入对应角色情报页
→ 查看今日情报流
→ 打开情报详情
→ 看到背景、重要性、机会/风险、来源链接
→ 愿意持续关注的人留下邮箱或加入社群
```

第一版页面包括：

1. 首页
   - 展示产品定位。
   - 展示角色入口。
   - 引导用户选择自己的身份。

2. 角色情报页
   - 展示某个角色的今日情报。
   - 内容重点是“今日判断”，不是普通新闻列表。
   - 包含重要信号、产品机会、风险提醒、工具/项目推荐和来源链接。

3. 情报详情页
   - 展示单条内容的完整分析。
   - 包含“发生了什么”“为什么重要”“对该角色意味着什么”“可做机会”“风险提醒”“原始来源和相关讨论”。

4. 历史归档页
   - 按日期和角色展示历史情报。
   - 支持搜索引擎收录和用户复访。

5. 订阅入口
   - 第一版只收邮箱、订阅角色和可选关键词。
   - 暂不做密码登录、支付和完整用户系统。

6. 简单后台配置
   - 第一版不做可视化后台。
   - 角色、数据源、Prompt 和运行频率先通过配置文件维护。

## 4. 技术路线

第一版采用轻量 Web 产品架构：

```text
Nginx
→ 网站项目 FastAPI Web 应用
→ 网站项目 SQLite 数据库
→ 网站项目 Worker
→ Horizon 引擎
→ AI API / 数据源
```

推荐技术栈：

1. FastAPI
   - 负责网站路由、JSON API、订阅提交、健康检查和服务层调用。
   - 与 Horizon 同属 Python 生态，方便通过适配层复用 Horizon 的采集和 AI 分析逻辑。

2. Jinja2
   - 第一版用于服务端渲染 HTML 页面。
   - 适合内容型网站，有利于 SEO，部署简单。

3. HTMX / Alpine.js
   - 用于少量页面交互，例如订阅表单提交、展开收起、筛选和移动端菜单。
   - 不引入重型前端框架，降低第一版复杂度。

4. SQLite
   - 第一版数据库。
   - 以单个文件保存数据，适合 2 核 4G 单机部署和 MVP 验证。

5. SQLAlchemy
   - 负责 Python 与数据库之间的数据访问。
   - 让后续从 SQLite 迁移到 PostgreSQL 更平滑。

6. Alembic
   - 负责数据库结构迁移。
   - 保证本地和服务器的数据表结构可追踪、可升级。

7. cron 或 APScheduler
   - 负责在网站项目中定时触发 worker，再由 worker 调用 Horizon 采集和分析任务。
   - 第一版优先考虑系统 cron + worker 命令，简单可靠。

8. Docker Compose
   - 负责在单台服务器上编排 web、worker、nginx 等服务。

9. Nginx
   - 负责域名、HTTPS、静态资源缓存和反向代理。

10. PWA
    - 让网站支持添加到手机桌面。
    - 第一版只做基础 manifest、图标和静态资源缓存。

11. DeepSeek
    - 作为第一版 AI 分析模型。
    - 更适合国内服务器环境和早期成本控制。

## 5. 前端可替换原则

虽然第一版采用 FastAPI + Jinja2，但架构上必须保证未来可以替换为 React / Next.js 前端。

原则如下：

1. 业务逻辑不写在模板里。
   - Jinja2 只负责展示。
   - 排序、筛选、角色分析、订阅处理等逻辑放在服务层。

2. 所有核心页面都要有对应 JSON API。
   - 角色页有 API。
   - 情报详情有 API。
   - 归档页有 API。
   - 订阅提交有 API。

3. 数据模型独立于页面层。
   - `items`、`analyses`、`briefings`、`subscriptions` 不依赖 Jinja2。

4. 前端目录保持独立。
   - 第一版模板放在网站项目的 `app/templates` 或 `web/templates`。
   - 未来 React / Next.js 可以放在网站项目的 `frontend/`，通过 API 访问后端。

5. API 返回结构尽量稳定。
   - 后续更换前端时，React 直接消费已有 API，不重写后端核心逻辑。

演进路径：

```text
第一阶段：FastAPI + Jinja2 快速上线
第二阶段：保留 FastAPI API，新增 React / Next.js 前端
第三阶段：SQLite 迁移 PostgreSQL，逐步下线 Jinja2 页面
```

## 6. 数据模型

第一版建议使用以下核心表：

```text
personas
sources
persona_sources
items
analyses
briefings
subscriptions
runs
```

### personas

保存角色配置，例如独立开发者、跨境卖家、投资观察者、企业 AI 应用负责人。

关键字段：

- `id`
- `slug`
- `name`
- `description`
- `prompt_profile`
- `enabled`
- `created_at`
- `updated_at`

### sources

保存数据源配置，例如 RSS、GitHub、Hacker News、国内新闻站点、公开 API。

关键字段：

- `id`
- `type`
- `name`
- `url`
- `config`
- `enabled`
- `created_at`
- `updated_at`

### persona_sources

保存角色与数据源之间的关联。

同一个数据源可以服务多个角色，一个角色也可以绑定多个数据源。

### items

保存抓取到的原始内容，是事实层。

关键字段：

- `id`
- `source_id`
- `external_id`
- `title`
- `url`
- `content`
- `author`
- `published_at`
- `metadata`
- `created_at`

### analyses

保存某个角色对某条内容的 AI 分析，是判断层。

同一条 item 可以针对不同 persona 生成不同 analysis。

关键字段：

- `id`
- `item_id`
- `persona_id`
- `score`
- `summary`
- `why_it_matters`
- `opportunities`
- `risks`
- `tags`
- `model`
- `created_at`

### briefings

保存每天每个角色的一份情报日报。

关键字段：

- `id`
- `persona_id`
- `date`
- `title`
- `summary`
- `content`
- `status`
- `created_at`

### subscriptions

保存轻量订阅记录。

第一版不做账号系统，只记录：

- `id`
- `email`
- `persona_id`
- `keywords`
- `status`
- `created_at`

### runs

保存后台任务运行状态。

关键字段：

- `id`
- `job_type`
- `persona_id`
- `started_at`
- `finished_at`
- `status`
- `fetched_count`
- `analyzed_count`
- `error_message`

## 7. Horizon 集成与改造边界

现有 Horizon 流程是：

```text
抓取 → 去重 → AI 打分 → AI 富化 → 生成 Markdown 文件
```

见微集成 Horizon 后建议形成：

```text
网站 worker 触发任务
→ 调用 Horizon 抓取、去重和 AI 分析能力
→ 适配层转换结果
→ 存入网站项目的 items / analyses / briefings
→ 网站读取自己的数据库展示
```

第一阶段不重写 Horizon，也不把网站代码放进 Horizon。只在必要时对 Horizon 做通用能力扩展：

1. 保留现有 scraper。
2. 新增或调整数据源 scraper 时，仍保持 Horizon 的通用引擎定位。
3. 必要时增加更稳定的结构化输出，例如 JSON artifact 或可复用 pipeline API。
4. 保留 Markdown 生成功能作为导出和兼容能力。

网站项目负责：

1. 自己的数据库存储层。
2. persona 配置。
3. 角色化 Prompt。
4. Web/API 层。
5. 页面模板和 PWA。
6. 用户订阅数据。

这样可以保持两个项目边界清晰：Horizon 专注“把外部信息变成结构化分析结果”，网站项目专注“把结构化结果变成用户产品”。

## 8. 后台任务与部署

后台任务采用“后台定时生成，前台只读展示”的原则。

不要在用户访问页面时现场抓取、调用 AI 或生成情报。

见微后台 Worker 负责：

- 定时触发 Horizon 抓取数据源
- 去重
- 存入 `items`
- 按 persona 调用 AI 分析
- 生成 `briefings`
- 发送订阅邮件或 webhook
- 记录运行状态

第一版运行频率建议：

```text
每天 2-4 次
例如 08:00 / 14:00 / 20:00
```

Web 服务负责：

- 首页
- 角色页
- 详情页
- 归档页
- 订阅提交
- PWA 静态资源
- API 查询数据库

部署建议：

```text
nginx
website-web
website-worker
website-sqlite volume
horizon engine dependency
```

在 2 核 4G 服务器上，AI 分析并发建议控制为：

```json
{
  "analysis_concurrency": 2,
  "enrichment_concurrency": 2
}
```

## 9. 错误处理

第一版至少需要以下容错：

1. 某个数据源失败，不影响其他数据源。
2. 某个角色分析失败，不影响其他角色。
3. AI 调用失败时，保留原始 item，下一轮可重试。
4. 后台任务必须记录成功、失败、抓取数量、分析数量和错误信息。
5. 前台页面在当天没有日报时，展示最近一次成功生成的日报。

## 10. 第一版做什么

第一版网站项目要做：

- 首页角色选择
- 4 个预设角色
- 每个角色一套数据源配置
- 每个角色一套 AI 分析 Prompt
- 定时情报生成
- 情报列表页
- 情报详情页
- 历史归档页
- 邮箱订阅入口
- SQLite 持久化
- JSON API
- Jinja2 页面
- PWA 基础支持
- Docker Compose 部署
- Nginx 反向代理
- 任务运行日志

Horizon 项目同期只做必要的通用能力补充，例如新增国内数据源、优化结构化输出或修正采集问题。

## 11. 第一版不做什么

第一版网站项目不做：

- 用户注册登录
- 支付订阅
- 个人自定义数据源
- 复杂后台管理
- 收藏夹
- 评论区
- 原生移动 App
- 分钟级实时抓取
- 多服务器部署
- 推荐算法
- 复杂全文搜索

这些能力在验证用户需求后再逐步加入。

## 12. 后续商业化路径

第一阶段免费公开，用于验证内容价值和角色需求。

第二阶段加入轻量订阅：

- 邮箱日报
- 角色订阅
- 关键词订阅
- 微信群 / 飞书群 / 公众号引导

第三阶段加入付费能力：

- 免费版：公开日报和部分精选内容。
- 订阅版：完整日报、机会库、搜索和历史归档。
- 专业版：关键词监控、竞品提醒、行业定制报告。

第四阶段升级为完整 SaaS：

- 用户系统
- 支付系统
- 自定义数据源
- 自定义角色
- 团队空间
- PostgreSQL
- React / Next.js 前端

## 13. 关键设计判断

1. Horizon 保持独立项目，继续作为后端情报引擎，而不是承载最终网站产品代码。
2. 第一版不做完整 SaaS，先验证角色化情报的价值。
3. 网站项目单独创建，负责 Web、API、数据库、订阅和 PWA。
4. 第一版网站项目使用 SQLite，降低部署复杂度。
5. 第一版网站项目使用 Jinja2，但必须通过服务层和 JSON API 保证未来可替换前端。
6. 用户访问时只读数据库，不触发现场抓取和 AI 分析。
7. 数据模型中必须区分事实层 `items` 和判断层 `analyses`。
8. 数据源和 Prompt 必须配置化，方便后续扩展国内数据源和新角色。
9. 网站项目通过适配层调用 Horizon，避免两个项目互相污染。
