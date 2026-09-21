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
    tools: list[types.Tool]
    resources: list[types.Resource]
    resource_templates: list[types.ResourceTemplate] = Field(
        serialization_alias="resourceTemplates"
    )
    prompts: list[types.Prompt]


class CapabilitiesMeta(BaseModel):
    server_id: str = Field(serialization_alias="serverId")
    server_info: types.Implementation = Field(serialization_alias="serverInfo")
    protocol_version: str | int = Field(serialization_alias="protocolVersion")
    fetched_at: int = Field(serialization_alias="fetchedAt")


class CapabilitiesResponse(BaseModel):
    model_config = ConfigDict(serialize_by_alias=True)

    data: CapabilitiesData
    meta: CapabilitiesMeta


ListResult = TypeVar("ListResult")
ListItem = TypeVar("ListItem")


def _is_loopback_url(url: str) -> bool:
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
    items: list[ListItem] = []
    cursor: str | None = None

    while True:
        page = await fetch_page(cursor)
        items.extend(getattr(page, item_attribute))
        cursor = page.nextCursor
        if cursor is None:
            return items


async def fetch_capabilities(
    server_id: str, server_config: McpServerConfig
) -> CapabilitiesResponse:
    transport_options: dict[str, Any] = {}
    if _is_loopback_url(server_config.url):
        transport_options["httpx_client_factory"] = _create_direct_http_client

    async with streamablehttp_client(
        server_config.url,
        headers=server_config.headers,
        **transport_options,
    ) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            initialize_result = await session.initialize()
            tools = await _collect_pages(session.list_tools, "tools")
            resources = await _collect_pages(session.list_resources, "resources")
            resource_templates = await _collect_pages(
                session.list_resource_templates, "resourceTemplates"
            )
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
