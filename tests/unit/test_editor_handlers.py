"""Unit tests for editor handlers."""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from mcpcommander.core.editor_handlers import (
    ClaudeCodeHandler,
    ClaudeDesktopHandler,
    CursorHandler,
    EditorHandler,
    EditorHandlerFactory,
    GenericHandler,
)
from mcpcommander.schemas.config_schema import EditorConfig, ServerConfig
from mcpcommander.utils.errors import EditorError, FilePermissionError


class TestEditorHandler:
    """Test EditorHandler abstract base class functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_path = self.temp_dir / "test_config.json"
        
        self.editor_config = EditorConfig(
            config_path=str(self.config_path),
            mcp_servers={}
        )

    def create_handler(self) -> EditorHandler:
        """Create a concrete handler for testing."""
        return ClaudeCodeHandler(self.editor_config)

    def test_handler_initialization(self):
        """Test handler initialization."""
        handler = self.create_handler()
        
        assert handler.editor_config == self.editor_config
        assert handler.config_path.resolve() == self.config_path.resolve()
        assert handler.jsonpath == "mcpServers"

    def test_server_exists_true(self):
        """Test server_exists when server exists."""
        handler = self.create_handler()
        
        # Create config file with server
        config = {"mcpServers": {"test-server": {"command": "npx test"}}}
        self.config_path.write_text(json.dumps(config))
        
        assert handler.server_exists("test-server") is True

    def test_server_exists_false(self):
        """Test server_exists when server doesn't exist."""
        handler = self.create_handler()
        
        # Create config file without server
        config = {"mcpServers": {}}
        self.config_path.write_text(json.dumps(config))
        
        assert handler.server_exists("test-server") is False

    def test_get_status_file_exists(self):
        """Test get_status when config file exists."""
        handler = self.create_handler()
        
        # Create config file with servers
        config = {"mcpServers": {"server1": {}, "server2": {}}}
        self.config_path.write_text(json.dumps(config))
        
        status = handler.get_status()
        
        assert Path(status["config_path"]).resolve() == self.config_path.resolve()
        assert status["exists"] is True
        assert status["readable"] is True
        assert status["writable"] is True
        assert status["server_count"] == 2

    def test_get_status_file_not_exists(self):
        """Test get_status when config file doesn't exist."""
        handler = self.create_handler()
        
        status = handler.get_status()
        
        assert Path(status["config_path"]).resolve() == self.config_path.resolve()
        assert status["exists"] is False
        assert status["readable"] is False
        assert status["writable"] is True  # Parent directory exists
        assert status["server_count"] == 0

    def test_load_editor_config_valid(self):
        """Test loading valid editor configuration."""
        handler = self.create_handler()
        
        config = {"mcpServers": {"test": {"command": "npx test"}}}
        self.config_path.write_text(json.dumps(config))
        
        loaded = handler._load_editor_config()
        
        assert loaded == config

    def test_load_editor_config_empty_file(self):
        """Test loading empty configuration file."""
        handler = self.create_handler()
        
        self.config_path.write_text("")
        
        loaded = handler._load_editor_config()
        
        assert loaded == {}

    def test_load_editor_config_nonexistent(self):
        """Test loading non-existent configuration file."""
        handler = self.create_handler()
        
        loaded = handler._load_editor_config()
        
        assert loaded == {}

    def test_load_editor_config_invalid_json(self):
        """Test loading configuration with invalid JSON."""
        handler = self.create_handler()
        
        self.config_path.write_text("invalid json")
        
        with pytest.raises(EditorError, match="Invalid JSON"):
            handler._load_editor_config()

    @patch('builtins.open')
    def test_load_editor_config_permission_error(self, mock_open):
        """Test loading configuration with permission error."""
        handler = self.create_handler()
        
        # Create the file so that exists() check passes
        self.config_path.write_text('{"mcpServers": {}}')
        
        mock_open.side_effect = PermissionError("Access denied")
        
        with pytest.raises(FilePermissionError, match="Permission denied"):
            handler._load_editor_config()

    def test_save_editor_config_success(self):
        """Test saving editor configuration successfully."""
        handler = self.create_handler()
        
        config = {"mcpServers": {"test": {"command": "npx test"}}}
        handler._save_editor_config(config)
        
        # Verify file was created and contains correct data
        assert self.config_path.exists()
        loaded = json.loads(self.config_path.read_text())
        assert loaded == config

    def test_save_editor_config_creates_directory(self):
        """Test saving configuration creates parent directory."""
        nested_path = self.temp_dir / "nested" / "config.json"
        editor_config = EditorConfig(config_path=str(nested_path), mcp_servers={})
        handler = ClaudeCodeHandler(editor_config)
        
        config = {"mcpServers": {}}
        handler._save_editor_config(config)
        
        assert nested_path.exists()
        assert nested_path.parent.exists()

    @patch('builtins.open')
    def test_save_editor_config_permission_error(self, mock_open):
        """Test saving configuration with permission error."""
        handler = self.create_handler()
        
        mock_open.side_effect = PermissionError("Access denied")
        
        with pytest.raises(FilePermissionError, match="Permission denied"):
            handler._save_editor_config({})

    def test_get_mcp_servers_section_simple(self):
        """Test getting MCP servers section with simple jsonpath."""
        handler = self.create_handler()
        
        config = {"mcpServers": {"test": {"command": "npx test"}}}
        servers = handler._get_mcp_servers_section(config)
        
        assert servers == {"test": {"command": "npx test"}}

    def test_get_mcp_servers_section_nested(self):
        """Test getting MCP servers section with nested jsonpath."""
        nested_config = EditorConfig(
            config_path=str(self.config_path),
            jsonpath="config.mcp.servers",
            mcp_servers={}
        )
        handler = ClaudeCodeHandler(nested_config)
        
        config = {"config": {"mcp": {"servers": {"test": {"command": "npx test"}}}}}
        servers = handler._get_mcp_servers_section(config)
        
        assert servers == {"test": {"command": "npx test"}}

    def test_get_mcp_servers_section_missing(self):
        """Test getting MCP servers section when section doesn't exist."""
        handler = self.create_handler()
        
        config = {"other": "data"}
        servers = handler._get_mcp_servers_section(config)
        
        assert servers == {}

    def test_set_mcp_servers_section_simple(self):
        """Test setting MCP servers section with simple jsonpath."""
        handler = self.create_handler()
        
        config = {}
        servers = {"test": {"command": "npx test"}}
        handler._set_mcp_servers_section(config, servers)
        
        assert config["mcpServers"] == servers

    def test_set_mcp_servers_section_nested(self):
        """Test setting MCP servers section with nested jsonpath."""
        nested_config = EditorConfig(
            config_path=str(self.config_path),
            jsonpath="config.mcp.servers",
            mcp_servers={}
        )
        handler = ClaudeCodeHandler(nested_config)
        
        config = {}
        servers = {"test": {"command": "npx test"}}
        handler._set_mcp_servers_section(config, servers)
        
        assert config["config"]["mcp"]["servers"] == servers


class TestClaudeCodeHandler:
    """Test Claude Code handler functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_path = self.temp_dir / "claude_config.json"
        
        self.editor_config = EditorConfig(
            config_path=str(self.config_path),
            mcp_servers={}
        )
        self.handler = ClaudeCodeHandler(self.editor_config)

    def test_add_server_new_file(self):
        """Test adding server to new configuration file."""
        server_config = ServerConfig(command="npx test-server")
        
        self.handler.add_server("test-server", server_config)
        
        # Verify file was created and contains server
        assert self.config_path.exists()
        config = json.loads(self.config_path.read_text())
        assert "mcpServers" in config
        assert "test-server" in config["mcpServers"]
        assert config["mcpServers"]["test-server"]["command"] == "npx test-server"

    def test_add_server_existing_file(self):
        """Test adding server to existing configuration file."""
        # Create existing config
        existing_config = {"mcpServers": {"existing": {"command": "npx existing"}}}
        self.config_path.write_text(json.dumps(existing_config))
        
        server_config = ServerConfig(command="npx test-server")
        self.handler.add_server("test-server", server_config)
        
        # Verify both servers exist
        config = json.loads(self.config_path.read_text())
        assert len(config["mcpServers"]) == 2
        assert "existing" in config["mcpServers"]
        assert "test-server" in config["mcpServers"]

    def test_remove_server_success(self):
        """Test removing existing server."""
        # Create config with server
        config = {"mcpServers": {"test-server": {"command": "npx test"}}}
        self.config_path.write_text(json.dumps(config))
        
        self.handler.remove_server("test-server")
        
        # Verify server was removed
        updated_config = json.loads(self.config_path.read_text())
        assert "test-server" not in updated_config["mcpServers"]

    def test_remove_server_not_found(self):
        """Test removing non-existent server."""
        # Create config without server
        config = {"mcpServers": {}}
        self.config_path.write_text(json.dumps(config))
        
        with pytest.raises(EditorError, match="not found"):
            self.handler.remove_server("nonexistent")

    def test_list_servers_with_servers(self):
        """Test listing servers when servers exist."""
        config = {
            "mcpServers": {
                "server1": {"command": "npx server1"},
                "server2": {"command": "npx server2"}
            }
        }
        self.config_path.write_text(json.dumps(config))
        
        servers = self.handler.list_servers()
        
        assert len(servers) == 2
        assert "server1" in servers
        assert "server2" in servers

    def test_list_servers_empty(self):
        """Test listing servers when no servers exist."""
        config = {"mcpServers": {}}
        self.config_path.write_text(json.dumps(config))
        
        servers = self.handler.list_servers()
        
        assert servers == {}

    def test_list_servers_no_file(self):
        """Test listing servers when config file doesn't exist."""
        servers = self.handler.list_servers()
        
        assert servers == {}


class TestClaudeDesktopHandler:
    """Test Claude Desktop handler functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_path = self.temp_dir / "claude_desktop_config.json"
        
        self.editor_config = EditorConfig(
            config_path=str(self.config_path),
            mcp_servers={}
        )
        self.handler = ClaudeDesktopHandler(self.editor_config)

    def test_add_server(self):
        """Test adding server to Claude Desktop."""
        server_config = ServerConfig(
            command="npx @modelcontextprotocol/server-filesystem",
            args=["/path/to/files"]
        )
        
        self.handler.add_server("filesystem", server_config)
        
        # Verify server was added
        config = json.loads(self.config_path.read_text())
        assert "filesystem" in config["mcpServers"]
        assert config["mcpServers"]["filesystem"]["args"] == ["/path/to/files"]

    def test_remove_server(self):
        """Test removing server from Claude Desktop."""
        config = {"mcpServers": {"filesystem": {"command": "npx filesystem"}}}
        self.config_path.write_text(json.dumps(config))
        
        self.handler.remove_server("filesystem")
        
        updated_config = json.loads(self.config_path.read_text())
        assert "filesystem" not in updated_config["mcpServers"]

    def test_list_servers(self):
        """Test listing Claude Desktop servers."""
        config = {"mcpServers": {"filesystem": {"command": "npx filesystem"}}}
        self.config_path.write_text(json.dumps(config))
        
        servers = self.handler.list_servers()
        
        assert "filesystem" in servers


class TestCursorHandler:
    """Test Cursor handler functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_path = self.temp_dir / "cursor_config.json"
        
        self.editor_config = EditorConfig(
            config_path=str(self.config_path),
            mcp_servers={}
        )
        self.handler = CursorHandler(self.editor_config)

    def test_add_server(self):
        """Test adding server to Cursor."""
        server_config = ServerConfig(command="uvx mcp-server-sqlite")
        
        self.handler.add_server("sqlite", server_config)
        
        config = json.loads(self.config_path.read_text())
        assert "sqlite" in config["mcpServers"]

    def test_remove_server(self):
        """Test removing server from Cursor."""
        config = {"mcpServers": {"sqlite": {"command": "uvx mcp-server-sqlite"}}}
        self.config_path.write_text(json.dumps(config))
        
        self.handler.remove_server("sqlite")
        
        updated_config = json.loads(self.config_path.read_text())
        assert "sqlite" not in updated_config["mcpServers"]

    def test_list_servers(self):
        """Test listing Cursor servers."""
        config = {"mcpServers": {"sqlite": {"command": "uvx mcp-server-sqlite"}}}
        self.config_path.write_text(json.dumps(config))
        
        servers = self.handler.list_servers()
        
        assert "sqlite" in servers


class TestGenericHandler:
    """Test Generic handler functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_path = self.temp_dir / "generic_config.json"
        
        self.editor_config = EditorConfig(
            config_path=str(self.config_path),
            mcp_servers={}
        )
        self.handler = GenericHandler(self.editor_config)

    def test_add_server(self):
        """Test adding server to generic configuration."""
        server_config = ServerConfig(command="python server.py")
        
        self.handler.add_server("custom", server_config)
        
        config = json.loads(self.config_path.read_text())
        assert "custom" in config["mcpServers"]

    def test_remove_server(self):
        """Test removing server from generic configuration."""
        config = {"mcpServers": {"custom": {"command": "python server.py"}}}
        self.config_path.write_text(json.dumps(config))
        
        self.handler.remove_server("custom")
        
        updated_config = json.loads(self.config_path.read_text())
        assert "custom" not in updated_config["mcpServers"]

    def test_list_servers(self):
        """Test listing generic servers."""
        config = {"mcpServers": {"custom": {"command": "python server.py"}}}
        self.config_path.write_text(json.dumps(config))
        
        servers = self.handler.list_servers()
        
        assert "custom" in servers

    def test_custom_jsonpath(self):
        """Test generic handler with custom jsonpath."""
        custom_config = EditorConfig(
            config_path=str(self.config_path),
            jsonpath="extensions.mcp.servers",
            mcp_servers={}
        )
        handler = GenericHandler(custom_config)
        
        server_config = ServerConfig(command="python server.py")
        handler.add_server("custom", server_config)
        
        config = json.loads(self.config_path.read_text())
        assert config["extensions"]["mcp"]["servers"]["custom"]["command"] == "python server.py"


class TestEditorHandlerFactory:
    """Test EditorHandlerFactory functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_path = self.temp_dir / "config.json"
        
        self.editor_config = EditorConfig(
            config_path=str(self.config_path),
            mcp_servers={}
        )

    def test_get_handler_claude_code(self):
        """Test getting Claude Code handler."""
        handler = EditorHandlerFactory.get_handler("claude-code", self.editor_config)
        
        assert isinstance(handler, ClaudeCodeHandler)

    def test_get_handler_claude_desktop(self):
        """Test getting Claude Desktop handler."""
        handler = EditorHandlerFactory.get_handler("claude-desktop", self.editor_config)
        
        assert isinstance(handler, ClaudeDesktopHandler)

    def test_get_handler_cursor(self):
        """Test getting Cursor handler."""
        handler = EditorHandlerFactory.get_handler("cursor", self.editor_config)
        
        assert isinstance(handler, CursorHandler)

    def test_get_handler_vscode(self):
        """Test getting VS Code handler."""
        handler = EditorHandlerFactory.get_handler("vscode", self.editor_config)
        
        assert isinstance(handler, GenericHandler)

    def test_get_handler_unknown_editor(self):
        """Test getting handler for unknown editor."""
        handler = EditorHandlerFactory.get_handler("unknown-editor", self.editor_config)
        
        assert isinstance(handler, GenericHandler)

    def test_get_handler_case_insensitive(self):
        """Test getting handler is case insensitive."""
        handler = EditorHandlerFactory.get_handler("CLAUDE-CODE", self.editor_config)
        
        assert isinstance(handler, ClaudeCodeHandler)

    def test_get_supported_editors(self):
        """Test getting list of supported editors."""
        supported = EditorHandlerFactory.get_supported_editors()
        
        assert "claude-code" in supported
        assert "claude-desktop" in supported
        assert "cursor" in supported
        assert "vscode" in supported
        assert isinstance(supported, list)
        assert len(supported) > 0


class TestEditorHandlerIntegration:
    """Test integration scenarios for editor handlers."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())

    def test_multiple_servers_same_editor(self):
        """Test adding multiple servers to the same editor."""
        config_path = self.temp_dir / "multi_config.json"
        editor_config = EditorConfig(config_path=str(config_path), mcp_servers={})
        handler = ClaudeCodeHandler(editor_config)
        
        # Add multiple servers
        server1 = ServerConfig(command="npx server1")
        server2 = ServerConfig(command="npx server2", args=["--port", "3000"])
        
        handler.add_server("server1", server1)
        handler.add_server("server2", server2)
        
        # Verify both servers exist
        servers = handler.list_servers()
        assert len(servers) == 2
        assert "server1" in servers
        assert "server2" in servers
        assert servers["server2"]["args"] == ["--port", "3000"]

    def test_server_overwrite(self):
        """Test overwriting existing server."""
        config_path = self.temp_dir / "overwrite_config.json"
        editor_config = EditorConfig(config_path=str(config_path), mcp_servers={})
        handler = ClaudeCodeHandler(editor_config)
        
        # Add server
        original = ServerConfig(command="npx original")
        handler.add_server("test-server", original)
        
        # Overwrite with new config
        updated = ServerConfig(command="npx updated", args=["--new-arg"])
        handler.add_server("test-server", updated)
        
        # Verify server was overwritten
        servers = handler.list_servers()
        assert len(servers) == 1
        assert servers["test-server"]["command"] == "npx updated"
        assert servers["test-server"]["args"] == ["--new-arg"]

    def test_complex_server_config(self):
        """Test adding server with complex configuration."""
        config_path = self.temp_dir / "complex_config.json"
        editor_config = EditorConfig(config_path=str(config_path), mcp_servers={})
        handler = ClaudeCodeHandler(editor_config)
        
        # Add server with complex config
        server_config = ServerConfig(
            command="python",
            args=["-m", "server"],
            env={"PATH": "/custom/path", "DEBUG": "1"}
        )
        
        handler.add_server("complex-server", server_config)
        
        # Verify complex config was saved correctly
        servers = handler.list_servers()
        complex_server = servers["complex-server"]
        assert complex_server["command"] == "python"
        assert complex_server["args"] == ["-m", "server"]
        assert complex_server["env"]["DEBUG"] == "1"

    def test_unicode_handling(self):
        """Test handling of Unicode characters in configurations."""
        config_path = self.temp_dir / "unicode_config.json"
        editor_config = EditorConfig(config_path=str(config_path), mcp_servers={})
        handler = ClaudeCodeHandler(editor_config)
        
        # Add server with Unicode characters
        server_config = ServerConfig(
            command="npx test-server",
            args=["--path", "/测试/path", "--name", "测试服务器"]
        )
        
        handler.add_server("unicode-server", server_config)
        
        # Verify Unicode was preserved
        servers = handler.list_servers()
        unicode_server = servers["unicode-server"]
        assert "/测试/path" in unicode_server["args"]
        assert "测试服务器" in unicode_server["args"]

    @patch('mcpcommander.core.editor_handlers.logger')
    def test_logging_integration(self, mock_logger):
        """Test that handlers use logging correctly."""
        config_path = self.temp_dir / "logging_config.json"
        editor_config = EditorConfig(config_path=str(config_path), mcp_servers={})
        handler = ClaudeCodeHandler(editor_config)
        
        server_config = ServerConfig(command="npx test")
        handler.add_server("test-server", server_config)
        
        # Verify logging was called
        mock_logger.info.assert_called()
        
        handler.remove_server("test-server")
        
        # Verify removal was logged
        assert mock_logger.info.call_count >= 2