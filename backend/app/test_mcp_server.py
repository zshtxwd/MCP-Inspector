"""Standalone MCP server used by the Inspector during local development."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP


mcp = FastMCP("MCP Test Server", stateless_http=True, json_response=True)


@mcp.tool()
def ping(message: str = "pong") -> str:
    """Return a message to verify that the MCP server is available."""
    return message


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    async with mcp.session_manager.run():
        yield


app = FastAPI(title="MCP Test Server", version="0.1.0", lifespan=lifespan)

# Keep the MCP app at the root so its streamable HTTP endpoint is /mcp.
app.mount("/", mcp.streamable_http_app())
