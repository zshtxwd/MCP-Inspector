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
