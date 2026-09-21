"""读取、缓存和修改 MCP 服务连接配置。"""

import json
import os
from functools import lru_cache
from threading import Lock
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter


class McpServerConfig(BaseModel):
    """单个 MCP 服务的连接设置。"""

    # Pydantic 配置：拒绝未定义的配置字段。
    model_config = ConfigDict(extra="forbid")

    # 连接 MCP 服务时使用的 HTTP 端点。
    url: str
    # Inspector 中显示的易读服务名称。
    name: str | None = None
    # 应用程序记录的当前连接状态。
    status: Literal["connected", "disconnected"] = "disconnected"
    # 应用程序使用的传输协议。
    transport: Literal["streamable-http"] = "streamable-http"
    # MCP 请求中发送的可选 HTTP 请求头。
    headers: dict[str, str] = Field(default_factory=dict)


# 从稳定服务标识符映射到连接设置。
ServerConfigMap = dict[str, McpServerConfig]
# 保护配置并发修改的进程内锁。
_server_configs_lock = Lock()


@lru_cache
def get_server_configs() -> ServerConfigMap:
    """返回从环境变量或默认值加载并缓存的服务映射。"""

    # MCP_SERVERS_JSON 环境变量提供的原始 JSON 配置。
    raw_configs = os.getenv("MCP_SERVERS_JSON")
    if raw_configs is None:
        return {
            "local": McpServerConfig(
                name="MCP Test Server",
                url="http://127.0.0.1:8001/mcp",
                status="connected",
            )
        }

    return TypeAdapter(ServerConfigMap).validate_python(json.loads(raw_configs))


def add_server_config(config: McpServerConfig) -> str:
    """添加一条服务配置并返回生成的标识符。

    Args:
        config: 要保存的、经过校验的连接设置。
    """

    with _server_configs_lock:
        # 保存全部已配置服务的缓存可变映射。
        server_configs = get_server_configs()
        # 生成新标识符时使用的起始数字后缀。
        sequence = 1
        # 当前候选标识符；持续递增，直到找到未使用的标识符。
        while (server_id := f"server-{sequence:03d}") in server_configs:
            sequence += 1
        server_configs[server_id] = config
        return server_id


def delete_server_config(server_id: str) -> bool:
    """按标识符删除服务，并返回该服务是否存在。

    Args:
        server_id: 要删除的配置标识符。
    """

    with _server_configs_lock:
        # 原子删除配置，并通过被删除的值判断目标是否存在。
        return get_server_configs().pop(server_id, None) is not None
