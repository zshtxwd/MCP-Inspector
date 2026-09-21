import json
import os
from functools import lru_cache
from threading import Lock
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter


class McpServerConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    url: str
    name: str | None = None
    status: Literal["connected", "disconnected"] = "disconnected"
    transport: Literal["streamable-http"] = "streamable-http"
    headers: dict[str, str] = Field(default_factory=dict)


ServerConfigMap = dict[str, McpServerConfig]
_server_configs_lock = Lock()


@lru_cache
def get_server_configs() -> ServerConfigMap:
    raw_configs = os.getenv("MCP_SERVERS_JSON")
    if raw_configs is None:
        return {
            "local": McpServerConfig(
                name="MCP Inspector",
                url="http://127.0.0.1:8000/mcp",
                status="connected",
            )
        }

    return TypeAdapter(ServerConfigMap).validate_python(json.loads(raw_configs))


def add_server_config(config: McpServerConfig) -> str:
    with _server_configs_lock:
        server_configs = get_server_configs()
        sequence = 1
        while (server_id := f"server-{sequence:03d}") in server_configs:
            sequence += 1
        server_configs[server_id] = config
        return server_id


def delete_server_config(server_id: str) -> bool:
    with _server_configs_lock:
        return get_server_configs().pop(server_id, None) is not None
