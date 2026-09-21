"""MCP 服务列表、创建、查询和删除接口的 API 测试。"""

from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.server_config import McpServerConfig


def _server_configs() -> dict[str, McpServerConfig]:
    """为接口测试构造确定性的服务配置。"""

    return {
        "server-001": McpServerConfig(
            name="filesystem",
            url="http://localhost:3001",
            status="connected",
            headers={"Authorization": "Bearer test-token", "X-Client": "inspector"},
        ),
        "server-002": McpServerConfig(
            name="github",
            url="http://localhost:3002",
        ),
        "server-003": McpServerConfig(
            name=None,
            url="https://example.com/mcp",
            status="connected",
            headers={"X-Environment": "staging"},
        ),
    }


def test_list_mcp_servers(monkeypatch) -> None:
    """列表接口返回所有服务的规范化摘要。

    Args:
        monkeypatch: 用于替换配置加载逻辑的 Pytest 固件。
    """

    monkeypatch.setattr("app.main.get_server_configs", _server_configs)
    # 在进程内调用 FastAPI 应用的 HTTP 测试客户端。
    result = TestClient(app).get("/api/mcp-servers")
    assert result.status_code == 200
    assert result.json() == {
        "success": True,
        "code": 200,
        "data": [
            {
                "id": "server-001",
                "name": "filesystem",
                "url": "http://localhost:3001",
                "status": "connected",
                "transport": "streamable-http",
            },
            {
                "id": "server-002",
                "name": "github",
                "url": "http://localhost:3002",
                "status": "disconnected",
                "transport": "streamable-http",
            },
            {
                "id": "server-003",
                "name": "server-003",
                "url": "https://example.com/mcp",
                "status": "connected",
                "transport": "streamable-http",
            },
        ],
    }


def test_create_mcp_server(monkeypatch) -> None:
    """创建接口将校验后的数据传递给配置存储。

    Args:
        monkeypatch: 用于替换配置持久化逻辑的 Pytest 固件。
    """

    # 返回确定性标识符的模拟持久化函数。
    add_server = Mock(return_value="server-001")
    monkeypatch.setattr("app.main.add_server_config", add_server)
    # 创建请求返回的 HTTP 响应。
    result = TestClient(app).post(
        "/api/mcp-servers",
        json={
            "name": "filesystem",
            "transport": "streamable-http",
            "url": "http://localhost:3001",
        },
    )
    assert result.status_code == 200
    assert result.json() == {"success": True, "code": 200, "data": None}
    # 传递给模拟持久化函数的配置对象。
    config = add_server.call_args.args[0]
    assert config.name == "filesystem"
    assert config.url == "http://localhost:3001"


def test_create_mcp_server_returns_unified_validation_error() -> None:
    """不支持的传输值会返回统一的校验错误响应。"""

    # 故意构造的无效请求对应的 HTTP 响应。
    result = TestClient(app).post(
        "/api/mcp-servers",
        json={
            "name": "filesystem",
            "transport": "stdio",
            "url": "http://localhost:3001",
        },
    )
    assert result.status_code == 422
    # 解析后的 JSON 响应体，用于断言错误结构。
    body = result.json()
    assert body["success"] is False
    assert body["code"] == 422
    assert body["data"] is None
    assert body["message"] == "Request validation failed"
    assert body["errors"]


@pytest.mark.parametrize(
    "payload",
    [
        {
            "name": "   ",
            "transport": "streamable-http",
            "url": "http://localhost:3001",
        },
        {
            "name": "filesystem",
            "transport": "streamable-http",
            "url": "   ",
        },
        {
            "name": "filesystem",
            "transport": "streamable-http",
            "url": "http://localhost:3001",
            "headers": {"Authorization": "Bearer token"},
        },
    ],
)
def test_create_mcp_server_rejects_blank_or_unsupported_fields(payload) -> None:
    result = TestClient(app).post("/api/mcp-servers", json=payload)

    assert result.status_code == 422
    body = result.json()
    assert body["success"] is False
    assert body["code"] == 422
    assert body["data"] is None
    assert body["message"] == "Request validation failed"
    assert body["errors"]


def test_get_mcp_server(monkeypatch) -> None:
    """详情接口返回一条规范化的服务摘要。

    Args:
        monkeypatch: 用于替换配置加载逻辑的 Pytest 固件。
    """

    monkeypatch.setattr("app.main.get_server_configs", _server_configs)
    # 请求指定服务标识符得到的 HTTP 响应。
    result = TestClient(app).get("/api/mcp-servers/server-001")
    assert result.status_code == 200
    assert result.json() == {
        "success": True,
        "code": 200,
        "data": {
            "id": "server-001",
            "name": "filesystem",
            "url": "http://localhost:3001",
            "status": "connected",
            "transport": "streamable-http",
        },
    }


def test_delete_mcp_server(monkeypatch) -> None:
    """删除接口移除一条已存在的服务配置。

    Args:
        monkeypatch: 用于替换配置删除逻辑的 Pytest 固件。
    """

    # 报告目标服务存在的模拟删除操作。
    delete_server = Mock(return_value=True)
    monkeypatch.setattr("app.main.delete_server_config", delete_server)
    # 删除操作返回的 HTTP 响应。
    result = TestClient(app).delete("/api/mcp-servers/server-001")
    assert result.status_code == 200
    assert result.json() == {"success": True, "code": 200, "data": None}
    delete_server.assert_called_once_with("server-001")


def test_unknown_mcp_server_returns_unified_error(monkeypatch) -> None:
    """未知标识符会返回统一的 404 错误结构。

    Args:
        monkeypatch: 用于提供空配置映射的 Pytest 固件。
    """

    monkeypatch.setattr("app.main.get_server_configs", lambda: {})
    # 配置映射中不存在该标识符时返回的 HTTP 响应。
    result = TestClient(app).get("/api/mcp-servers/unknown")
    assert result.status_code == 404
    assert result.json() == {
        "success": False,
        "code": 404,
        "data": None,
        "message": "MCP server not found",
    }
