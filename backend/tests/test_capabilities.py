"""能力接口和 MCP 分页辅助函数的测试。"""

from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from mcp import types

from app.capabilities import (
    CapabilitiesData,
    CapabilitiesMeta,
    CapabilitiesResponse,
    _collect_pages,
    _is_loopback_url,
)
from app.main import app


def _capabilities_response() -> CapabilitiesResponse:
    """构造包含全部 MCP 能力类型的代表性响应数据。"""

    return CapabilitiesResponse(
        data=CapabilitiesData(
            tools=[
                types.Tool(
                    name="search_files",
                    title="Search files",
                    description="Find files by name or contents.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"},
                            "path": {"type": "string", "default": "."},
                        },
                        "required": ["query"],
                    },
                ),
                types.Tool(
                    name="read_file",
                    description="Read a UTF-8 text file.",
                    inputSchema={
                        "type": "object",
                        "properties": {"path": {"type": "string"}},
                        "required": ["path"],
                    },
                ),
            ],
            resources=[
                types.Resource(
                    name="Project README",
                    uri="workspace://README.md",
                    description="Project documentation.",
                    mimeType="text/markdown",
                ),
                types.Resource(
                    name="Latest logs",
                    uri="logs://latest",
                    mimeType="text/plain",
                ),
            ],
            resource_templates=[
                types.ResourceTemplate(
                    name="Workspace file",
                    uriTemplate="workspace://{path}",
                    description="Read a file from the workspace.",
                    mimeType="text/plain",
                )
            ],
            prompts=[
                types.Prompt(
                    name="code_review",
                    description="Review a code change for correctness.",
                    arguments=[
                        types.PromptArgument(
                            name="diff", description="The diff to review", required=True
                        ),
                        types.PromptArgument(
                            name="focus", description="Optional review focus", required=False
                        ),
                    ],
                )
            ],
        ),
        meta=CapabilitiesMeta(
            server_id="local",
            server_info=types.Implementation(
                name="MCP Test Server", version="1.2.0", websiteUrl="https://example.com"
            ),
            protocol_version="2025-06-18",
            fetched_at=1_758_440_000_000,
        ),
    )


def test_get_capabilities_serializes_all_capability_types(monkeypatch) -> None:
    """能力接口使用 API 别名序列化完整能力数据和元数据。

    Args:
        monkeypatch: 用于替换网络获取函数的 Pytest 固件。
    """

    # 模拟获取函数返回的确定性能力数据。
    response = _capabilities_response()
    # 替代网络能力获取函数的异步模拟对象。
    fetch_mock = AsyncMock(return_value=response)
    monkeypatch.setattr("app.main.fetch_capabilities", fetch_mock)

    # 被测试接口返回的 HTTP 响应。
    result = TestClient(app).get("/api/mcp-servers/local/capabilities")

    assert result.status_code == 200
    assert result.json() == {
        "success": True,
        "code": 200,
        "data": {
            "data": {
                "tools": [
                    {
                        "name": "search_files",
                        "title": "Search files",
                        "description": "Find files by name or contents.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string"},
                                "path": {"type": "string", "default": "."},
                            },
                            "required": ["query"],
                        },
                    },
                    {
                        "name": "read_file",
                        "description": "Read a UTF-8 text file.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {"path": {"type": "string"}},
                            "required": ["path"],
                        },
                    },
                ],
                "resources": [
                    {
                        "name": "Project README",
                        "uri": "workspace://README.md",
                        "description": "Project documentation.",
                        "mimeType": "text/markdown",
                    },
                    {
                        "name": "Latest logs",
                        "uri": "logs://latest",
                        "mimeType": "text/plain",
                    },
                ],
                "resourceTemplates": [
                    {
                        "name": "Workspace file",
                        "uriTemplate": "workspace://{path}",
                        "description": "Read a file from the workspace.",
                        "mimeType": "text/plain",
                    }
                ],
                "prompts": [
                    {
                        "name": "code_review",
                        "description": "Review a code change for correctness.",
                        "arguments": [
                            {
                                "name": "diff",
                                "description": "The diff to review",
                                "required": True,
                            },
                            {
                                "name": "focus",
                                "description": "Optional review focus",
                                "required": False,
                            },
                        ],
                    }
                ],
            },
            "meta": {
                "serverId": "local",
                "serverInfo": {
                    "name": "MCP Test Server",
                    "version": "1.2.0",
                    "websiteUrl": "https://example.com",
                },
                "protocolVersion": "2025-06-18",
                "fetchedAt": 1_758_440_000_000,
            },
        },
    }
    fetch_mock.assert_awaited_once()


def test_get_capabilities_returns_404_for_unknown_server() -> None:
    """能力接口拒绝配置中不存在的服务标识符。"""

    # 未知服务标识符对应的 HTTP 响应。
    result = TestClient(app).get("/api/mcp-servers/unknown/capabilities")

    assert result.status_code == 404
    assert result.json() == {
        "success": False,
        "code": 404,
        "data": None,
        "message": "MCP server not found",
    }


@pytest.mark.anyio
async def test_collect_pages_follows_next_cursor_for_each_capability_type() -> None:
    """分页辅助函数会跟随游标并保持四类能力项目的顺序。"""

    # 模拟列表操作返回的两个页面。
    # 分别覆盖工具、资源、资源模板和提示词。
    pages = {
        "tools": (
            types.ListToolsResult(
                tools=[types.Tool(name="search_files", inputSchema={"type": "object"})],
                nextCursor="tools-page-2",
            ),
            types.ListToolsResult(
                tools=[types.Tool(name="read_file", inputSchema={"type": "object"})]
            ),
        ),
        "resources": (
            types.ListResourcesResult(
                resources=[types.Resource(name="README", uri="workspace://README.md")],
                nextCursor="resources-page-2",
            ),
            types.ListResourcesResult(
                resources=[types.Resource(name="logs", uri="logs://latest")]
            ),
        ),
        "resourceTemplates": (
            types.ListResourceTemplatesResult(
                resourceTemplates=[
                    types.ResourceTemplate(name="file", uriTemplate="workspace://{path}")
                ],
                nextCursor="resourceTemplates-page-2",
            ),
            types.ListResourceTemplatesResult(
                resourceTemplates=[
                    types.ResourceTemplate(name="issue", uriTemplate="issue://{number}")
                ]
            ),
        ),
        "prompts": (
            types.ListPromptsResult(
                prompts=[types.Prompt(name="code_review")], nextCursor="prompts-page-2"
            ),
            types.ListPromptsResult(prompts=[types.Prompt(name="summarize")]),
        ),
    }

    for item_attribute, (first_page, second_page) in pages.items():
        fetch_page = AsyncMock(side_effect=[first_page, second_page])
        # 获取所有页面后合并得到的项目。
        items = await _collect_pages(fetch_page, item_attribute)

        first_items = getattr(first_page, item_attribute)
        second_items = getattr(second_page, item_attribute)
        assert [item.name for item in items] == [
            first_items[0].name,
            second_items[0].name,
        ]
        assert [call.args for call in fetch_page.await_args_list] == [
            (None,),
            (first_page.nextCursor,),
        ]


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("http://localhost:8000/mcp", True),
        ("http://LOCALHOST:8000/mcp", True),
        ("http://127.0.0.1:8000/mcp", True),
        ("http://[::1]:8000/mcp", True),
        ("https://example.com/mcp", False),
        ("not-a-url", False),
    ],
)
def test_is_loopback_url(url: str, expected: bool) -> None:
    """能够识别回环主机，并拒绝公共主机。

    Args:
        url: 传给辅助函数的参数化 URL。
        expected: ``url`` 预期的回环地址判断结果。
    """

    assert _is_loopback_url(url) is expected
