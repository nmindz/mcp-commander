"""Unit tests for Pydantic schemas."""

from pathlib import Path

import pytest

from mcpcommander.schemas.config_schema import EditorConfig, MCPCommanderConfig, ServerConfig, HttpTransport


class TestHttpTransport:
    """Test HttpTransport schema."""

    def test_valid_host_port_format(self):
        """Test valid host/port HTTP transport configuration."""
        transport = HttpTransport(host="localhost", port=3000)
        assert transport.type == "http"
        assert transport.host == "localhost"
        assert transport.port == 3000
        assert transport.path == "/mcp"  # Default value
        assert transport.url is None
        assert transport.headers is None

    def test_valid_url_format(self):
        """Test valid URL-based HTTP transport configuration."""
        transport = HttpTransport(url="https://api.github.com/mcp/")
        assert transport.type == "http"
        assert transport.url == "https://api.github.com/mcp/"
        assert transport.host is None
        assert transport.port is None
        assert transport.headers is None

    def test_valid_url_format_with_headers(self):
        """Test valid URL-based HTTP transport with headers."""
        transport = HttpTransport(
            url="https://api.github.com/mcp/",
            headers={"Authorization": "Bearer token123"}
        )
        assert transport.type == "http"
        assert transport.url == "https://api.github.com/mcp/"
        assert transport.headers == {"Authorization": "Bearer token123"}

    def test_github_mcp_server_format(self):
        """Test GitHub MCP server configuration format."""
        transport = HttpTransport(
            url="https://api.githubcopilot.com/mcp/",
            headers={"Authorization": "Bearer $GITHUB_PAT"}
        )
        assert transport.type == "http"
        assert transport.url == "https://api.githubcopilot.com/mcp/"
        assert transport.headers == {"Authorization": "Bearer $GITHUB_PAT"}

    def test_missing_both_url_and_host_port_fails(self):
        """Test that missing both URL and host/port fails validation."""
        with pytest.raises(ValueError, match="Must specify either 'url' or both 'host' and 'port'"):
            HttpTransport()

    def test_missing_port_with_host_fails(self):
        """Test that providing host without port fails validation."""
        with pytest.raises(ValueError, match="Must specify either 'url' or both 'host' and 'port'"):
            HttpTransport(host="localhost")

    def test_missing_host_with_port_fails(self):
        """Test that providing port without host fails validation."""
        with pytest.raises(ValueError, match="Must specify either 'url' or both 'host' and 'port'"):
            HttpTransport(port=3000)

    def test_both_url_and_host_port_fails(self):
        """Test that providing both URL and host/port fails validation."""
        with pytest.raises(ValueError, match="Cannot specify both 'url' and 'host'/'port'"):
            HttpTransport(url="https://api.github.com/mcp/", host="localhost", port=3000)

    def test_invalid_port_range(self):
        """Test invalid port range validation."""
        with pytest.raises(ValueError, match="Port must be between 1 and 65535"):
            HttpTransport(host="localhost", port=0)
        
        with pytest.raises(ValueError, match="Port must be between 1 and 65535"):
            HttpTransport(host="localhost", port=65536)

    def test_invalid_url_scheme(self):
        """Test invalid URL scheme validation."""
        with pytest.raises(ValueError, match="HTTP URL must start with http:// or https://"):
            HttpTransport(url="ftp://api.github.com/mcp/")
        
        with pytest.raises(ValueError, match="HTTP URL must start with http:// or https://"):
            HttpTransport(url="ws://api.github.com/mcp/")

    def test_model_dump_excludes_none_values(self):
        """Test that model_dump excludes None values."""
        # URL-based format
        transport_url = HttpTransport(url="https://api.github.com/mcp/")
        dumped = transport_url.model_dump(exclude_none=True)
        expected = {
            "type": "http",
            "url": "https://api.github.com/mcp/",
            "path": "/mcp"
        }
        assert dumped == expected

        # Host/port format
        transport_host_port = HttpTransport(host="localhost", port=3000)
        dumped = transport_host_port.model_dump(exclude_none=True)
        expected = {
            "type": "http",
            "host": "localhost",
            "port": 3000,
            "path": "/mcp"
        }
        assert dumped == expected


class TestServerConfig:
    """Test ServerConfig schema."""

    def test_valid_server_config_minimal(self):
        """Test valid minimal server configuration."""
        config = ServerConfig(command="test-command")
        assert config.command == "test-command"
        assert config.args is None
        assert config.env is None

    def test_valid_server_config_full(self):
        """Test valid full server configuration."""
        config = ServerConfig(
            command="test-command", args=["arg1", "arg2"], env={"VAR1": "value1", "VAR2": "value2"}
        )
        assert config.command == "test-command"
        assert config.args == ["arg1", "arg2"]
        assert config.env == {"VAR1": "value1", "VAR2": "value2"}

    def test_server_config_dict_excludes_none(self):
        """Test ServerConfig.dict() excludes None values."""
        config = ServerConfig(command="test-command")
        config_dict = config.dict()

        assert config_dict == {"command": "test-command"}
        assert "args" not in config_dict
        assert "env" not in config_dict

    def test_server_config_dict_includes_values(self):
        """Test ServerConfig.dict() includes non-None values."""
        config = ServerConfig(command="test-command", args=["arg1"], env={"VAR": "value"})
        config_dict = config.dict()

        assert config_dict == {"command": "test-command", "args": ["arg1"], "env": {"VAR": "value"}}

    def test_empty_command_validation(self):
        """Test empty command validation."""
        with pytest.raises(ValueError, match="Command cannot be empty"):
            ServerConfig(command="")

    def test_whitespace_command_validation(self):
        """Test whitespace-only command validation."""
        with pytest.raises(ValueError, match="Command cannot be empty"):
            ServerConfig(command="   ")

    def test_command_strip(self):
        """Test command whitespace stripping."""
        config = ServerConfig(command="  test-command  ")
        assert config.command == "test-command"


class TestEditorConfig:
    """Test EditorConfig schema."""

    def test_valid_editor_config_minimal(self):
        """Test valid minimal editor configuration."""
        config = EditorConfig(config_path="/path/to/config.json")
        assert config.config_path == "/path/to/config.json"
        assert config.jsonpath == "mcpServers"  # Default value

    def test_valid_editor_config_full(self):
        """Test valid full editor configuration."""
        config = EditorConfig(config_path="/path/to/config.json", jsonpath="custom.path")
        assert config.config_path == "/path/to/config.json"
        assert config.jsonpath == "custom.path"

    def test_expanded_path_property(self):
        """Test expanded_path property."""
        config = EditorConfig(config_path="~/config.json")
        expanded = config.expanded_path

        assert isinstance(expanded, Path)
        assert expanded.is_absolute()  # Cross-platform absolute path check
        assert "~" not in str(expanded)  # Should be expanded

    def test_empty_config_path_validation(self):
        """Test empty config path validation."""
        with pytest.raises(ValueError, match="Configuration path cannot be empty"):
            EditorConfig(config_path="")

    def test_whitespace_config_path_validation(self):
        """Test whitespace-only config path validation."""
        with pytest.raises(ValueError, match="Configuration path cannot be empty"):
            EditorConfig(config_path="   ")

    def test_config_path_strip(self):
        """Test config path whitespace stripping."""
        config = EditorConfig(config_path="  /path/to/config.json  ")
        assert config.config_path == "/path/to/config.json"


class TestMCPCommanderConfig:
    """Test MCPCommanderConfig schema."""

    def test_valid_commander_config(self):
        """Test valid MCP Commander configuration."""
        editors = {
            "claude-code": EditorConfig(config_path="/path/to/claude.json"),
            "cursor": EditorConfig(config_path="/path/to/cursor.json"),
        }

        config = MCPCommanderConfig(editors=editors)
        assert len(config.editors) == 2
        assert "claude-code" in config.editors
        assert "cursor" in config.editors

    def test_get_editor_names(self):
        """Test get_editor_names method."""
        editors = {
            "claude-code": EditorConfig(config_path="/path/to/claude.json"),
            "cursor": EditorConfig(config_path="/path/to/cursor.json"),
        }

        config = MCPCommanderConfig(editors=editors)
        names = config.get_editor_names()

        assert isinstance(names, list)
        assert len(names) == 2
        assert "claude-code" in names
        assert "cursor" in names

    def test_get_editor_config(self):
        """Test get_editor_config method."""
        editors = {"claude-code": EditorConfig(config_path="/path/to/claude.json")}

        config = MCPCommanderConfig(editors=editors)
        editor_config = config.get_editor_config("claude-code")

        assert isinstance(editor_config, EditorConfig)
        assert editor_config.config_path == "/path/to/claude.json"

    def test_get_unknown_editor_config(self):
        """Test get_editor_config with unknown editor."""
        editors = {"claude-code": EditorConfig(config_path="/path/to/claude.json")}

        config = MCPCommanderConfig(editors=editors)

        with pytest.raises(ValueError, match="Unknown editor"):
            config.get_editor_config("unknown-editor")

    def test_empty_editors_validation(self):
        """Test empty editors validation (now allowed for config reset)."""
        # Empty editors is now allowed for config reset functionality
        config = MCPCommanderConfig(editors={})
        assert config.editors == {}
        assert config.get_editor_names() == []

    def test_server_config_with_http_transport_url(self):
        """Test ServerConfig with HTTP transport using URL format."""
        transport = HttpTransport(
            url="https://api.githubcopilot.com/mcp/",
            headers={"Authorization": "Bearer $GITHUB_PAT"}
        )
        config = ServerConfig(transport=transport, env={"GITHUB_PAT": "ghp_token123"})
        
        assert config.transport == transport
        assert config.command is None
        assert config.env == {"GITHUB_PAT": "ghp_token123"}
        
        # Test dict output format
        config_dict = config.dict()
        expected = {
            "transport": {
                "type": "http",
                "url": "https://api.githubcopilot.com/mcp/",
                "headers": {"Authorization": "Bearer $GITHUB_PAT"},
                "path": "/mcp"
            },
            "env": {"GITHUB_PAT": "ghp_token123"}
        }
        assert config_dict == expected

    def test_server_config_with_http_transport_host_port(self):
        """Test ServerConfig with HTTP transport using host/port format."""
        transport = HttpTransport(host="localhost", port=3000, path="/api/mcp")
        config = ServerConfig(transport=transport)
        
        assert config.transport == transport
        assert config.command is None
        
        # Test dict output format
        config_dict = config.dict()
        expected = {
            "transport": {
                "type": "http",
                "host": "localhost",
                "port": 3000,
                "path": "/api/mcp"
            }
        }
        assert config_dict == expected
