from unittest.mock import Mock

from fastapi.testclient import TestClient

from app.main import app
from app.server_config import McpServerConfig


def _server_configs() -> dict[str, McpServerConfig]:
    return {
        "server-001": McpServerConfig(
            name="filesystem",
            url="http://localhost:3001",
            status="connected",
        ),
        "server-002": McpServerConfig(
            name="github",
            url="http://localhost:3002",
        ),
    }


def test_list_mcp_servers(monkeypatch) -> None:
    monkeypatch.setattr("app.main.get_server_configs", _server_configs)
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
        ],
    }


def test_create_mcp_server(monkeypatch) -> None:
    add_server = Mock(return_value="server-001")
    monkeypatch.setattr("app.main.add_server_config", add_server)
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
    config = add_server.call_args.args[0]
    assert config.name == "filesystem"
    assert config.url == "http://localhost:3001"


def test_create_mcp_server_returns_unified_validation_error() -> None:
    result = TestClient(app).post(
        "/api/mcp-servers",
        json={
            "name": "filesystem",
            "transport": "stdio",
            "url": "http://localhost:3001",
        },
    )
    assert result.status_code == 422
    body = result.json()
    assert body["success"] is False
    assert body["code"] == 422
    assert body["data"] is None
    assert body["message"] == "Request validation failed"
    assert body["errors"]


def test_get_mcp_server(monkeypatch) -> None:
    monkeypatch.setattr("app.main.get_server_configs", _server_configs)
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
    delete_server = Mock(return_value=True)
    monkeypatch.setattr("app.main.delete_server_config", delete_server)
    result = TestClient(app).delete("/api/mcp-servers/server-001")
    assert result.status_code == 200
    assert result.json() == {"success": True, "code": 200, "data": None}
    delete_server.assert_called_once_with("server-001")


def test_unknown_mcp_server_returns_unified_error(monkeypatch) -> None:
    monkeypatch.setattr("app.main.get_server_configs", lambda: {})
    result = TestClient(app).get("/api/mcp-servers/unknown")
    assert result.status_code == 404
    assert result.json() == {
        "success": False,
        "code": 404,
        "data": None,
        "message": "MCP server not found",
    }
