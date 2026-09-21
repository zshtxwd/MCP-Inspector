# MCP Inspector

本项目用于帮助开发者进行 MCP 服务器的开发与调试。

## 技术栈

- 前端：Vue 3、Vite、TypeScript、Element Plus、Pinia、Axios
- 后端：Python、FastAPI、MCP Python SDK

## 本地开发

启动后端：

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\python -m pip install -e .
.\.venv\Scripts\python -m uvicorn app.main:app --reload --port 8000
```

启动前端：

```powershell
cd frontend
npm install
npm run dev
```

完成上述依赖安装后，也可以在项目根目录同时启动前后端：

```powershell
py scripts/start.py
```

前端地址为 `http://localhost:5173`，后端地址为
`http://localhost:8000`，MCP Streamable HTTP 端点为
`http://localhost:8000/mcp`。

## MCP 服务配置

后端通过 `MCP_SERVERS_JSON` 环境变量维护 `serverId` 到 MCP Streamable
HTTP 服务的映射。未设置时默认提供指向本项目 MCP 端点的 `local` 配置。

```powershell
$env:MCP_SERVERS_JSON = '{"server-001":{"name":"filesystem","url":"https://example.com/mcp","status":"connected","transport":"streamable-http","headers":{"Authorization":"Bearer token"}}}'
```

配置后可通过 `GET /api/mcp-servers/{serverId}/capabilities` 获取该服务的
tools、resources、resource templates 和 prompts。通过
`GET /api/mcp-servers` 可获取全部已配置服务，也可通过同一路径的 POST 请求
新增服务，并通过 `GET/DELETE /api/mcp-servers/{serverId}` 查询或删除服务。
所有 API 响应统一包含 `success`、`code` 和 `data` 字段。
