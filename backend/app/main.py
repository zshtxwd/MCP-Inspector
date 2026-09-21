from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.capabilities import CapabilitiesResponse, fetch_capabilities
from app.responses import ApiErrorResponse, ApiResponse
from app.server_config import (
    McpServerConfig,
    add_server_config,
    delete_server_config,
    get_server_configs,
)
from app.servers import (
    CreateMcpServerRequest,
    McpServerSummary,
    get_mcp_server_summary,
    list_mcp_servers,
)


app = FastAPI(
    title="MCP Inspector API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def handle_http_exception(_: Request, exc: HTTPException) -> JSONResponse:
    error = ApiErrorResponse(code=exc.status_code, message=str(exc.detail))
    return JSONResponse(status_code=exc.status_code, content=error.model_dump())


@app.exception_handler(RequestValidationError)
async def handle_validation_error(
    _: Request, exc: RequestValidationError
) -> JSONResponse:
    error = ApiErrorResponse(code=422, message="Request validation failed")
    content = error.model_dump()
    content["errors"] = jsonable_encoder(exc.errors())
    return JSONResponse(status_code=422, content=content)


@app.get("/api/health", tags=["system"])
async def health() -> ApiResponse[dict[str, str]]:
    return ApiResponse(
        data={
            "name": "MCP Inspector API",
            "status": "ok",
            "version": app.version,
        }
    )


@app.get(
    "/api/mcp-servers",
    response_model=ApiResponse[list[McpServerSummary]],
    tags=["mcp-servers"],
)
async def get_mcp_servers() -> ApiResponse[list[McpServerSummary]]:
    return ApiResponse(data=list_mcp_servers(get_server_configs()))


@app.post(
    "/api/mcp-servers",
    response_model=ApiResponse[None],
    tags=["mcp-servers"],
)
async def create_mcp_server(request: CreateMcpServerRequest) -> ApiResponse[None]:
    add_server_config(
        McpServerConfig(
            name=request.name,
            transport=request.transport,
            url=request.url,
        )
    )
    return ApiResponse(data=None)


@app.get(
    "/api/mcp-servers/{server_id}/capabilities",
    response_model=ApiResponse[CapabilitiesResponse],
    response_model_exclude_none=True,
    tags=["mcp-servers"],
)
async def get_mcp_server_capabilities(
    server_id: str,
) -> ApiResponse[CapabilitiesResponse]:
    server_config = get_server_configs().get(server_id)
    if server_config is None:
        raise HTTPException(status_code=404, detail="MCP server not found")

    try:
        capabilities = await fetch_capabilities(server_id, server_config)
        return ApiResponse(data=capabilities)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to fetch MCP server capabilities: {exc}",
        ) from exc


@app.get(
    "/api/mcp-servers/{server_id}",
    response_model=ApiResponse[McpServerSummary],
    tags=["mcp-servers"],
)
async def get_mcp_server(server_id: str) -> ApiResponse[McpServerSummary]:
    server = get_mcp_server_summary(server_id, get_server_configs())
    if server is None:
        raise HTTPException(status_code=404, detail="MCP server not found")
    return ApiResponse(data=server)


@app.delete(
    "/api/mcp-servers/{server_id}",
    response_model=ApiResponse[None],
    tags=["mcp-servers"],
)
async def delete_mcp_server(server_id: str) -> ApiResponse[None]:
    if not delete_server_config(server_id):
        raise HTTPException(status_code=404, detail="MCP server not found")
    return ApiResponse(data=None)
