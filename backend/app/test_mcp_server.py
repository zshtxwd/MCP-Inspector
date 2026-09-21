"""Inspector 本地开发期间使用的独立 MCP 服务。"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP


# 作为 Inspector 本地开发目标的进程内 MCP 服务。
mcp = FastMCP("MCP Test Server", stateless_http=True, json_response=True)


@mcp.tool()
def ping(message: str = "pong") -> str:
    """返回 *message*，供客户端验证服务是否可用。

    Args:
        message: 要原样返回给 MCP 客户端的内容。
    """

    return message


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """随 FastAPI 应用生命周期启动和停止 MCP 会话管理器。

    Args:
        _: 生命周期协议要求传入的 FastAPI 应用对象。
    """

    async with mcp.session_manager.run():
        yield


# 通过可流式传输 HTTP 暴露测试 MCP 服务的 FastAPI 包装应用。
app = FastAPI(title="MCP Test Server", version="0.1.0", lifespan=lifespan)

# 将 MCP 应用挂载到根路径，使可流式传输 HTTP 端点为 /mcp。
app.mount("/", mcp.streamable_http_app())
