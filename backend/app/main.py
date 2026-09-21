"""提供 MCP 服务管理接口的 FastAPI 应用。"""

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


# Uvicorn 和测试客户端使用的 FastAPI 应用实例。
app = FastAPI(
    title="MCP Inspector API",
    version="0.1.0",
)

# 允许本地前端开发服务器调用 API 的跨域策略。
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def handle_http_exception(_: Request, exc: HTTPException) -> JSONResponse:
    """将 FastAPI HTTP 异常转换为项目统一的错误响应结构。

    Args:
        _: 为符合 FastAPI 处理器签名而保留的请求对象。
        exc: 路由抛出的 HTTP 异常。
    """

    # 根据异常状态码和详情构造统一错误数据。
    error = ApiErrorResponse(code=exc.status_code, message=str(exc.detail))
    return JSONResponse(status_code=exc.status_code, content=error.model_dump())


@app.exception_handler(RequestValidationError)
async def handle_validation_error(
    _: Request, exc: RequestValidationError
) -> JSONResponse:
    """使用与其他 API 错误相同的结构返回请求校验失败信息。

    Args:
        _: 为符合 FastAPI 处理器签名而保留的请求对象。
        exc: 解析请求时生成的校验详情。
    """

    # 用于响应体的基础错误对象。
    error = ApiErrorResponse(code=422, message="Request validation failed")
    # Pydantic 生成的、兼容 JSON 的字段级校验详情。
    content = error.model_dump()
    content["errors"] = jsonable_encoder(exc.errors())
    return JSONResponse(status_code=422, content=content)


@app.get("/api/health", tags=["system"])
async def health() -> ApiResponse[dict[str, str]]:
    """报告 Inspector API 当前正在运行。"""

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
    """列出所有已配置的 MCP 服务。"""

    return ApiResponse(data=list_mcp_servers(get_server_configs()))


@app.post(
    "/api/mcp-servers",
    response_model=ApiResponse[None],
    tags=["mcp-servers"],
)
async def create_mcp_server(request: CreateMcpServerRequest) -> ApiResponse[None]:
    """校验并注册一条新的 MCP 服务配置。

    Args:
        request: 经过校验的服务创建请求数据。
    """

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
    """获取指定服务暴露的工具、资源和提示词。

    Args:
        server_id: 要查询的已配置服务标识符。
    """

    # 用于建立 MCP 连接的内部配置。
    server_config = get_server_configs().get(server_id)
    if server_config is None:
        raise HTTPException(status_code=404, detail="MCP server not found")

    try:
        # 从已配置服务获取并规范化后的能力响应。
        capabilities = await fetch_capabilities(server_id, server_config)
        return ApiResponse(data=capabilities)
    except Exception as exc:
        # 将下游连接失败转换为返回给客户端的网关错误。
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
    """返回一条已配置 MCP 服务的公开摘要信息。

    Args:
        server_id: 要返回的已配置服务标识符。
    """

    # 根据当前配置映射生成的服务摘要。
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
    """删除一条已配置的 MCP 服务。

    Args:
        server_id: 要删除的已配置服务标识符。
    """

    if not delete_server_config(server_id):
        raise HTTPException(status_code=404, detail="MCP server not found")
    return ApiResponse(data=None)
