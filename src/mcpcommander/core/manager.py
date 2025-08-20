"""Core MCP server management functionality."""

from pathlib import Path
from typing import Any

from colorama import Fore, Style, init

from mcpcommander.core.backup import BackupManager
from mcpcommander.core.config import ConfigManager
from mcpcommander.core.editor_handlers import EditorHandlerFactory
from mcpcommander.schemas.config_schema import BackupInfo, EditorConfig
from mcpcommander.utils.config_parser import ServerConfigParser
from mcpcommander.utils.discovery import MCPDiscovery
from mcpcommander.utils.errors import BackupError, ConfigurationError, EditorError
from mcpcommander.utils.logger import get_logger

# Initialize colorama
init()

logger = get_logger(__name__)


class MCPManager:
    """Main class for managing MCP servers across different editors."""

    def __init__(self, config_path: Path | None = None) -> None:
        """Initialize MCP Manager with configuration."""
        self.config_manager = ConfigManager(config_path)
        self.editor_factory = EditorHandlerFactory()
        self.discovery = MCPDiscovery()
        self.backup_manager = BackupManager(self.config_manager.config_path)
        logger.info("MCPManager initialized")

    def add_server(
        self,
        server_name: str,
        server_config: str | dict[str, Any],
        editor_name: str | None = None,
        env_vars: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Add a server to specified editors or all editors."""
        try:
            # Parse and validate server configuration
            validated_config = ServerConfigParser.parse_server_config(server_config, env_vars)

            # Get target editors
            target_editors = self._get_target_editors(editor_name)

            results = {}
            successful = []
            failed = []

            # Add server to each target editor
            for editor in target_editors:
                try:
                    editor_config = self.config_manager.get_editor_config(editor)
                    handler = self.editor_factory.get_handler(editor, editor_config)
                    handler.add_server(server_name, validated_config)

                    successful.append(editor)
                    results[editor] = {"status": "success", "message": "Added successfully"}
                    logger.info(f"Added server '{server_name}' to {editor}")

                except Exception as e:
                    failed.append(editor)
                    results[editor] = {"status": "error", "message": str(e)}
                    logger.error(f"Failed to add server '{server_name}' to {editor}: {e}")

            # Print summary
            self._print_operation_summary("ADD", server_name, successful, failed)

            return {
                "server_name": server_name,
                "successful": successful,
                "failed": failed,
                "results": results,
            }

        except Exception as e:
            logger.error(f"Failed to add server '{server_name}': {e}")
            raise ConfigurationError(f"Failed to add server '{server_name}': {e}") from e

    def add_server_to_all_discovered(
        self,
        server_name: str,
        server_config: str | dict[str, Any],
        env_vars: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Add a server to ALL discovered MCP configurations on the system."""
        logger.info(f"Adding server '{server_name}' to all discovered MCP configurations")

        try:
            # Discover all MCP configurations
            discovered = self.discovery.discover_all_mcp_configs()

            if not discovered:
                print(
                    f"{Fore.YELLOW}⚠️  No MCP configurations found on this system{Style.RESET_ALL}"
                )
                return {
                    "server_name": server_name,
                    "successful": [],
                    "failed": [],
                    "results": {},
                    "discovered_count": 0,
                }

            print(
                f"{Fore.CYAN}🔍 Discovered {len(discovered)} MCP configuration(s){Style.RESET_ALL}"
            )

            # Parse and validate server configuration
            validated_config = ServerConfigParser.parse_server_config(server_config, env_vars)

            results = {}
            successful = []
            failed = []

            # Add server to each discovered configuration
            for editor_name, editor_config in discovered.items():
                try:
                    handler = self.editor_factory.get_handler(editor_name, editor_config)
                    handler.add_server(server_name, validated_config)

                    successful.append(editor_name)
                    results[editor_name] = {
                        "status": "success",
                        "message": "Added successfully",
                        "config_path": editor_config.config_path,
                    }
                    logger.info(f"Added server '{server_name}' to {editor_name}")

                except Exception as e:
                    failed.append(editor_name)
                    results[editor_name] = {
                        "status": "error",
                        "message": str(e),
                        "config_path": editor_config.config_path,
                    }
                    logger.error(f"Failed to add server '{server_name}' to {editor_name}: {e}")

            # Print detailed summary
            self._print_discovery_operation_summary("ADD", server_name, successful, failed, results)

            return {
                "server_name": server_name,
                "successful": successful,
                "failed": failed,
                "results": results,
                "discovered_count": len(discovered),
            }

        except Exception as e:
            logger.error(f"Failed to add server '{server_name}' to all configurations: {e}")
            raise ConfigurationError(f"Failed to add server to all configurations: {e}") from e

    def remove_server(self, server_name: str, editor_name: str | None = None) -> dict[str, Any]:
        """Remove a server from specified editors or all editors."""
        try:
            # Get target editors
            target_editors = self._get_target_editors(editor_name)

            results = {}
            successful = []
            failed = []

            # Remove server from each target editor
            for editor in target_editors:
                try:
                    editor_config = self.config_manager.get_editor_config(editor)
                    handler = self.editor_factory.get_handler(editor, editor_config)

                    # Check if server exists
                    if not handler.server_exists(server_name):
                        failed.append(editor)
                        results[editor] = {
                            "status": "error",
                            "message": f"Server '{server_name}' not found",
                        }
                        continue

                    handler.remove_server(server_name)
                    successful.append(editor)
                    results[editor] = {"status": "success", "message": "Removed successfully"}
                    logger.info(f"Removed server '{server_name}' from {editor}")

                except Exception as e:
                    failed.append(editor)
                    results[editor] = {"status": "error", "message": str(e)}
                    logger.error(f"Failed to remove server '{server_name}' from {editor}: {e}")

            # Print summary
            self._print_operation_summary("REMOVE", server_name, successful, failed)

            return {
                "server_name": server_name,
                "successful": successful,
                "failed": failed,
                "results": results,
            }

        except Exception as e:
            logger.error(f"Failed to remove server '{server_name}': {e}")
            raise ConfigurationError(f"Failed to remove server '{server_name}': {e}") from e

    def list_servers(self, editor_name: str | None = None) -> dict[str, dict[str, Any]]:
        """List servers configured in specified editors or all editors."""
        try:
            target_editors = self._get_target_editors(editor_name)

            all_servers = {}

            for editor in target_editors:
                try:
                    editor_config = self.config_manager.get_editor_config(editor)
                    handler = self.editor_factory.get_handler(editor, editor_config)
                    servers = handler.list_servers()
                    all_servers[editor] = servers

                except Exception as e:
                    logger.error(f"Failed to list servers for {editor}: {e}")
                    all_servers[editor] = {}

            return all_servers

        except Exception as e:
            logger.error(f"Failed to list servers: {e}")
            raise ConfigurationError(f"Failed to list servers: {e}") from e

    def status(self) -> dict[str, Any]:
        """Get status of all editor configurations."""
        try:
            editors_status = {}
            available_editors = self.config_manager.get_available_editors()

            for editor_name in available_editors:
                try:
                    editor_config = self.config_manager.get_editor_config(editor_name)
                    handler = self.editor_factory.get_handler(editor_name, editor_config)
                    editors_status[editor_name] = handler.get_status()

                except Exception as e:
                    logger.error(f"Failed to get status for {editor_name}: {e}")
                    editors_status[editor_name] = {
                        "error": str(e),
                        "config_path": (
                            editor_config.config_path if "editor_config" in locals() else "unknown"
                        ),
                    }

            return {"config_path": str(self.config_manager.config_path), "editors": editors_status}

        except Exception as e:
            logger.error(f"Failed to get status: {e}")
            raise ConfigurationError(f"Failed to get status: {e}") from e

    def discover_mcp_configs(self) -> dict[str, EditorConfig]:
        """Discover all MCP configurations on the system."""
        return self.discovery.discover_all_mcp_configs()

    def print_discovery_report(self) -> None:
        """Print discovery report of all MCP configurations."""
        discovered = self.discover_mcp_configs()
        self.discovery.print_discovery_report(discovered)

    def populate_config_with_discovered(self) -> dict[str, str]:
        """Populate configuration with discovered MCP editors."""
        discovered = self.discover_mcp_configs()

        # If no discoveries, return empty result
        if not discovered:
            return {}

        # Add discovered editors to config
        added_editors = {}
        for editor_name, editor_config in discovered.items():
            try:
                self.config_manager.add_editor(editor_name, editor_config)
                added_editors[editor_name] = str(editor_config.config_path)
                logger.info(f"Added discovered editor '{editor_name}' to configuration")
            except Exception as e:
                logger.error(f"Failed to add discovered editor '{editor_name}': {e}")

        return added_editors

    def get_available_editors(self) -> list[str]:
        """Get list of available editor names."""
        return self.config_manager.get_available_editors()

    def _get_target_editors(self, editor_name: str | None) -> list[str]:
        """Get list of target editors for operation."""
        if editor_name:
            available_editors = self.config_manager.get_available_editors()
            if editor_name not in available_editors:
                raise EditorError(
                    f"Unknown editor: {editor_name}",
                    f"Available editors: {', '.join(available_editors)}",
                )
            return [editor_name]
        return self.config_manager.get_available_editors()

    def _print_operation_summary(
        self, operation: str, server_name: str, successful: list[str], failed: list[str]
    ) -> None:
        """Print colorized operation summary."""
        total = len(successful) + len(failed)

        if successful and not failed:
            print(
                f"{Fore.GREEN}✅ {operation} '{server_name}': Success on all {total} editor(s){Style.RESET_ALL}"
            )
        elif not successful and failed:
            print(
                f"{Fore.RED}❌ {operation} '{server_name}': Failed on all {total} editor(s){Style.RESET_ALL}"
            )
        else:
            print(
                f"{Fore.YELLOW}⚠️  {operation} '{server_name}': Partial success ({len(successful)}/{total}){Style.RESET_ALL}"
            )

        if successful:
            print(f"{Fore.GREEN}   ✅ Successful: {', '.join(successful)}{Style.RESET_ALL}")
        if failed:
            print(f"{Fore.RED}   ❌ Failed: {', '.join(failed)}{Style.RESET_ALL}")

    def _print_discovery_operation_summary(
        self,
        operation: str,
        server_name: str,
        successful: list[str],
        failed: list[str],
        results: dict[str, Any],
    ) -> None:
        """Print detailed discovery operation summary."""
        total = len(successful) + len(failed)

        print(f"\n{Fore.CYAN}📊 {operation} Operation Summary{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{'=' * 40}{Style.RESET_ALL}")

        if successful and not failed:
            print(
                f"{Fore.GREEN}✅ SUCCESS: Added '{server_name}' to all {total} discovered configuration(s){Style.RESET_ALL}"
            )
        elif not successful and failed:
            print(
                f"{Fore.RED}❌ FAILED: Could not add '{server_name}' to any configuration{Style.RESET_ALL}"
            )
        else:
            print(
                f"{Fore.YELLOW}⚠️  PARTIAL: Added '{server_name}' to {len(successful)}/{total} configuration(s){Style.RESET_ALL}"
            )

        # Print detailed results
        for editor_name in successful + failed:
            result = results[editor_name]
            status_color = Fore.GREEN if result["status"] == "success" else Fore.RED
            status_icon = "✅" if result["status"] == "success" else "❌"

            print(
                f"{status_color}   {status_icon} {editor_name.upper():<15} {result['config_path']}{Style.RESET_ALL}"
            )
            if result["status"] == "error":
                print(f"{Fore.RED}      Error: {result['message']}{Style.RESET_ALL}")

        if successful:
            print(
                f"\n{Fore.GREEN}🎉 Server '{server_name}' is now available in {len(successful)} MCP configuration(s){Style.RESET_ALL}"
            )

    # Backup and Restore Methods

    def create_backup(
        self, editor_name: str | None = None, description: str | None = None
    ) -> BackupInfo:
        """Create a backup of MCP configurations.

        Args:
            editor_name: Specific editor to backup, None for all editors
            description: Optional description for the backup

        Returns:
            BackupInfo: Information about the created backup

        Raises:
            BackupError: If backup creation fails
        """
        try:
            # Get editor configurations
            editor_configs = {}
            if editor_name:
                # Single editor backup
                if editor_name not in self.get_available_editors():
                    raise BackupError(f"Unknown editor: {editor_name}")
                editor_configs[editor_name] = self.config_manager.get_editor_config(editor_name)
            else:
                # All editors backup
                for name in self.get_available_editors():
                    editor_configs[name] = self.config_manager.get_editor_config(name)

            # Create the backup
            backup_info = self.backup_manager.create_backup(
                editor_configs=editor_configs, editor_name=editor_name, description=description
            )

            # Print success message
            if editor_name:
                print(
                    f"{Fore.GREEN}✅ Created backup for {editor_name}: {backup_info.backup_id}{Style.RESET_ALL}"
                )
            else:
                editors_count = len(backup_info.files_backed_up)
                print(
                    f"{Fore.GREEN}✅ Created backup for {editors_count} editor(s): {backup_info.backup_id}{Style.RESET_ALL}"
                )

            return backup_info

        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            raise BackupError(f"Failed to create backup: {e}") from e

    def list_backups(self, editor_name: str | None = None) -> list[BackupInfo]:
        """List available backups.

        Args:
            editor_name: Filter by specific editor name

        Returns:
            List of backup information
        """
        try:
            return self.backup_manager.list_backups(editor_name)
        except Exception as e:
            logger.error(f"Failed to list backups: {e}")
            raise BackupError(f"Failed to list backups: {e}") from e

    def restore_backup(self, backup_id: str, force: bool = False) -> dict[str, str]:
        """Restore a backup.

        Args:
            backup_id: ID of the backup to restore
            force: Skip confirmation prompts

        Returns:
            Dict mapping editor names to restore status messages

        Raises:
            BackupError: If restore operation fails
        """
        try:
            # Get current editor configurations for validation
            editor_configs = {}
            for name in self.get_available_editors():
                editor_configs[name] = self.config_manager.get_editor_config(name)

            # Restore the backup
            results = self.backup_manager.restore_backup(
                backup_id=backup_id, editor_configs=editor_configs, force=force
            )

            # Print results
            successful = []
            failed = []

            for editor_name, message in results.items():
                print(f"  {message}")
                if message.startswith("✅"):
                    successful.append(editor_name)
                else:
                    failed.append(editor_name)

            # Print summary
            if successful and not failed:
                print(f"\n{Fore.GREEN}✅ Successfully restored backup {backup_id}{Style.RESET_ALL}")
            elif successful and failed:
                print(
                    f"\n{Fore.YELLOW}⚠️  Partially restored backup {backup_id} ({len(successful)}/{len(results)} editors){Style.RESET_ALL}"
                )
            else:
                print(f"\n{Fore.RED}❌ Failed to restore backup {backup_id}{Style.RESET_ALL}")

            return results

        except Exception as e:
            logger.error(f"Failed to restore backup {backup_id}: {e}")
            raise BackupError(f"Failed to restore backup {backup_id}: {e}") from e

    def delete_backup(self, backup_id: str) -> None:
        """Delete a backup.

        Args:
            backup_id: ID of the backup to delete

        Raises:
            BackupError: If deletion fails
        """
        try:
            self.backup_manager.delete_backup(backup_id)
            print(f"{Fore.GREEN}✅ Deleted backup: {backup_id}{Style.RESET_ALL}")
        except Exception as e:
            logger.error(f"Failed to delete backup {backup_id}: {e}")
            raise BackupError(f"Failed to delete backup {backup_id}: {e}") from e

    def get_backup_info(self, backup_id: str) -> BackupInfo | None:
        """Get detailed information about a backup.

        Args:
            backup_id: ID of the backup

        Returns:
            BackupInfo if found, None otherwise
        """
        try:
            return self.backup_manager.get_backup_info(backup_id)
        except Exception as e:
            logger.error(f"Failed to get backup info for {backup_id}: {e}")
            return None

    def set_max_backups(self, max_backups: int) -> None:
        """Set the maximum number of backups to keep.

        Args:
            max_backups: Maximum number of backups (must be >= 1)

        Raises:
            ConfigurationError: If max_backups is invalid
        """
        try:
            self.backup_manager.set_max_backups(max_backups)
            print(f"{Fore.GREEN}✅ Set maximum backups to {max_backups}{Style.RESET_ALL}")
        except Exception as e:
            logger.error(f"Failed to set max backups: {e}")
            raise ConfigurationError(f"Failed to set max backups: {e}") from e

    def get_backup_stats(self) -> dict[str, Any]:
        """Get backup statistics.

        Returns:
            Dictionary with backup statistics
        """
        try:
            return self.backup_manager.get_backup_stats()
        except Exception as e:
            logger.error(f"Failed to get backup stats: {e}")
            return {
                "total_backups": 0,
                "max_backups": 10,
                "total_size_bytes": 0,
                "total_size_mb": 0.0,
                "backup_directory": str(self.backup_manager.backup_dir),
                "editor_counts": {},
                "oldest_backup": None,
                "newest_backup": None,
                "error": str(e),
            }

    def get_config_path(self) -> Path:
        """Get the absolute path to the configuration file.

        Returns:
            Path: Absolute path to the configuration file
        """
        return self.config_manager.config_path.resolve()

    def reset_configuration(self, include_backups: bool = False) -> None:
        """Reset MCP Commander configuration to empty state.

        Args:
            include_backups: Whether to also remove all backup files

        Raises:
            ConfigurationError: If reset fails
        """
        try:
            # Create empty configuration
            empty_config = {"editors": {}}

            # Write empty config to file
            config_path = self.config_manager.config_path
            config_path.parent.mkdir(parents=True, exist_ok=True)

            with open(config_path, "w") as f:
                import json

                json.dump(empty_config, f, indent=2)

            # Reload configuration
            self.config_manager._config = None

            # Remove backup files if requested
            if include_backups:
                self.backup_manager.clear_all_backups()

            logger.info("Configuration reset to empty state")

        except Exception as e:
            logger.error(f"Failed to reset configuration: {e}")
            raise ConfigurationError(f"Failed to reset configuration: {e}") from e

    def get_status(self) -> dict[str, Any]:
        """Get comprehensive status information.

        Returns:
            Dictionary containing configuration status and editor information
        """
        try:
            status_info = self.status()  # Use existing status method
            return status_info
        except Exception as e:
            logger.error(f"Failed to get status: {e}")
            raise ConfigurationError(f"Failed to get status: {e}") from e
