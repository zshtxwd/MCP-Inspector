from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mcp.server.fastmcp import FastMCP


mcp = FastMCP("MCP Inspector", stateless_http=True, json_response=True)


@mcp.tool()
def ping(message: str = "pong") -> str:
    """Return a message to verify that the MCP server is available."""
    return message


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    async with mcp.session_manager.run():
        yield


app = FastAPI(
    title="MCP Inspector API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", tags=["system"])
async def health() -> dict[str, str]:
    return {
        "name": "MCP Inspector API",
        "status": "ok",
        "version": app.version,
    }


# Keep this mount last so FastAPI routes are matched before the MCP ASGI app.
app.mount("/", mcp.streamable_http_app())
