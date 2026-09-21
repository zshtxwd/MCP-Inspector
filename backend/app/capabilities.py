"""从 MCP 服务获取并规范化工具、资源和提示词。"""

import time
from collections.abc import Awaitable, Callable
from ipaddress import ip_address
from typing import Any, TypeVar
from urllib.parse import urlparse

import httpx
from mcp import ClientSession, types
from mcp.client.streamable_http import streamablehttp_client
from pydantic import BaseModel, ConfigDict, Field

from app.server_config import McpServerConfig


class CapabilitiesData(BaseModel):
    """MCP 服务声明的能力集合。"""

    # 服务可以执行的工具。
    tools: list[types.Tool]
    # 服务直接暴露的资源。
    resources: list[types.Resource]
    # 用于访问参数化资源的 URI 模板。
    resource_templates: list[types.ResourceTemplate] = Field(
        serialization_alias="resourceTemplates"
    )
    # 服务暴露的提示词模板。
    prompts: list[types.Prompt]


class CapabilitiesMeta(BaseModel):
    """描述能力获取时间和来源的元数据。"""

    # 被查询的已配置服务标识符。
    server_id: str = Field(serialization_alias="serverId")
    # 初始化期间服务返回的实现信息。
    server_info: types.Implementation = Field(serialization_alias="serverInfo")
    # 与服务协商得到的 MCP 协议版本。
    protocol_version: str | int = Field(serialization_alias="protocolVersion")
    # 能力获取完成时的 Unix 毫秒时间戳。
    fetched_at: int = Field(serialization_alias="fetchedAt")


class CapabilitiesResponse(BaseModel):
    """组合后的能力集合和获取元数据。"""

    # 配置 JSON 序列化时使用 API 的 camelCase 别名。
    model_config = ConfigDict(serialize_by_alias=True)

    # 响应体中返回的能力列表。
    data: CapabilitiesData
    # 与能力列表一起返回的服务和获取元数据。
    meta: CapabilitiesMeta


# 分页 MCP 方法返回结果对象的类型变量。
ListResult = TypeVar("ListResult")
# 从分页结果中提取的单个项目的类型变量。
ListItem = TypeVar("ListItem")


def _is_loopback_url(url: str) -> bool:
    """返回 *url* 是否指向 localhost 或回环 IP 地址。

    Args:
        url: 要检查主机名的端点 URL。
    """

    # 从 URL 中解析出的主机名，不包含端口和路径。
    hostname = urlparse(url).hostname
    if hostname is None:
        return False
    if hostname.lower() == "localhost":
        return True
    try:
        return ip_address(hostname).is_loopback
    except ValueError:
        return False


def _create_direct_http_client(
    headers: dict[str, str] | None = None,
    timeout: httpx.Timeout | None = None,
    auth: httpx.Auth | None = None,
) -> httpx.AsyncClient:
    """创建一个忽略代理环境变量的 HTTP 客户端。

    Args:
        headers: 请求使用的可选默认 HTTP 请求头。
        timeout: 可选的 HTTPX 超时配置。
        auth: 可选的 HTTPX 身份验证处理器。
    """

    return httpx.AsyncClient(
        headers=headers,
        timeout=timeout,
        auth=auth,
        trust_env=False,
    )


async def _collect_pages(
    fetch_page: Callable[[str | None], Awaitable[ListResult]],
    item_attribute: str,
) -> list[ListItem]:
    """跟随分页游标并拼接指定结果属性中的项目。

    Args:
        fetch_page: 接收当前游标的异步函数。
        item_attribute: 包含待追加项目的结果属性名。
    """

    # MCP 服务所有页面返回的累计项目。
    items: list[ListItem] = []
    # 下一页游标；传入 None 表示请求第一页。
    cursor: str | None = None

    while True:
        # 调用方提供的 MCP 列表方法返回的当前页面。
        page = await fetch_page(cursor)
        items.extend(getattr(page, item_attribute))
        cursor = page.nextCursor
        if cursor is None:
            return items


async def fetch_capabilities(
    server_id: str, server_config: McpServerConfig
) -> CapabilitiesResponse:
    """连接 MCP 服务并获取其声明的全部能力。

    Args:
        server_id: 写入响应元数据的服务标识符。
        server_config: MCP 连接使用的 URL 和请求头。
    """

    # 可选传输钩子；本地端点启用该配置以避免使用代理。
    transport_options: dict[str, Any] = {}
    if _is_loopback_url(server_config.url):
        transport_options["httpx_client_factory"] = _create_direct_http_client

    async with streamablehttp_client(
        server_config.url,
        headers=server_config.headers,
        **transport_options,
    ) as (read_stream, write_stream, _transport_context):
        async with ClientSession(read_stream, write_stream) as session:
            # 初始化元数据包含协议和实现详情。
            initialize_result = await session.initialize()
            # 完整收集的工具列表，包括所有基于游标的页面。
            tools = await _collect_pages(session.list_tools, "tools")
            # 完整收集的直接资源列表。
            resources = await _collect_pages(session.list_resources, "resources")
            # 完整收集的参数化资源模板列表。
            resource_templates = await _collect_pages(
                session.list_resource_templates, "resourceTemplates"
            )
            # 完整收集的提示词模板列表。
            prompts = await _collect_pages(session.list_prompts, "prompts")

    return CapabilitiesResponse(
        data=CapabilitiesData(
            tools=tools,
            resources=resources,
            resource_templates=resource_templates,
            prompts=prompts,
        ),
        meta=CapabilitiesMeta(
            server_id=server_id,
            server_info=initialize_result.serverInfo,
            protocol_version=initialize_result.protocolVersion,
            fetched_at=int(time.time() * 1000),
        ),
    )
