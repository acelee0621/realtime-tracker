# 📦 实时库存管理系统

一个全栈、实时的库存追踪应用，基于 FastAPI、WebSocket 和 PostgreSQL 构建。本项目旨在演示如何构建一个高度互动、异步的现代化Web服务。

用户可以通过前端界面添加、更新和删除库存物品，所有更改都会被即时广播到所有连接的客户端，无需刷新页面。

![应用动态演示](https://github.com/acelee0621/realtime-tracker/blob/main/animation.gif)


---

## ✨ 核心特性

* **⚡️ 纯正的实时体验**：本项目核心功能深度依赖 **PostgreSQL 的 `LISTEN`/`NOTIFY`** 数据库级特性，配合 **WebSockets**，将任何数据变更即时、高效地推送给所有客户端。
* **🚀 现代化异步后端**：后端基于 **FastAPI** 和 **SQLAlchemy 2.0** 构建，充分利用 Python 的 `async/await` 语法实现高性能的非阻塞I/O。
* **🔗 健壮的连接管理**：服务器能够有效管理多个 WebSocket 连接，并优雅地处理客户端的断连与重连。
* **🛡️ 安全与稳定**：
    * 包含健康检查接口 (`/health`, `/db-check`)，便于生产环境监控。
    * 前端通过HTML转义来防止XSS攻击。
    * WebSocket客户端具备自动重连机制，提升用户体验。
* **🌐 轻量级原生前端**：一个简洁、轻快的用户界面，完全由**原生 JavaScript (ES6 Class)**、HTML 和 CSS 构建，无需任何重型框架。

---

## 🏛️ 架构概览

本应用采用解耦的事件驱动架构来实现实时功能，其核心是 PostgreSQL 数据库。

1.  **客户端 (浏览器)**：用户通过标准的 REST API 调用后端，执行一项CRUD操作（例如，添加一个新物品）。
2.  **FastAPI 后端**：后端处理 API 请求，并在 PostgreSQL 数据库中执行相应的操作。
3.  **数据库触发器**：`inventory` 表上的一个SQL触发器在数据发生任何变化（`INSERT`, `UPDATE`, `DELETE`）时自动触发。
4.  **Postgres NOTIFY**：触发器通过 `pg_notify()` 函数将一个JSON格式的载荷发送到一个指定的频道 (`inventory_channel`)。
5.  **通知服务**：FastAPI 应用内部一个专用的异步服务，持续 `LISTEN`（监听）着这个 PostgreSQL 频道。
6.  **WebSocket 广播**：在收到通知后，该服务将消息传递给 WebSocket 连接管理器，后者将其广播给所有已连接的客户端。
7.  **UI 更新**：客户端的 JavaScript 接收到 WebSocket 消息，并动态更新界面以反映数据的最新变化。

```
+----------+      (1) REST API      +-----------------+      (2) CRUD      +-------------+
|          | ---------------------> |                 | -----------------> |             |
|  客户端  |                        |  FastAPI 后端   |                    |  PostgreSQL |
| (浏览器) |      (7) WS 更新       |                 | <----------------- | (含触发器)  |
|          | <--------------------- | (通知器 + WS)   |   (4) pg_notify()    |             |
+----------+                        +-----------------+ <----------------- +-------------+
                                           ^    (6) 广播
                                           |
                               (5) 监听 `inventory_channel` 频道
```

---

## 🛠️ 技术栈

* **后端:** Python 3.13+, FastAPI, SQLAlchemy (async), Uvicorn
* **数据库:** **PostgreSQL** (必需)
* **实时通信:** WebSockets, PostgreSQL LISTEN/NOTIFY
* **前端:** HTML5, CSS3, 原生 JavaScript (ES6)

---

## 🚀 快速开始

### 环境要求

* Python 3.13 或更高版本
* **PostgreSQL** 实例 (必需)
* 包管理工具 `pip`

### 1. 克隆仓库

```bash
git clone [https://github.com/your-username/realtime-tracker.git](https://github.com/your-username/realtime-tracker.git)
cd realtime-tracker
```

### 2. 创建并激活虚拟环境

本项目使用 uv 管理。

```bash
# 创建虚拟环境
uv venv
```

### 3. 安装依赖

```bash
# 使用 pyproject.toml 文件安装所有依赖
uv sync
```

### 4. 配置 PostgreSQL 数据库 (必需)

复制环境变量示例文件，并根据您的 PostgreSQL 信息进行修改。

```bash
cp .env.example .env
```

然后，编辑 `.env` 文件。

**重要提示：** 本项目深度依赖 PostgreSQL 的 `LISTEN/NOTIFY` 机制来实现核心的实时推送功能，因此**必须**使用 PostgreSQL 数据库。代码中保留的 SQLite 配置仅为项目模板残留，并未适配此项目的实时特性。

请确保您的 `.env` 文件配置如下：
```dotenv
# .env
DB_TYPE=postgres

DB_HOST=localhost
DB_PORT=5432
DB_USER=your_postgres_user
DB_PASSWORD=your_postgres_password
DB_NAME=your_database_name

# 其他连接池配置可按需调整
POOL_SIZE=20
MAX_OVERFLOW=10
```

### 5. 运行应用

服务器启动时，会自动创建所需的数据库和表。

```bash
uvicorn app.main:app --reload
```

### 6. 访问应用

打开您的浏览器并访问 **http://127.0.0.1:8000**

您可以打开多个浏览器窗口来观察实时同步更新的效果！

---

## 📬 联系

* 微信公众号：**码间絮语**
<center>
  <img src="https://github.com/acelee0621/fastapi-users-turtorial/blob/main/QRcode.png" width="500" alt="签名图">
</center>

* 欢迎 Star ⭐ & 关注，获取最新教程和代码更新。

---

## 📄 开源许可

本项目采用 **MIT 许可**。详情请见 [LICENSE](LICENSE) 文件。

Copyright (c) 2025 Aaron Lee