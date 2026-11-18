# 新闻资讯 App · FastAPI 全栈项目

一个移动端风格的新闻资讯应用：新闻分类 / 列表 / 详情、收藏、浏览历史、注册登录、个人资料，以及接入**通义千问**的流式 AI 问答。

前后端分离，后端用 FastAPI + SQLAlchemy 2.0 异步 ORM + MySQL，热点数据走 Redis 旁路缓存；前端是 Vue 3 + Vant 4 的 H5 页面。

> 说明：这是一个**个人学习项目**（主体跟随课程完成，AI 问答模块为自行接入千问并实现代理与流式解析），用于练习 FastAPI 全栈开发，不是生产系统。

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.125-009688?logo=fastapi&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?logo=mysql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7-DC382D?logo=redis&logoColor=white)
![Vue](https://img.shields.io/badge/Vue-3-42B883?logo=vuedotjs&logoColor=white)

---

## 功能

- **新闻**：分类导航、分页列表、详情（正文 / 作者 / 发布时间 / 浏览量）、同分类相关推荐
- **AI 问答**：接入阿里云百炼（DashScope）`qwen-plus`，服务端代理、SSE 流式返回，前端逐字渲染，支持 Markdown 与代码块
- **用户**：注册、登录、Token 鉴权、修改资料、修改密码
- **收藏 / 历史**：收藏与取消、收藏状态回显、浏览历史自动记录、单条删除与清空
- **体验**：Pinia 持久化登录态、中英双语（vue-i18n）、深浅主题、移动端 TabBar 导航

## 技术栈

| 层 | 选型 |
| --- | --- |
| Web 框架 | FastAPI 0.125、Uvicorn |
| ORM / 数据库 | SQLAlchemy 2.0（async）、aiomysql、MySQL 8 |
| 缓存 | Redis（`redis.asyncio`）、JSON 序列化、Cache-Aside |
| 鉴权 | Bearer Token（服务端签发、落库）、`passlib` pbkdf2_sha256 |
| AI | 阿里云百炼 DashScope、`httpx`、SSE |
| 前端 | Vue 3、Vite 7、Vue Router 4、Pinia + persistedstate |
| UI | Vant 4、`marked` + `DOMPurify`（Markdown 渲染与 XSS 过滤） |
| 国际化 | vue-i18n 9（zh-CN / en-US） |

## 架构

```
┌──────────────────────────────┐
│  Vue 3 + Vant + Pinia (H5)   │
└──────────────┬───────────────┘
               │ axios / fetch(SSE)
┌──────────────▼───────────────┐
│           FastAPI            │
│  routers → crud → models     │
│     │            │           │
│     │            └── SQLAlchemy async → MySQL
│     └── cache（Redis，Cache-Aside，异常降级）
│     └── ai_proxy（httpx → DashScope）
└──────────────────────────────┘
```

后端按职责分层：`routers` 只做参数校验与响应组装，`crud` 封装所有 SQL，`cache` 封装 Redis 读写，`schemas` 定义出入参。

## 目录结构

```
.
├── main.py                 # FastAPI 入口，注册路由 / CORS / 全局异常
├── routers/                # 接口层：news / users / favorite / history / ai_proxy
├── crud/                   # 数据访问层（含 news_cache 缓存读写）
├── models/                 # SQLAlchemy ORM 模型
├── schemas/                # Pydantic 出入参
├── cache/                  # Redis key 与 TTL 定义
├── config/                 # 数据库连接、Redis 连接
├── utils/                  # 鉴权、密码、统一响应、异常处理
├── 02-数据库sql文件/        # database.sql（建库建表 + 示例数据）
└── 03-前端项目代码/xwzx-news # Vue 3 前端
```

## 快速开始

### 1. 准备 MySQL 与 Redis

```sql
CREATE DATABASE news DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
```

```bash
mysql -u root -p news < "02-数据库sql文件/database.sql"
```

Redis 默认连 `localhost:6379`（见 `config/cache_conf.py`）。

### 2. 配置环境变量

在项目根目录新建 `.env`：

```ini
DATABASE_URL=mysql+aiomysql://root:你的密码@127.0.0.1:3306/news?charset=utf8mb4
DASHSCOPE_API_KEY=sk-你的百炼Key
```

### 3. 启动后端

```bash
python -m venv .venv
.venv\Scripts\activate        # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt redis
uvicorn main:app --reload --port 8000
```

接口文档：http://127.0.0.1:8000/docs

### 4. 启动前端

```bash
cd 03-前端项目代码/xwzx-news
npm install
npm run dev
```

打开 http://localhost:5173 （`/api` 已由 Vite 代理到 8000）。

## 接口一览

| 模块 | 方法 | 路径 |
| --- | --- | --- |
| 新闻 | GET | `/api/news/categories` |
| 新闻 | GET | `/api/news/list?categoryId=&page=&pageSize=` |
| 新闻 | GET | `/api/news/detail?id=` |
| 用户 | POST | `/api/user/register` |
| 用户 | POST | `/api/user/login` |
| 用户 | GET | `/api/user/info` |
| 用户 | PUT | `/api/user/update` |
| 用户 | PUT | `/api/user/password` |
| 收藏 | GET | `/api/favorite/check` |
| 收藏 | POST | `/api/favorite/add` |
| 收藏 | DELETE | `/api/favorite/remove` |
| 收藏 | GET | `/api/favorite/list` |
| 收藏 | DELETE | `/api/favorite/clear` |
| 历史 | POST | `/api/history/add` |
| 历史 | GET | `/api/history/list` |
| 历史 | DELETE | `/api/history/delete/{news_id}` |
| 历史 | DELETE | `/api/history/clear` |
| AI | POST | `/api/ai/chat` |

## 缓存设计

| Key | 内容 | TTL |
| --- | --- | --- |
| `news:categories` | 分类列表 | 2h |
| `news_list:{分类id\|all}:{页码}:{每页}` | 新闻列表 | 30min |
| `news:detail:{id}` | 新闻详情 | 5min |
| `news:related:{id}:{分类id}` | 相关新闻 | 30min |

- 读路径 Cache-Aside：先查 Redis，未命中回源 MySQL 并回填。
- 所有缓存读写 `try/except` 降级，Redis 不可用时不影响接口（只打日志）。
- TTL 按数据稳定性分级，避免同一时刻集中过期。
- 浏览量 `views = views + 1` 走独立事务，失败不阻断详情返回（弱一致换读性能）。

## AI 问答流程

```
浏览器 → POST /api/ai/chat → 后端 httpx → DashScope(compatible-mode, stream)
                                   ↓
浏览器 ← SSE data: {...} ← 逐块转发
```

- API Key 只存在服务端 `.env`，前端不接触。
- 前端 `fetch` + `ReadableStream` 按行解析 `data:`，取 `choices[0].delta.content` 增量渲染。
- Markdown 经 `marked` 解析后由 `DOMPurify` 过滤，防 XSS。

## 已知限制

- AI 代理目前是**缓冲转发**（未对上游使用 `stream=True`），短回复体感正常，长回复不是严格逐 token 推送。
- Token 鉴权为教学简化实现；生产环境应加过期校验、刷新机制与更严格的 CORS 白名单。
- 全局异常处理里 `DEBUG_MODE = True`，会返回堆栈，上线前必须关闭。
- 暂无自动化测试。

## 说明

课程来源：黑马程序员相关课程。AI 问答、缓存落地与部分前端交互为个人实践与调整。
