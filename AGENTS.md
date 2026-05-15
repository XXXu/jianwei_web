# AGENTS.md instructions for jianwei_web

## 语言偏好

- 与用户交流时必须使用中文。
- 新增或修改的 Markdown 文档内容优先使用中文。
- README、设计文档、实施计划、提示词文档、说明文档都优先使用中文。
- 除非用户明确要求使用其他语言，否则不要切换到英文。

## 产品定位

- 见微当前前台产品定位先收敛为：面向“独立开发者 / AI 产品创业者”的 AI 情报网站。
- 当前首页和运营表达应优先服务 `indie-maker` 这一角色。
- 暂时不要在首页主视觉里强调跨境卖家、投资观察者、企业 AI 应用负责人等其他角色。

## 架构边界

- 以上定位收敛只影响前台呈现和运营文案，不代表系统改成单角色架构。
- 后台业务代码、数据库结构、导入链路和 API 仍必须保持多角色可扩展设计。
- 不要移除或简化 `personas`、`persona_id`、`persona_slug` 等多角色字段和逻辑。
- `/personas/{slug}` 仍应支持未来多个角色。
- Horizon artifact 导入仍应通过 `analysis.persona_slug` 映射到对应 persona。
- 未来扩展其他角色时，应通过新增数据源、提示词和前台入口实现，而不是重做数据模型。

## 项目边界

- `jianwei_web` 是网站产品层，负责页面、API、订阅入口、SQLite 数据库、导入任务和部署入口。
- `Horizon` 是独立的数据采集与 AI 分析引擎，不要把 Horizon 的抓取逻辑直接搬进 `jianwei_web`。
- 两者通过 artifact JSON 进行衔接。

## 开发约定

- 优先保持小步改动，避免无关重构。
- 修改页面时要同步更新测试。
- 提交前至少运行：

```bash
python -m pytest -q
python -m ruff check app tests
```
