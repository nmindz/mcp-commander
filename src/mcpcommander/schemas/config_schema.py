"""Pydantic schemas for configuration validation."""

from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class HttpTransport(BaseModel):
    """Schema for HTTP transport configuration.
    
    Supports two formats:
    1. Traditional: {type: "http", host: "localhost", port: 3000, path: "/mcp"}
    2. URL-based: {type: "http", url: "https://api.example.com/mcp/", headers: {...}}
    """

    type: Literal["http"] = "http"
    
    # Traditional format fields (optional when using URL format)
    host: str | None = Field(None, description="HTTP host")
    port: int | None = Field(None, description="HTTP port")
    path: str | None = Field(None, description="HTTP path (only for host/port format)")
    
    # URL-based format fields (optional when using traditional format)
    url: str | None = Field(None, description="Full HTTP URL")
    headers: dict[str, str] | None = Field(None, description="HTTP headers")

    @field_validator("port")
    @classmethod
    def validate_port(cls, v: int | None) -> int | None:
        if v is not None and not 1 <= v <= 65535:
            raise ValueError("Port must be between 1 and 65535")
        return v

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str | None) -> str | None:
        if v is not None and not v.startswith(("http://", "https://")):
            raise ValueError("HTTP URL must start with http:// or https://")
        return v

    @model_validator(mode="after")
    def validate_http_config(self) -> "HttpTransport":
        """Validate that either URL or host/port is specified."""
        has_url = self.url is not None
        has_host_port = self.host is not None and self.port is not None
        
        if not has_url and not has_host_port:
            raise ValueError("Must specify either 'url' or both 'host' and 'port' for HTTP transport")
        
        if has_url and has_host_port:
            raise ValueError("Cannot specify both 'url' and 'host'/'port'. Use one format or the other")
        
        # Set default path for host/port format, but not for URL format
        if has_host_port and self.path is None:
            self.path = "/mcp"
        
        return self


class WebSocketTransport(BaseModel):
    """Schema for WebSocket transport configuration."""

    type: Literal["websocket"] = "websocket"
    url: str = Field(..., description="WebSocket URL")
    headers: dict[str, str] | None = Field(None, description="WebSocket headers")

    @field_validator("url")
    def validate_url(cls, v: str) -> str:
        if not v.startswith(("ws://", "wss://")):
            raise ValueError("WebSocket URL must start with ws:// or wss://")
        return v


class SSETransport(BaseModel):
    """Schema for Server-Sent Events transport configuration."""

    type: Literal["sse"] = "sse"
    url: str = Field(..., description="SSE URL")
    headers: dict[str, str] | None = Field(None, description="SSE headers")

    @field_validator("url")
    def validate_sse_url(cls, v: str) -> str:
        if not v.startswith(("http://", "https://")):
            raise ValueError("SSE URL must start with http:// or https://")
        return v


class StdioTransport(BaseModel):
    """Schema for STDIO transport configuration (traditional command-based)."""

    type: Literal["stdio"] = "stdio"
    command: str = Field(..., description="Command to execute the server")
    args: list[str] | None = Field(None, description="Command arguments")
    env: dict[str, str] | None = Field(None, description="Environment variables")

    @field_validator("command")
    def validate_command(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Command cannot be empty")
        return v.strip()


# Union type for all transport types
Transport = HttpTransport | WebSocketTransport | SSETransport | StdioTransport


class ServerConfig(BaseModel):
    """Schema for MCP server configuration supporting all transport types."""

    # For backward compatibility, allow direct command specification (STDIO)
    command: str | None = Field(None, description="Command to execute (STDIO transport)")
    args: list[str] | None = Field(None, description="Command arguments (STDIO transport)")
    env: dict[str, str] | None = Field(None, description="Environment variables")

    # New transport specification
    transport: Transport | None = Field(None, description="Transport configuration")

    @field_validator("command")
    @classmethod
    def validate_command(cls, v: str | None) -> str | None:
        """Validate and clean command."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError("Command cannot be empty")
            return v.strip()
        return v

    @model_validator(mode="after")
    def validate_server_config(self) -> "ServerConfig":
        """Validate that either command or transport is specified."""
        if self.command is not None and self.transport is not None:
            raise ValueError(
                "Cannot specify both 'command' and 'transport'. Use 'transport' for new configurations."
            )

        if self.command is None and self.transport is None:
            raise ValueError("Must specify either 'command' (legacy) or 'transport' configuration")

        # If command is specified, create a STDIO transport internally
        if self.command is not None:
            self.transport = StdioTransport(command=self.command, args=self.args, env=self.env)

        return self

    def dict(self, **kwargs: Any) -> dict[str, Any]:
        """Return dict representation suitable for MCP configuration files."""
        if isinstance(self.transport, StdioTransport):
            # For STDIO, use the legacy format for compatibility
            result: dict[str, Any] = {"command": self.transport.command}
            if self.transport.args:
                result["args"] = self.transport.args
            if self.transport.env:
                result["env"] = self.transport.env
        else:
            # For HTTP, WebSocket, and SSE transports, flatten the transport properties
            # This matches the expected MCP configuration format
            result = self.transport.model_dump(exclude_none=True) if self.transport else {}
            if self.env:
                result["env"] = self.env

        return result

    @property
    def transport_type(self) -> str:
        """Get the transport type as a string."""
        return self.transport.type if self.transport else "stdio"

    @property
    def is_stdio(self) -> bool:
        """Check if this is a STDIO transport."""
        return isinstance(self.transport, StdioTransport)

    @property
    def is_network(self) -> bool:
        """Check if this is a network-based transport."""
        return not self.is_stdio


class EditorConfig(BaseModel):
    """Schema for editor configuration."""

    config_path: str = Field(..., description="Path to editor configuration file")
    jsonpath: str = Field("mcpServers", description="JSON path to MCP servers section")

    @field_validator("config_path")
    def validate_config_path(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Configuration path cannot be empty")
        return v.strip()

    @property
    def expanded_path(self) -> Path:
        """Return expanded path with user directory resolved."""
        return Path(self.config_path).expanduser().resolve()


class MCPCommanderConfig(BaseModel):
    """Schema for main MCP Commander configuration."""

    editors: dict[str, EditorConfig] = Field(..., description="Editor configurations")

    @field_validator("editors")
    def validate_editors(cls, v: dict[str, Any]) -> dict[str, Any]:
        # Allow empty editors dict for selfdestruct/reset scenarios
        return v

    def get_editor_names(self) -> list[str]:
        """Get list of configured editor names."""
        return list(self.editors.keys())

    def get_editor_config(self, name: str) -> EditorConfig:
        """Get configuration for specific editor."""
        if name not in self.editors:
            raise ValueError(f"Unknown editor: {name}")
        return self.editors[name]


class BackupInfo(BaseModel):
    """Schema for backup information."""

    backup_id: str = Field(..., description="Unique backup identifier")
    timestamp: datetime = Field(..., description="Backup creation timestamp")
    editor_name: str | None = Field(
        None, description="Specific editor name if single-editor backup"
    )
    description: str = Field(..., description="Backup description")
    files_backed_up: list[str] = Field(
        default_factory=list, description="List of editor names backed up"
    )

    @field_validator("backup_id")
    def validate_backup_id(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Backup ID cannot be empty")
        return v.strip()

    @property
    def is_single_editor(self) -> bool:
        """Check if this is a single editor backup."""
        return self.editor_name is not None

    @property
    def display_name(self) -> str:
        """Get display name for the backup."""
        if self.editor_name:
            return f"{self.editor_name} backup"
        else:
            return "All editors backup"

    @property
    def formatted_timestamp(self) -> str:
        """Get formatted timestamp string."""
        return self.timestamp.strftime("%Y-%m-%d %H:%M:%S")


class BackupConfig(BaseModel):
    """Schema for backup configuration."""

    max_backups: int = Field(10, description="Maximum number of backups to keep", ge=1)
    backups: list[BackupInfo] = Field(
        default_factory=list, description="List of backup information"
    )

    @field_validator("max_backups")
    def validate_max_backups(cls, v: int) -> int:
        if v < 1:
            raise ValueError("Maximum backups must be at least 1")
        return v
