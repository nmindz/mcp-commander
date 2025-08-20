"""MCP configuration discovery utilities."""

import os
import platform
from pathlib import Path

from colorama import Fore, Style, init

from mcpcommander.schemas.config_schema import EditorConfig
from mcpcommander.utils.logger import get_logger

# Initialize colorama
init()

logger = get_logger(__name__)


class MCPDiscovery:
    """Discovers MCP configurations across the system."""

    def __init__(self) -> None:
        self.system = platform.system().lower()
        self.home = Path.home()

    def discover_all_mcp_configs(self) -> dict[str, EditorConfig]:
        """Discover all available MCP configurations on the system."""
        logger.info("Starting MCP configuration discovery")
        discovered = {}

        # Known MCP-compatible applications
        discovery_methods = [
            ("claude-code", self._discover_claude_code),
            ("claude-desktop", self._discover_claude_desktop),
            ("cursor", self._discover_cursor),
            ("vscode", self._discover_vscode),
            ("windsurf", self._discover_windsurf),
            ("claude-cli", self._discover_claude_cli),
        ]

        for name, method in discovery_methods:
            try:
                config = method()
                if config:
                    discovered[name] = config
                    logger.info(f"Discovered {name} configuration at {config.config_path}")
            except Exception as e:
                logger.debug(f"Failed to discover {name}: {e}")

        logger.info(f"Discovery completed. Found {len(discovered)} MCP configurations")
        return discovered

    def _discover_claude_code(self) -> EditorConfig | None:
        """Discover Claude Code CLI configuration."""
        if self.system == "windows":
            # Windows: Use USERPROFILE environment variable
            user_profile = os.environ.get("USERPROFILE")
            if user_profile:
                claude_config = Path(user_profile) / ".claude.json"
            else:
                claude_config = self.home / ".claude.json"
        else:
            # macOS/Linux: Use home directory
            claude_config = self.home / ".claude.json"

        if claude_config.exists():
            return EditorConfig(config_path=str(claude_config), jsonpath="mcpServers")
        return None

    def _discover_claude_desktop(self) -> EditorConfig | None:
        """Discover Claude Desktop configuration."""
        if self.system == "darwin":  # macOS
            config_path = (
                self.home
                / "Library"
                / "Application Support"
                / "Claude"
                / "claude_desktop_config.json"
            )
        elif self.system == "windows":
            appdata = os.environ.get("APPDATA")
            if appdata:
                config_path = Path(appdata) / "Claude" / "claude_desktop_config.json"
            else:
                # Fallback using USERPROFILE
                user_profile = os.environ.get("USERPROFILE")
                if user_profile:
                    config_path = (
                        Path(user_profile)
                        / "AppData"
                        / "Roaming"
                        / "Claude"
                        / "claude_desktop_config.json"
                    )
                else:
                    config_path = (
                        self.home / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json"
                    )
        else:  # Linux
            config_path = self.home / ".config" / "Claude" / "claude_desktop_config.json"

        if config_path.exists():
            return EditorConfig(config_path=str(config_path), jsonpath="mcpServers")
        return None

    def _discover_cursor(self) -> EditorConfig | None:
        """Discover Cursor configuration."""
        # Primary location: ~/.cursor/mcp.json (most common)
        if self.system == "windows":
            user_profile = os.environ.get("USERPROFILE")
            if user_profile:
                primary_path = Path(user_profile) / ".cursor" / "mcp.json"
            else:
                primary_path = self.home / ".cursor" / "mcp.json"
        else:
            primary_path = self.home / ".cursor" / "mcp.json"

        # Alternative paths for different installation types
        alt_paths = []

        if self.system == "darwin":  # macOS
            alt_paths.extend(
                [
                    self.home
                    / "Library"
                    / "Application Support"
                    / "Cursor"
                    / "User"
                    / "globalStorage"
                    / "mcp.json",
                    self.home / ".cursor" / "config.json",
                ]
            )
        elif self.system == "windows":
            appdata = os.environ.get("APPDATA")
            if appdata:
                alt_paths.append(Path(appdata) / "Cursor" / "User" / "globalStorage" / "mcp.json")
            alt_paths.extend(
                [
                    primary_path.parent / "config.json",
                ]
            )
        else:  # Linux
            alt_paths.extend(
                [
                    self.home / ".config" / "Cursor" / "User" / "globalStorage" / "mcp.json",
                    self.home / ".cursor" / "config.json",
                ]
            )

        for path in [primary_path] + alt_paths:
            if path.exists():
                return EditorConfig(config_path=str(path), jsonpath="mcpServers")
        return None

    def _discover_vscode(self) -> EditorConfig | None:
        """Discover VS Code configuration."""
        paths_to_try = []

        if self.system == "darwin":  # macOS
            paths_to_try = [
                (
                    self.home / "Library" / "Application Support" / "Code" / "User" / "mcp.json",
                    "servers",
                ),
                (
                    self.home
                    / "Library"
                    / "Application Support"
                    / "Code"
                    / "User"
                    / "settings.json",
                    "mcp.servers",
                ),
            ]
        elif self.system == "windows":
            appdata = os.environ.get("APPDATA")
            if appdata:
                base_path = Path(appdata) / "Code" / "User"
            else:
                user_profile = os.environ.get("USERPROFILE")
                if user_profile:
                    base_path = Path(user_profile) / "AppData" / "Roaming" / "Code" / "User"
                else:
                    base_path = self.home / "AppData" / "Roaming" / "Code" / "User"

            paths_to_try = [
                (base_path / "mcp.json", "servers"),
                (base_path / "settings.json", "mcp.servers"),
            ]
        else:  # Linux
            paths_to_try = [
                (self.home / ".config" / "Code" / "User" / "mcp.json", "servers"),
                (self.home / ".config" / "Code" / "User" / "settings.json", "mcp.servers"),
            ]

        # Also check global user MCP config
        if self.system == "windows":
            user_profile = os.environ.get("USERPROFILE")
            if user_profile:
                paths_to_try.insert(0, (Path(user_profile) / ".mcp.json", "servers"))
        else:
            paths_to_try.insert(0, (self.home / ".mcp.json", "servers"))

        for config_path, jsonpath in paths_to_try:
            if config_path.exists():
                return EditorConfig(config_path=str(config_path), jsonpath=jsonpath)

        return None

    def _discover_windsurf(self) -> EditorConfig | None:
        """Discover Windsurf IDE configuration."""
        if self.system == "windows":
            user_profile = os.environ.get("USERPROFILE")
            if user_profile:
                windsurf_config = Path(user_profile) / ".codeium" / "windsurf" / "mcp_config.json"
            else:
                windsurf_config = self.home / ".codeium" / "windsurf" / "mcp_config.json"
        else:
            # macOS and Linux use the same path
            windsurf_config = self.home / ".codeium" / "windsurf" / "mcp_config.json"

        if windsurf_config.exists():
            return EditorConfig(config_path=str(windsurf_config), jsonpath="mcpServers")
        return None

    def _discover_claude_cli(self) -> EditorConfig | None:
        """Discover Claude CLI configuration."""
        if self.system == "windows":
            user_profile = os.environ.get("USERPROFILE")
            if user_profile:
                cli_config = Path(user_profile) / ".clauderc.json"
            else:
                cli_config = self.home / ".clauderc.json"
        else:
            cli_config = self.home / ".clauderc.json"

        if cli_config.exists():
            return EditorConfig(config_path=str(cli_config), jsonpath="mcpServers")
        return None

    def print_discovery_report(self, discovered: dict[str, EditorConfig]) -> None:
        """Print colorized discovery report."""
        print(f"\n{Fore.CYAN}🔍 MCP Configuration Discovery Report{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{'=' * 50}{Style.RESET_ALL}")

        if not discovered:
            print(f"{Fore.YELLOW}⚠️  No MCP configurations found on this system{Style.RESET_ALL}")
            print(
                f"{Fore.WHITE}   Consider installing Claude Desktop or Claude Code CLI{Style.RESET_ALL}"
            )
            return

        print(f"{Fore.GREEN}✅ Found {len(discovered)} MCP configuration(s):{Style.RESET_ALL}")

        for name, config in discovered.items():
            status = "✅" if config.expanded_path.exists() else "❌"
            color = Fore.GREEN if config.expanded_path.exists() else Fore.RED

            print(f"{color}   {status} {name.upper():<15} {config.config_path}{Style.RESET_ALL}")

        print(
            f"\n{Fore.CYAN}💡 Use 'mcp add server <server_name> <config> --all' to install to all discovered configurations{Style.RESET_ALL}"
        )


def discover_mcp_configs() -> dict[str, EditorConfig]:
    """Convenience function to discover all MCP configurations."""
    discovery = MCPDiscovery()
    return discovery.discover_all_mcp_configs()


def print_discovery_report(discovered: dict[str, EditorConfig]) -> None:
    """Convenience function to print discovery report."""
    discovery = MCPDiscovery()
    discovery.print_discovery_report(discovered)
