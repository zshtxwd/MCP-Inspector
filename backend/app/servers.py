from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator

from app.server_config import ServerConfigMap


class McpServerSummary(BaseModel):
    id: str
    name: str
    url: str
    status: Literal["connected", "disconnected"]
    transport: Literal["streamable-http"]


class CreateMcpServerRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    transport: Literal["streamable-http"]
    url: str

    @field_validator("name", "url")
    @classmethod
    def validate_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must not be blank")
        return value


def get_mcp_server_summary(
    server_id: str, server_configs: ServerConfigMap
) -> McpServerSummary | None:
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
    return [
        summary
        for server_id in server_configs
        if (summary := get_mcp_server_summary(server_id, server_configs)) is not None
    ]
