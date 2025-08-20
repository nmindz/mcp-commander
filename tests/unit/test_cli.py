"""Unit tests for CLI interface."""

import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock
from pathlib import Path

from mcpcommander.cli.main import app
from mcpcommander.utils.errors import MCPCommanderError


class TestCLICommands:
    """Test main CLI commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_version_command(self):
        """Test version command."""
        result = self.runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "1.0.0" in result.stdout

    def test_help_command(self):
        """Test help command."""
        result = self.runner.invoke(app, ["help"])
        assert result.exit_code == 0
        assert "MCP Commander" in result.stdout

    def test_examples_command(self):
        """Test examples command."""
        result = self.runner.invoke(app, ["examples"])
        assert result.exit_code == 0
        # Should show examples without errors

    @patch('mcpcommander.cli.main.MCPManager')
    def test_editors_command(self, mock_manager_class):
        """Test editors command."""
        mock_manager = MagicMock()
        mock_manager.get_available_editors.return_value = ["claude-code", "cursor"]
        mock_manager_class.return_value = mock_manager

        result = self.runner.invoke(app, ["editors"])
        assert result.exit_code == 0
        mock_manager.get_available_editors.assert_called_once()

    @patch('mcpcommander.cli.main.MCPManager')
    def test_discover_command(self, mock_manager_class):
        """Test discover command."""
        mock_manager = MagicMock()
        mock_manager.populate_config_with_discovered.return_value = {}
        mock_manager_class.return_value = mock_manager

        result = self.runner.invoke(app, ["discover"])
        assert result.exit_code == 0
        mock_manager.print_discovery_report.assert_called_once()
        mock_manager.populate_config_with_discovered.assert_called_once()


class TestConfigSubcommands:
    """Test mcp config subcommands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch('mcpcommander.cli.main.MCPManager')
    def test_config_servers_command(self, mock_manager_class):
        """Test config servers command."""
        mock_manager = MagicMock()
        mock_manager.list_servers.return_value = {
            "claude-code": {"filesystem": {"command": "npx server"}}
        }
        mock_manager_class.return_value = mock_manager

        result = self.runner.invoke(app, ["config", "servers"])
        assert result.exit_code == 0
        mock_manager.list_servers.assert_called_once()

    @patch('mcpcommander.cli.main.MCPManager')
    def test_config_servers_with_editor(self, mock_manager_class):
        """Test config servers command with specific editor."""
        mock_manager = MagicMock()
        mock_manager.list_servers.return_value = {
            "claude-code": {"filesystem": {"command": "npx server"}}
        }
        mock_manager_class.return_value = mock_manager

        result = self.runner.invoke(app, ["config", "servers", "claude-code"])
        assert result.exit_code == 0
        mock_manager.list_servers.assert_called_once_with("claude-code")

    @patch('mcpcommander.cli.main.MCPManager')
    def test_config_show_command(self, mock_manager_class):
        """Test config show command."""
        mock_manager = MagicMock()
        mock_manager.get_status.return_value = {
            "configuration_file": "/path/to/config.json",
            "editors": {"claude-code": {"status": "configured"}}
        }
        mock_manager_class.return_value = mock_manager

        result = self.runner.invoke(app, ["config", "show"])
        assert result.exit_code == 0
        mock_manager.get_status.assert_called_once()

    @patch('mcpcommander.cli.main.MCPManager')
    def test_config_path_command(self, mock_manager_class):
        """Test config path command."""
        mock_manager = MagicMock()
        mock_manager.get_config_path.return_value = Path("/path/to/config.json")
        mock_manager_class.return_value = mock_manager

        result = self.runner.invoke(app, ["config", "path"])
        assert result.exit_code == 0
        mock_manager.get_config_path.assert_called_once()

    @patch('mcpcommander.cli.main.MCPManager')
    @patch('mcpcommander.cli.main.confirm_action')
    def test_config_reset_command(self, mock_confirm, mock_manager_class):
        """Test config reset command."""
        mock_confirm.return_value = True
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager

        result = self.runner.invoke(app, ["config", "reset"])
        assert result.exit_code == 0
        mock_manager.reset_configuration.assert_called_once_with(include_backups=False)

    @patch('mcpcommander.cli.main.MCPManager')
    def test_config_reset_with_force(self, mock_manager_class):
        """Test config reset command with force flag."""
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager

        result = self.runner.invoke(app, ["config", "reset", "--force"])
        assert result.exit_code == 0
        mock_manager.reset_configuration.assert_called_once_with(include_backups=False)

    @patch('mcpcommander.cli.main.MCPManager')
    @patch('mcpcommander.cli.main.confirm_action')
    def test_config_reset_with_backups(self, mock_confirm, mock_manager_class):
        """Test config reset command with include-backups flag."""
        mock_confirm.return_value = True
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager

        result = self.runner.invoke(app, ["config", "reset", "--include-backups"])
        assert result.exit_code == 0
        mock_manager.reset_configuration.assert_called_once_with(include_backups=True)

    def test_config_help_command(self):
        """Test config help command."""
        result = self.runner.invoke(app, ["config", "help"])
        assert result.exit_code == 0
        assert "config" in result.stdout.lower()


class TestServerManagement:
    """Test server add/remove commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch('mcpcommander.cli.main.MCPManager')
    def test_add_server_command(self, mock_manager_class):
        """Test add server command."""
        mock_manager = MagicMock()
        mock_manager.add_server.return_value = {
            "successful": ["claude-code"],
            "failed": [],
            "results": {"claude-code": "Success"}
        }
        mock_manager_class.return_value = mock_manager

        result = self.runner.invoke(app, ["add", "server", "test-server", "npx test-server"])
        assert result.exit_code == 0
        mock_manager.add_server.assert_called_once_with("test-server", "npx test-server", None, {})

    @patch('mcpcommander.cli.main.MCPManager')
    def test_add_server_with_editor(self, mock_manager_class):
        """Test add server command with specific editor."""
        mock_manager = MagicMock()
        mock_manager.add_server.return_value = {
            "successful": ["claude-code"],
            "failed": [],
            "results": {"claude-code": "Success"}
        }
        mock_manager_class.return_value = mock_manager

        result = self.runner.invoke(app, ["add", "server", "test-server", "npx test-server", "claude-code"])
        assert result.exit_code == 0
        mock_manager.add_server.assert_called_once_with("test-server", "npx test-server", "claude-code", {})

    @patch('mcpcommander.cli.main.MCPManager')
    def test_remove_server_command(self, mock_manager_class):
        """Test remove server command."""
        mock_manager = MagicMock()
        mock_manager.remove_server.return_value = {
            "successful": ["claude-code"],
            "failed": [],
            "results": {"claude-code": "Success"}
        }
        mock_manager_class.return_value = mock_manager

        result = self.runner.invoke(app, ["remove", "server", "test-server"])
        assert result.exit_code == 0
        mock_manager.remove_server.assert_called_once_with("test-server", None)

    @patch('mcpcommander.cli.main.MCPManager')
    def test_remove_server_with_editor(self, mock_manager_class):
        """Test remove server command with specific editor."""
        mock_manager = MagicMock()
        mock_manager.remove_server.return_value = {
            "successful": ["claude-code"],
            "failed": [],
            "results": {"claude-code": "Success"}
        }
        mock_manager_class.return_value = mock_manager

        result = self.runner.invoke(app, ["remove", "server", "test-server", "claude-code"])
        assert result.exit_code == 0
        mock_manager.remove_server.assert_called_once_with("test-server", "claude-code")


class TestBackupSubcommands:
    """Test mcp backup subcommands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch('mcpcommander.cli.main.MCPManager')
    def test_backup_create_command(self, mock_manager_class):
        """Test backup create command."""
        mock_manager = MagicMock()
        mock_backup_info = MagicMock()
        mock_backup_info.backup_id = "backup_123"
        mock_manager.create_backup.return_value = mock_backup_info
        mock_manager_class.return_value = mock_manager

        result = self.runner.invoke(app, ["backup", "create"])
        assert result.exit_code == 0
        mock_manager.create_backup.assert_called_once_with(editor_name=None, description=None)

    @patch('mcpcommander.cli.main.MCPManager')
    def test_backup_create_with_editor(self, mock_manager_class):
        """Test backup create command with specific editor."""
        mock_manager = MagicMock()
        mock_backup_info = MagicMock()
        mock_backup_info.backup_id = "backup_123"
        mock_manager.create_backup.return_value = mock_backup_info
        mock_manager_class.return_value = mock_manager

        result = self.runner.invoke(app, ["backup", "create", "claude-code", "--no-interactive"])
        assert result.exit_code == 0
        mock_manager.create_backup.assert_called_once_with(editor_name="claude-code", description=None)

    @patch('mcpcommander.cli.main.MCPManager')
    def test_backup_list_command(self, mock_manager_class):
        """Test backup list command."""
        mock_manager = MagicMock()
        mock_backup_info = MagicMock()
        mock_backup_info.backup_id = "backup_123"
        mock_backup_info.formatted_timestamp = "2025-08-18 10:00:00"
        mock_backup_info.display_name = "All editors backup"
        mock_backup_info.files_backed_up = ["claude-code", "cursor"]
        mock_backup_info.description = "Test backup"
        mock_manager.list_backups.return_value = [mock_backup_info]
        mock_manager_class.return_value = mock_manager

        result = self.runner.invoke(app, ["backup", "list"])
        assert result.exit_code == 0
        mock_manager.list_backups.assert_called_once_with(None)

    @patch('mcpcommander.cli.main.MCPManager')
    @patch('mcpcommander.cli.main.select_backup')
    def test_backup_restore_interactive(self, mock_select, mock_manager_class):
        """Test backup restore command with interactive selection."""
        mock_manager = MagicMock()
        mock_backup_info = MagicMock()
        mock_backup_info.backup_id = "backup_123"
        mock_backup_info.formatted_timestamp = "2025-08-18 10:00:00"
        mock_backup_info.description = "Test backup"
        mock_backup_info.files_backed_up = ["claude-code"]
        mock_manager.list_backups.return_value = [mock_backup_info]
        mock_select.return_value = mock_backup_info
        mock_manager.restore_backup.return_value = {"claude-code": "Success"}
        mock_manager_class.return_value = mock_manager

        result = self.runner.invoke(app, ["backup", "restore", "--force"])
        assert result.exit_code == 0
        mock_manager.restore_backup.assert_called_once_with("backup_123", force=True)

    @patch('mcpcommander.cli.main.MCPManager')
    def test_backup_restore_by_id(self, mock_manager_class):
        """Test backup restore command with specific backup ID."""
        mock_manager = MagicMock()
        mock_backup_info = MagicMock()
        mock_backup_info.backup_id = "backup_123"
        mock_backup_info.formatted_timestamp = "2025-08-18 10:00:00"
        mock_backup_info.description = "Test backup"
        mock_backup_info.files_backed_up = ["claude-code"]
        mock_manager.get_backup_info.return_value = mock_backup_info
        mock_manager.restore_backup.return_value = {"claude-code": "Success"}
        mock_manager_class.return_value = mock_manager

        result = self.runner.invoke(app, ["backup", "restore", "backup_123", "--force"])
        assert result.exit_code == 0
        mock_manager.restore_backup.assert_called_once_with("backup_123", force=True)

    @patch('mcpcommander.cli.main.MCPManager')
    @patch('mcpcommander.cli.main.select_backup')
    @patch('mcpcommander.cli.main.confirm_action')
    def test_backup_delete_interactive(self, mock_confirm, mock_select, mock_manager_class):
        """Test backup delete command with interactive selection."""
        mock_manager = MagicMock()
        mock_backup_info = MagicMock()
        mock_backup_info.backup_id = "backup_123"
        mock_manager.list_backups.return_value = [mock_backup_info]
        mock_select.return_value = mock_backup_info
        mock_confirm.return_value = True
        mock_manager_class.return_value = mock_manager

        result = self.runner.invoke(app, ["backup", "delete"])
        assert result.exit_code == 0
        mock_manager.delete_backup.assert_called_once_with("backup_123")

    @patch('mcpcommander.cli.main.MCPManager')
    def test_backup_config_show(self, mock_manager_class):
        """Test backup config command."""
        mock_manager = MagicMock()
        mock_manager.get_backup_stats.return_value = {
            "total_backups": 5,
            "max_backups": 10,
            "total_size_bytes": 16252928,
            "total_size_mb": 15.5,
            "backup_directory": "/path/to/backups",
            "editor_counts": {"claude-code": 3, "cursor": 2},
            "oldest_backup": None,
            "newest_backup": None
        }
        mock_manager_class.return_value = mock_manager

        result = self.runner.invoke(app, ["backup", "config"])
        assert result.exit_code == 0
        mock_manager.get_backup_stats.assert_called_once()

    def test_backup_help_command(self):
        """Test backup help command."""
        result = self.runner.invoke(app, ["backup", "help"])
        assert result.exit_code == 0
        assert "backup" in result.stdout.lower()


class TestErrorHandling:
    """Test CLI error handling."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch('mcpcommander.cli.main.MCPManager')
    def test_mcp_commander_error_handling(self, mock_manager_class):
        """Test handling of MCPCommanderError."""
        mock_manager = MagicMock()
        mock_manager.list_servers.side_effect = MCPCommanderError("Test error")
        mock_manager_class.return_value = mock_manager

        result = self.runner.invoke(app, ["config", "servers"])
        assert result.exit_code == 1
        assert "Test error" in result.stdout

    @patch('mcpcommander.cli.main.MCPManager')
    def test_generic_error_handling(self, mock_manager_class):
        """Test handling of generic exceptions."""
        mock_manager = MagicMock()
        mock_manager.list_servers.side_effect = Exception("Unexpected error")
        mock_manager_class.return_value = mock_manager

        result = self.runner.invoke(app, ["config", "servers"])
        assert result.exit_code == 1
        assert "Unexpected error" in result.stdout


class TestEnvironmentOptions:
    """Test environment variable handling."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch.dict('os.environ', {'MCP_COMMANDER_VERBOSE': '1'})
    @patch('mcpcommander.cli.main.configure_debug_logging')
    @patch('mcpcommander.cli.main.MCPManager')
    @patch('mcpcommander.cli.main.VERBOSE_MODE', True)
    def test_debug_environment_variable(self, mock_manager_class, mock_debug):
        """Test debug mode activation via environment variable."""
        mock_manager = MagicMock()
        mock_manager.add_server.return_value = {"successful": ["claude-code"], "failed": []}
        mock_manager_class.return_value = mock_manager

        result = self.runner.invoke(app, ["add", "server", "test-server", "npx test-server"])
        assert result.exit_code == 0
        mock_debug.assert_called_once()

    @patch.dict('os.environ', {'MCP_VERBOSE': '1'})
    @patch('mcpcommander.cli.main.MCPManager')
    def test_verbose_environment_variable(self, mock_manager_class):
        """Test verbose mode activation via environment variable."""
        mock_manager = MagicMock()
        mock_manager.get_available_editors.return_value = []
        mock_manager_class.return_value = mock_manager

        result = self.runner.invoke(app, ["editors"])
        assert result.exit_code == 0
        # Verbose mode should be activated (hard to test output directly)