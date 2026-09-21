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


def test_get_capabilities(monkeypatch) -> None:
    """能力接口使用 API 别名序列化数据和元数据。

    Args:
        monkeypatch: 用于替换网络获取函数的 Pytest 固件。
    """

    # 模拟获取函数返回的确定性能力数据。
    response = CapabilitiesResponse(
        data=CapabilitiesData(
            tools=[types.Tool(name="ping", inputSchema={"type": "object"})],
            resources=[],
            resource_templates=[],
            prompts=[],
        ),
        meta=CapabilitiesMeta(
            server_id="local",
            server_info=types.Implementation(name="test-server", version="1.0.0"),
            protocol_version="2026-07-28",
            fetched_at=1_758_440_000_000,
        ),
    )
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
                "tools": [{"name": "ping", "inputSchema": {"type": "object"}}],
                "resources": [],
                "resourceTemplates": [],
                "prompts": [],
            },
            "meta": {
                "serverId": "local",
                "serverInfo": {"name": "test-server", "version": "1.0.0"},
                "protocolVersion": "2026-07-28",
                "fetchedAt": 1_758_440_000_000,
            },
        },
    }


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
async def test_collect_pages_follows_next_cursor() -> None:
    """分页辅助函数会跟随游标并保持项目顺序。"""

    # 模拟列表操作返回的两个页面。
    fetch_page = AsyncMock(
        side_effect=[
            types.ListToolsResult(
                tools=[types.Tool(name="first", inputSchema={"type": "object"})],
                nextCursor="next-page",
            ),
            types.ListToolsResult(
                tools=[types.Tool(name="second", inputSchema={"type": "object"})]
            ),
        ]
    )

    # 获取所有页面后合并得到的项目。
    tools = await _collect_pages(fetch_page, "tools")

    assert [tool.name for tool in tools] == ["first", "second"]
    assert [call.args for call in fetch_page.await_args_list] == [(None,), ("next-page",)]


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("http://localhost:8000/mcp", True),
        ("http://127.0.0.1:8000/mcp", True),
        ("http://[::1]:8000/mcp", True),
        ("https://example.com/mcp", False),
    ],
)
def test_is_loopback_url(url: str, expected: bool) -> None:
    """能够识别回环主机，并拒绝公共主机。

    Args:
        url: 传给辅助函数的参数化 URL。
        expected: ``url`` 预期的回环地址判断结果。
    """

    assert _is_loopback_url(url) is expected
