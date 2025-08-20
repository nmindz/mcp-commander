"""Unit tests for MCP discovery functionality."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from mcpcommander.schemas.config_schema import EditorConfig
from mcpcommander.utils.discovery import MCPDiscovery, discover_mcp_configs, print_discovery_report


class TestMCPDiscovery:
    """Test MCPDiscovery functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.discovery = MCPDiscovery()

    @patch('platform.system')
    def test_init_windows(self, mock_system):
        """Test initialization on Windows."""
        mock_system.return_value = "Windows"
        discovery = MCPDiscovery()
        
        assert discovery.system == "windows"
        assert discovery.home == Path.home()

    @patch('platform.system')
    def test_init_linux(self, mock_system):
        """Test initialization on Linux."""
        mock_system.return_value = "Linux"
        discovery = MCPDiscovery()
        
        assert discovery.system == "linux"

    @patch('platform.system')
    def test_init_macos(self, mock_system):
        """Test initialization on macOS."""
        mock_system.return_value = "Darwin"
        discovery = MCPDiscovery()
        
        assert discovery.system == "darwin"

    def test_discover_all_mcp_configs_empty(self):
        """Test discovery when no configurations are found."""
        with patch.object(self.discovery, '_discover_claude_desktop', return_value=None), \
             patch.object(self.discovery, '_discover_claude_code', return_value=None), \
             patch.object(self.discovery, '_discover_cursor', return_value=None), \
             patch.object(self.discovery, '_discover_vscode', return_value=None), \
             patch.object(self.discovery, '_discover_windsurf', return_value=None), \
             patch.object(self.discovery, '_discover_claude_cli', return_value=None):
            
            result = self.discovery.discover_all_mcp_configs()
            
            assert result == {}

    def test_discover_all_mcp_configs_multiple_editors(self):
        """Test discovery when multiple editors are found."""
        claude_config = EditorConfig(
            config_path="~/.config/claude-desktop/config.json",
            jsonpath="mcpServers"
        )
        cursor_config = EditorConfig(
            config_path="~/.cursor/config.json",
            jsonpath="mcpServers"
        )
        
        with patch.object(self.discovery, '_discover_claude_desktop', return_value=claude_config), \
             patch.object(self.discovery, '_discover_claude_code', return_value=None), \
             patch.object(self.discovery, '_discover_cursor', return_value=cursor_config), \
             patch.object(self.discovery, '_discover_vscode', return_value=None), \
             patch.object(self.discovery, '_discover_windsurf', return_value=None), \
             patch.object(self.discovery, '_discover_claude_cli', return_value=None):
            
            result = self.discovery.discover_all_mcp_configs()
            
            assert "claude-desktop" in result
            assert "cursor" in result
            assert len(result) == 2
            assert result["claude-desktop"] == claude_config
            assert result["cursor"] == cursor_config

    def test_discover_claude_desktop_windows(self):
        """Test Claude Desktop discovery on Windows."""
        with patch.object(self.discovery, 'system', 'windows'):
            with patch.dict(os.environ, {'APPDATA': 'C:/Users/Test/AppData/Roaming'}):
                expected_path = Path("C:/Users/Test/AppData/Roaming/Claude/claude_desktop_config.json")
                
                with patch('pathlib.Path.exists', return_value=True):
                    result = self.discovery._discover_claude_desktop()
                    
                    assert result is not None
                    assert result.config_path == str(expected_path)
                    assert result.jsonpath == "mcpServers"

    def test_discover_claude_desktop_macos(self):
        """Test Claude Desktop discovery on macOS."""
        with patch.object(self.discovery, 'system', 'darwin'):
            expected_path = self.discovery.home / "Library/Application Support/Claude/claude_desktop_config.json"
            
            with patch('pathlib.Path.exists', return_value=True):
                result = self.discovery._discover_claude_desktop()
                
                assert result is not None
                assert result.config_path == str(expected_path)

    def test_discover_claude_desktop_linux(self):
        """Test Claude Desktop discovery on Linux."""
        with patch.object(self.discovery, 'system', 'linux'):
            expected_path = self.discovery.home / ".config/Claude/claude_desktop_config.json"
            
            with patch('pathlib.Path.exists', return_value=True):
                result = self.discovery._discover_claude_desktop()
                
                assert result is not None

    def test_discover_claude_code_windows(self):
        """Test Claude Code discovery on Windows."""
        with patch.object(self.discovery, 'system', 'windows'):
            with patch.dict(os.environ, {'USERPROFILE': 'C:/Users/Test'}):
                expected_path = Path("C:/Users/Test/.claude.json")
                
                with patch('pathlib.Path.exists', return_value=True):
                    result = self.discovery._discover_claude_code()
                    
                    assert result is not None

    def test_discover_claude_code_macos(self):
        """Test Claude Code discovery on macOS."""
        with patch.object(self.discovery, 'system', 'darwin'):
            expected_path = self.discovery.home / ".claude.json"
            
            with patch('pathlib.Path.exists', return_value=True):
                result = self.discovery._discover_claude_code()
                
                assert result is not None

    def test_discover_claude_code_linux(self):
        """Test Claude Code discovery on Linux."""
        with patch.object(self.discovery, 'system', 'linux'):
            expected_path = self.discovery.home / ".claude.json"
            
            with patch('pathlib.Path.exists', return_value=True):
                result = self.discovery._discover_claude_code()
                
                assert result is not None

    def test_discover_cursor_windows(self):
        """Test Cursor discovery on Windows."""
        with patch.object(self.discovery, 'system', 'windows'):
            with patch.dict(os.environ, {'USERPROFILE': 'C:/Users/Test'}):
                expected_path = Path("C:/Users/Test/.cursor/mcp.json")
                
                with patch('pathlib.Path.exists', return_value=True):
                    result = self.discovery._discover_cursor()
                    
                    assert result is not None

    def test_discover_cursor_macos(self):
        """Test Cursor discovery on macOS."""
        with patch.object(self.discovery, 'system', 'darwin'):
            expected_path = self.discovery.home / ".cursor/mcp.json"
            
            with patch('pathlib.Path.exists', return_value=True):
                result = self.discovery._discover_cursor()
                
                assert result is not None

    def test_discover_cursor_linux(self):
        """Test Cursor discovery on Linux."""
        with patch.object(self.discovery, 'system', 'linux'):
            expected_path = self.discovery.home / ".cursor/mcp.json"
            
            with patch('pathlib.Path.exists', return_value=True):
                result = self.discovery._discover_cursor()
                
                assert result is not None

    def test_discover_vscode_windows(self):
        """Test VS Code discovery on Windows."""
        with patch.object(self.discovery, 'system', 'windows'):
            with patch.dict(os.environ, {'APPDATA': 'C:/Users/Test/AppData/Roaming'}):
                expected_path = Path("C:/Users/Test/AppData/Roaming/Code/User/mcp.json")
                
                with patch('pathlib.Path.exists', return_value=True):
                    result = self.discovery._discover_vscode()
                    
                    assert result is not None

    def test_discover_vscode_macos(self):
        """Test VS Code discovery on macOS."""
        with patch.object(self.discovery, 'system', 'darwin'):
            expected_path = self.discovery.home / "Library/Application Support/Code/User/mcp.json"
            
            with patch('pathlib.Path.exists', return_value=True):
                result = self.discovery._discover_vscode()
                
                assert result is not None

    def test_discover_windsurf_windows(self):
        """Test Windsurf discovery on Windows."""
        with patch.object(self.discovery, 'system', 'windows'):
            with patch.dict(os.environ, {'USERPROFILE': 'C:/Users/Test'}):
                expected_path = Path("C:/Users/Test/.codeium/windsurf/mcp_config.json")
                
                with patch('pathlib.Path.exists', return_value=True):
                    result = self.discovery._discover_windsurf()
                    
                    assert result is not None

    def test_discover_claude_cli_windows(self):
        """Test Claude CLI discovery on Windows."""
        with patch.object(self.discovery, 'system', 'windows'):
            with patch.dict(os.environ, {'USERPROFILE': 'C:/Users/Test'}):
                expected_path = Path("C:/Users/Test/.clauderc.json")
                
                with patch('pathlib.Path.exists', return_value=True):
                    result = self.discovery._discover_claude_cli()
                    
                    assert result is not None

    def test_discover_methods_return_none_when_file_missing(self):
        """Test that discovery methods return None when config file doesn't exist."""
        # Mock Path.exists to return False to simulate missing files
        with patch('pathlib.Path.exists', return_value=False):
            assert self.discovery._discover_claude_desktop() is None
            assert self.discovery._discover_claude_code() is None
            assert self.discovery._discover_cursor() is None
            assert self.discovery._discover_vscode() is None
            assert self.discovery._discover_windsurf() is None
            assert self.discovery._discover_claude_cli() is None

    @patch('mcpcommander.utils.discovery.print')
    def test_print_discovery_report_empty(self, mock_print):
        """Test printing discovery report with no configurations."""
        self.discovery.print_discovery_report({})
        
        # Check that print was called with empty report message
        mock_print.assert_called()
        calls = [str(call) for call in mock_print.call_args_list]
        assert any("No MCP configurations found" in call for call in calls)

    @patch('mcpcommander.utils.discovery.print')
    def test_print_discovery_report_with_configs(self, mock_print):
        """Test printing discovery report with configurations."""
        config = EditorConfig(
            config_path="~/.claude.json",
            jsonpath="mcpServers"
        )
        discovered = {"claude-code": config}
        
        self.discovery.print_discovery_report(discovered)
        
        mock_print.assert_called()
        calls = [str(call) for call in mock_print.call_args_list]
        assert any("Found 1 MCP configuration" in call for call in calls)

    def test_discover_all_editors_exception_handling(self):
        """Test that exceptions in individual discovery methods don't break the process."""
        with patch.object(self.discovery, '_discover_claude_desktop', side_effect=Exception("Test error")), \
             patch.object(self.discovery, '_discover_claude_code', return_value=None), \
             patch.object(self.discovery, '_discover_cursor', return_value=None), \
             patch.object(self.discovery, '_discover_vscode', return_value=None), \
             patch.object(self.discovery, '_discover_windsurf', return_value=None), \
             patch.object(self.discovery, '_discover_claude_cli', return_value=None):
            
            # Should not raise exception despite one method failing
            result = self.discovery.discover_all_mcp_configs()
            assert result == {}

    def test_discover_all_editors_comprehensive(self):
        """Test that all editor discovery methods are called."""
        with patch.object(self.discovery, '_discover_claude_desktop', return_value=None) as mock_claude_desktop, \
             patch.object(self.discovery, '_discover_claude_code', return_value=None) as mock_claude_code, \
             patch.object(self.discovery, '_discover_cursor', return_value=None) as mock_cursor, \
             patch.object(self.discovery, '_discover_vscode', return_value=None) as mock_vscode, \
             patch.object(self.discovery, '_discover_windsurf', return_value=None) as mock_windsurf, \
             patch.object(self.discovery, '_discover_claude_cli', return_value=None) as mock_claude_cli:
            
            self.discovery.discover_all_mcp_configs()
            
            # Verify all discovery methods were called
            mock_claude_desktop.assert_called_once()
            mock_claude_code.assert_called_once()
            mock_cursor.assert_called_once()
            mock_vscode.assert_called_once()
            mock_windsurf.assert_called_once()
            mock_claude_cli.assert_called_once()


class TestDiscoveryFunctions:
    """Test convenience functions."""

    @patch('mcpcommander.utils.discovery.MCPDiscovery')
    def test_discover_mcp_configs(self, mock_discovery_class):
        """Test discover_mcp_configs convenience function."""
        mock_discovery = MagicMock()
        mock_discovery.discover_all_mcp_configs.return_value = {"test": "config"}
        mock_discovery_class.return_value = mock_discovery
        
        result = discover_mcp_configs()
        
        mock_discovery_class.assert_called_once()
        mock_discovery.discover_all_mcp_configs.assert_called_once()
        assert result == {"test": "config"}

    @patch('mcpcommander.utils.discovery.MCPDiscovery')
    def test_print_discovery_report_function(self, mock_discovery_class):
        """Test print_discovery_report convenience function."""
        mock_discovery = MagicMock()
        mock_discovery_class.return_value = mock_discovery
        
        test_configs = {"test": "config"}
        print_discovery_report(test_configs)
        
        mock_discovery_class.assert_called_once()
        mock_discovery.print_discovery_report.assert_called_once_with(test_configs)


class TestCrossPlatformBehavior:
    """Test cross-platform specific behavior."""

    def setup_method(self):
        """Set up test fixtures."""
        self.discovery = MCPDiscovery()

    @patch('platform.system')
    def test_windows_environment_variable_handling(self, mock_system):
        """Test Windows environment variable handling."""
        mock_system.return_value = "Windows"
        discovery = MCPDiscovery()
        
        with patch.dict(os.environ, {'USERPROFILE': 'C:/Users/TestUser', 'APPDATA': 'C:/Users/TestUser/AppData/Roaming'}):
            # Test that Windows-specific paths are constructed correctly
            with patch('pathlib.Path.exists', return_value=True):
                claude_result = discovery._discover_claude_code()
                assert claude_result is not None
                
                desktop_result = discovery._discover_claude_desktop()
                assert desktop_result is not None

    @patch('platform.system')
    def test_windows_fallback_when_env_missing(self, mock_system):
        """Test Windows fallback when environment variables are missing."""
        mock_system.return_value = "Windows"
        discovery = MCPDiscovery()
        
        # Test without USERPROFILE/APPDATA
        with patch.dict(os.environ, {}, clear=True):
            with patch('pathlib.Path.exists', return_value=True):
                result = discovery._discover_claude_code()
                assert result is not None  # Should still work with home directory fallback

    def test_path_expansion(self):
        """Test that paths are properly expanded."""
        # Test that all discovery methods return paths as strings, not Path objects
        with patch('pathlib.Path.exists', return_value=True):
            if hasattr(self.discovery, '_discover_claude_code'):
                result = self.discovery._discover_claude_code()
                if result:
                    assert isinstance(result.config_path, str)