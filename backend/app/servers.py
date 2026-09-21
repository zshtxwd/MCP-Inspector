"""MCP 服务 API 资源的 Pydantic 模型和辅助函数。"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator

from app.server_config import ServerConfigMap


class McpServerSummary(BaseModel):
    """REST API 返回的 MCP 服务公开信息。"""

    # 为配置的服务分配的稳定标识符。
    id: str
    # Inspector 界面中显示的服务名称。
    name: str
    # MCP 可流式传输 HTTP 端点。
    url: str
    # 服务当前是否处于连接状态。
    status: Literal["connected", "disconnected"]
    # API 对外提供的传输方式。
    transport: Literal["streamable-http"]


class CreateMcpServerRequest(BaseModel):
    """创建 MCP 服务时接收的、经过校验的请求数据。"""

    # Pydantic 配置：拒绝未定义的请求字段。
    model_config = ConfigDict(extra="forbid")

    # 用户提供的显示名称。
    name: str
    # 请求使用的传输方式，目前仅支持可流式传输 HTTP。
    transport: Literal["streamable-http"]
    # 用户提供的端点 URL。
    url: str

    @field_validator("name", "url")
    @classmethod
    def validate_not_blank(cls, value: str) -> str:
        """拒绝只包含空白字符的名称和 URL。

        Args:
            cls: 调用此校验器的 Pydantic 模型类。
            value: 正在校验的名称或 URL。
        """

        if not value.strip():
            raise ValueError("must not be blank")
        return value


def get_mcp_server_summary(
    server_id: str, server_configs: ServerConfigMap
) -> McpServerSummary | None:
    """将一条内部配置转换为 API 摘要信息。

    Args:
        server_id: 要在 ``server_configs`` 中查找的服务标识符。
        server_configs: 当前配置的 MCP 服务映射。
    """

    # 根据稳定服务标识符查找到的配置。
    config = server_configs.get(server_id)
    if config is None:
        return None
    return McpServerSummary(
        id=server_id,
        name=config.name or server_id,
        url=config.url,
        status=config.status,
        transport=config.transport,
    )


def list_mcp_servers(server_configs: ServerConfigMap) -> list[McpServerSummary]:
    """为每个已配置的 MCP 服务生成摘要信息。"""

    return [
        # 当前服务标识符对应的摘要信息。
        summary
        for server_id in server_configs
        if (summary := get_mcp_server_summary(server_id, server_configs)) is not None
    ]
