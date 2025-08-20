"""Modern CLI interface using typer with organized subcommands."""

from __future__ import annotations

import builtins
import os
import sys
from pathlib import Path

import typer
from colorama import Fore, Style, init
from rich import box
from rich.console import Console
from rich.table import Table

from mcpcommander import __version__
from mcpcommander.core.manager import MCPManager
from mcpcommander.utils.cli_examples import print_command_examples
from mcpcommander.utils.errors import MCPCommanderError
from mcpcommander.utils.interactive import confirm_action, get_backup_description, select_backup
from mcpcommander.utils.logger import configure_debug_logging, get_logger

# Initialize colorama and rich with proper Windows support
init(autoreset=True, convert=True, strip=False)

# Set console encoding for Windows
if os.name == "nt":  # Windows
    try:
        # Try to set UTF-8 encoding for better Unicode support
        import io

        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        # Fall back to default encoding if UTF-8 fails
        pass


# Cross-platform Unicode support
def get_unicode_chars() -> dict[str, str]:
    """Get appropriate Unicode characters based on platform and encoding support."""
    # Try to detect if Unicode is supported
    try:
        # Test if we can encode Unicode characters
        test_chars = {"checkmark": "✅", "cross": "❌", "line": "═"}
        for char in test_chars.values():
            char.encode(sys.stdout.encoding or "utf-8")
        return {"checkmark": "✅", "cross": "❌", "line": "═", "stop": "⏹️"}
    except (UnicodeEncodeError, LookupError, AttributeError):
        # Fall back to ASCII alternatives
        return {"checkmark": "[OK]", "cross": "[ERROR]", "line": "-", "stop": "[STOP]"}


UNICODE_CHARS = get_unicode_chars()

# Main app
app = typer.Typer(help="MCP Commander - Cross-platform MCP server management", add_completion=False)

# Subcommand groups
add_app = typer.Typer(help="Add MCP servers and editors")
remove_app = typer.Typer(help="Remove MCP servers and editors")
backup_app = typer.Typer(help="Backup management for MCP configurations")
config_app = typer.Typer(help="Manage MCP Commander configuration")

app.add_typer(add_app, name="add")
app.add_typer(remove_app, name="remove")
app.add_typer(backup_app, name="backup")
app.add_typer(config_app, name="config")


# Check for environment variable verbose setting
def is_verbose_from_env() -> bool:
    """Check if verbose mode is enabled via environment variable."""
    env_verbose = os.environ.get("MCP_COMMANDER_VERBOSE", "").lower()
    return env_verbose in ("1", "true", "yes")


# Global verbose setting
VERBOSE_MODE = is_verbose_from_env()
# Create console with cross-platform encoding support
console = Console(legacy_windows=True, force_terminal=True)
logger = get_logger(__name__)


def _process_environment_options(
    from_env: str | None, env_list: builtins.list[str]
) -> builtins.dict[str, str]:
    """Process --from-env and --env options into environment variable dictionary.

    Args:
        from_env: Comma-separated list of environment variable names to copy from current environment
        env_list: List of KEY:value pairs for explicit environment variables

    Returns:
        Dictionary of environment variables

    Raises:
        typer.BadParameter: If environment variable parsing fails
    """
    env_vars: dict[str, str] = {}

    # Process --from-env option
    if from_env:
        for env_name in from_env.split(","):
            env_name = env_name.strip()
            if env_name:
                env_value = os.environ.get(env_name)
                if env_value is not None:
                    env_vars[env_name] = env_value
                else:
                    print(
                        f"{Fore.YELLOW}⚠️  Environment variable '{env_name}' not found in current environment{Style.RESET_ALL}"
                    )

    # Process --env options
    for env_pair in env_list:
        if ":" not in env_pair:
            raise typer.BadParameter(
                f"Invalid --env format '{env_pair}'. Expected KEY:value format."
            )

        key, value = env_pair.split(":", 1)
        key = key.strip()
        value = value.strip()

        if not key:
            raise typer.BadParameter(f"Empty key in --env option '{env_pair}'")

        env_vars[key] = value

    return env_vars


def help_callback(ctx: typer.Context, param: typer.CallbackParam, value: bool) -> None:
    """Custom help callback that always shows complete help with examples."""
    if not value:
        return

    # Get command name from context
    command_name = ctx.info_name

    # Show default help
    print(ctx.get_help())

    # Always show examples for help (no longer dependent on verbose flag)
    if command_name:
        print_command_examples(command_name)

    raise typer.Exit()


# =============================================================================
# ADD COMMANDS
# =============================================================================


@add_app.command("server")
def add_server(
    server_name: str = typer.Argument(..., help="Name of the server"),
    server_config: str = typer.Argument(..., help="Server configuration (JSON or command path)"),
    editor: str | None = typer.Argument(None, help="Specific editor to add server to"),
    config: Path | None = typer.Option(None, "--config", "-c", help="Configuration file path"),
    all_editors: bool = typer.Option(
        False, "--all", help="Add to ALL discovered MCP configurations on the system"
    ),
    from_env: str | None = typer.Option(
        None,
        "--from-env",
        help="Comma-separated environment variable names to copy from current environment",
    ),
    env: builtins.list[str] = typer.Option(
        [], "--env", help="Environment variable in KEY:value format (can be used multiple times)"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable debug logging"),
    help: bool = typer.Option(
        False,
        "--help",
        callback=help_callback,
        expose_value=False,
        is_eager=True,
        help="Show this message and exit.",
    ),
) -> None:
    """Add MCP server to editors."""
    if verbose or VERBOSE_MODE:
        configure_debug_logging()

    try:
        # Process environment variable options
        env_vars = _process_environment_options(from_env, env)

        manager = MCPManager(config)

        if all_editors:
            result = manager.add_server_to_all_discovered(server_name, server_config, env_vars)

            if result["discovered_count"] == 0:
                print(
                    f"\n{Fore.YELLOW}💡 Tip: Install Claude Desktop or Claude Code CLI to get started with MCP{Style.RESET_ALL}"
                )
                raise typer.Exit(0)

            if not result["failed"]:
                print(
                    f"\n{Fore.GREEN}🎉 Successfully added '{server_name}' to all {result['discovered_count']} MCP configuration(s)!{Style.RESET_ALL}"
                )
            elif result["successful"]:
                print(
                    f"\n{Fore.YELLOW}⚠️  Added '{server_name}' to {len(result['successful'])}/{result['discovered_count']} configuration(s){Style.RESET_ALL}"
                )
                raise typer.Exit(1)
            else:
                raise typer.Exit(1)
        else:
            result = manager.add_server(server_name, server_config, editor, env_vars)

            if not result["failed"]:
                target = editor or "all configured editors"
                print(
                    f"{Fore.GREEN}✅ Successfully added server '{server_name}' to {target}{Style.RESET_ALL}"
                )
            else:
                raise typer.Exit(1)

    except MCPCommanderError as e:
        print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        if e.details:
            print(f"{Fore.YELLOW}   Details: {e.details}{Style.RESET_ALL}")
        raise typer.Exit(1) from None
    except Exception as e:
        print(f"{Fore.RED}❌ Unexpected error: {e}{Style.RESET_ALL}")
        if verbose or VERBOSE_MODE:
            logger.exception("Unexpected error in add server command")
        raise typer.Exit(1) from e


@add_app.command("editor")
def add_editor(
    name: str = typer.Argument(..., help="Name of the editor (e.g., 'vscode-custom')"),
    config_path: str = typer.Argument(..., help="Path to the editor's MCP configuration file"),
    jsonpath: str = typer.Option(
        "mcpServers", "--jsonpath", "-j", help="JSONPath to MCP servers section"
    ),
    config: Path | None = typer.Option(None, "--config", "-c", help="Configuration file path"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable debug logging"),
    help: bool = typer.Option(
        False,
        "--help",
        callback=help_callback,
        expose_value=False,
        is_eager=True,
        help="Show this message and exit.",
    ),
) -> None:
    """Add support for a new editor."""
    if verbose or VERBOSE_MODE:
        configure_debug_logging()

    try:
        from mcpcommander.schemas.config_schema import EditorConfig

        manager = MCPManager(config)

        # Create new editor configuration
        editor_config = EditorConfig(config_path=config_path, jsonpath=jsonpath)

        # Add to configuration
        manager.config_manager.add_editor(name, editor_config)

        print(f"{Fore.GREEN}✅ Successfully added editor '{name}'{Style.RESET_ALL}")
        print(f"{Fore.CYAN}   Config Path: {config_path}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}   JSON Path: {jsonpath}{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}💡 You can now use '{name}' with other commands:{Style.RESET_ALL}")
        print(f'{Fore.WHITE}   mcp add server server-name "command" {name}{Style.RESET_ALL}')
        print(f"{Fore.WHITE}   mcp config servers {name}{Style.RESET_ALL}")

    except MCPCommanderError as e:
        print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        if e.details:
            print(f"{Fore.YELLOW}   Details: {e.details}{Style.RESET_ALL}")
        raise typer.Exit(1) from None
    except Exception as e:
        print(f"{Fore.RED}❌ Unexpected error: {e}{Style.RESET_ALL}")
        if verbose or VERBOSE_MODE:
            logger.exception("Unexpected error in add editor command")
        raise typer.Exit(1) from e


@add_app.command("help")
def add_help() -> None:
    """Show help for add commands."""
    print(f"{Fore.CYAN}📖 Add Commands Help{Style.RESET_ALL}")
    print(f"{Fore.BLUE}{'=' * 30}{Style.RESET_ALL}")
    print()
    print(f"{Fore.GREEN}mcp add server{Style.RESET_ALL} - Add MCP server to editors")
    print(f'  {Fore.WHITE}mcp add server myserver "npx server" --all{Style.RESET_ALL}')
    print(f'  {Fore.WHITE}mcp add server myserver "npx server" claude-code{Style.RESET_ALL}')
    print()
    print(f"{Fore.GREEN}mcp add editor{Style.RESET_ALL} - Add support for a new editor")
    print(f'  {Fore.WHITE}mcp add editor custom-editor "/path/to/config.json"{Style.RESET_ALL}')
    print()
    print(f"{Fore.YELLOW}💡 Use --help with any subcommand for detailed options{Style.RESET_ALL}")


# =============================================================================
# REMOVE COMMANDS
# =============================================================================


@remove_app.command("server")
def remove_server(
    server_name: str = typer.Argument(..., help="Name of the server to remove"),
    editor: str | None = typer.Argument(None, help="Specific editor to remove server from"),
    config: Path | None = typer.Option(None, "--config", "-c", help="Configuration file path"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable debug logging"),
    help: bool = typer.Option(
        False,
        "--help",
        callback=help_callback,
        expose_value=False,
        is_eager=True,
        help="Show this message and exit.",
    ),
) -> None:
    """Remove MCP server from editors."""
    if verbose or VERBOSE_MODE:
        configure_debug_logging()

    try:
        manager = MCPManager(config)
        result = manager.remove_server(server_name, editor)

        if not result["failed"]:
            target = editor or "all configured editors"
            print(
                f"{Fore.GREEN}✅ Successfully removed server '{server_name}' from {target}{Style.RESET_ALL}"
            )
        else:
            raise typer.Exit(1)

    except MCPCommanderError as e:
        print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        if e.details:
            print(f"{Fore.YELLOW}   Details: {e.details}{Style.RESET_ALL}")
        raise typer.Exit(1) from None
    except Exception as e:
        print(f"{Fore.RED}❌ Unexpected error: {e}{Style.RESET_ALL}")
        if verbose or VERBOSE_MODE:
            logger.exception("Unexpected error in remove server command")
        raise typer.Exit(1) from e


@remove_app.command("editor")
def remove_editor(
    name: str = typer.Argument(..., help="Name of the editor to remove"),
    config: Path | None = typer.Option(None, "--config", "-c", help="Configuration file path"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable debug logging"),
    help: bool = typer.Option(
        False,
        "--help",
        callback=help_callback,
        expose_value=False,
        is_eager=True,
        help="Show this message and exit.",
    ),
) -> None:
    """Remove support for an editor."""
    if verbose or VERBOSE_MODE:
        configure_debug_logging()

    try:
        manager = MCPManager(config)

        # Check if editor exists
        available_editors = manager.get_available_editors()
        if name not in available_editors:
            print(f"{Fore.RED}❌ Editor '{name}' not found{Style.RESET_ALL}")
            print(
                f"{Fore.YELLOW}   Available editors: {', '.join(available_editors)}{Style.RESET_ALL}"
            )
            raise typer.Exit(1)

        # Remove editor
        manager.config_manager.remove_editor(name)

        print(f"{Fore.GREEN}✅ Successfully removed editor '{name}'{Style.RESET_ALL}")

    except MCPCommanderError as e:
        print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        if e.details:
            print(f"{Fore.YELLOW}   Details: {e.details}{Style.RESET_ALL}")
        raise typer.Exit(1) from None
    except Exception as e:
        print(f"{Fore.RED}❌ Unexpected error: {e}{Style.RESET_ALL}")
        if verbose or VERBOSE_MODE:
            logger.exception("Unexpected error in remove editor command")
        raise typer.Exit(1) from e


@remove_app.command("help")
def remove_help() -> None:
    """Show help for remove commands."""
    print(f"{Fore.CYAN}📖 Remove Commands Help{Style.RESET_ALL}")
    print(f"{Fore.BLUE}{'=' * 30}{Style.RESET_ALL}")
    print()
    print(f"{Fore.GREEN}mcp remove server{Style.RESET_ALL} - Remove MCP server from editors")
    print(f"  {Fore.WHITE}mcp remove server myserver{Style.RESET_ALL}")
    print(f"  {Fore.WHITE}mcp remove server myserver claude-code{Style.RESET_ALL}")
    print()
    print(f"{Fore.GREEN}mcp remove editor{Style.RESET_ALL} - Remove support for an editor")
    print(f"  {Fore.WHITE}mcp remove editor custom-editor{Style.RESET_ALL}")
    print()
    print(f"{Fore.YELLOW}💡 Use --help with any subcommand for detailed options{Style.RESET_ALL}")


# =============================================================================
# BACKUP COMMANDS
# =============================================================================


@backup_app.command("create")
def backup_create(
    editor: str | None = typer.Argument(
        None, help="Specific editor to backup (or all if not specified)"
    ),
    description: str | None = typer.Option(
        None, "--description", "-d", help="Description for the backup"
    ),
    interactive: bool = typer.Option(
        True, "--interactive/--no-interactive", help="Ask for description interactively"
    ),
    config: Path | None = typer.Option(None, "--config", "-c", help="Configuration file path"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable debug logging"),
    help: bool = typer.Option(
        False,
        "--help",
        callback=help_callback,
        expose_value=False,
        is_eager=True,
        help="Show this message and exit.",
    ),
) -> None:
    """Create a backup of MCP configurations."""
    if verbose or VERBOSE_MODE:
        configure_debug_logging()

    try:
        # Get description interactively if not provided and interactive mode is enabled
        if not description and interactive:
            desc_input = get_backup_description()
            if desc_input:
                description = desc_input

        manager = MCPManager(config)
        backup_info = manager.create_backup(editor_name=editor, description=description)

        # Show backup details
        print(f"\n{Fore.CYAN}📦 Backup Details:{Style.RESET_ALL}")
        print(f"  ID: {backup_info.backup_id}")
        print(f"  Timestamp: {backup_info.formatted_timestamp}")
        print(f"  Description: {backup_info.description}")
        print(f"  Files: {', '.join(backup_info.files_backed_up)}")

    except MCPCommanderError as e:
        print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        if e.details:
            print(f"{Fore.YELLOW}   Details: {e.details}{Style.RESET_ALL}")
        raise typer.Exit(1) from None
    except Exception as e:
        print(f"{Fore.RED}❌ Unexpected error: {e}{Style.RESET_ALL}")
        if verbose or VERBOSE_MODE:
            logger.exception("Unexpected error in backup create command")
        raise typer.Exit(1) from e


@backup_app.command("restore")
def backup_restore(
    backup_id: str | None = typer.Argument(
        None, help="Backup ID to restore (interactive selection if not provided)"
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompts"),
    config: Path | None = typer.Option(None, "--config", "-c", help="Configuration file path"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable debug logging"),
    help: bool = typer.Option(
        False,
        "--help",
        callback=help_callback,
        expose_value=False,
        is_eager=True,
        help="Show this message and exit.",
    ),
) -> None:
    """Restore a backup of MCP configurations."""
    if verbose or VERBOSE_MODE:
        configure_debug_logging()

    try:
        manager = MCPManager(config)

        # If no backup_id provided, show interactive selection
        if not backup_id:
            backups = manager.list_backups()
            if not backups:
                print(f"{Fore.YELLOW}No backups available to restore.{Style.RESET_ALL}")
                raise typer.Exit(0)

            selected_backup = select_backup(backups, "Select backup to restore")
            if not selected_backup:
                print(f"{Fore.YELLOW}Restore cancelled.{Style.RESET_ALL}")
                raise typer.Exit(0)

            backup_id = selected_backup.backup_id

        # Get backup info
        backup_info = manager.get_backup_info(backup_id)
        if not backup_info:
            print(f"{Fore.RED}❌ Backup not found: {backup_id}{Style.RESET_ALL}")
            raise typer.Exit(1)

        # Show backup details and confirm
        print(f"\n{Fore.CYAN}📦 Restoring Backup:{Style.RESET_ALL}")
        print(f"  ID: {backup_info.backup_id}")
        print(f"  Timestamp: {backup_info.formatted_timestamp}")
        print(f"  Description: {backup_info.description}")
        print(f"  Files: {', '.join(backup_info.files_backed_up)}")

        if not force:
            if not confirm_action(
                "Proceed with restore? This will overwrite existing configurations"
            ):
                print(f"{Fore.YELLOW}Restore cancelled.{Style.RESET_ALL}")
                raise typer.Exit(0)

        # Perform restore
        print(f"\n{Fore.CYAN}🔄 Restoring configurations...{Style.RESET_ALL}")
        manager.restore_backup(backup_id, force=force)

        print(f"\n{Fore.CYAN}📊 Restore completed.{Style.RESET_ALL}")

    except MCPCommanderError as e:
        print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        if e.details:
            print(f"{Fore.YELLOW}   Details: {e.details}{Style.RESET_ALL}")
        raise typer.Exit(1) from None
    except Exception as e:
        print(f"{Fore.RED}❌ Unexpected error: {e}{Style.RESET_ALL}")
        if verbose or VERBOSE_MODE:
            logger.exception("Unexpected error in backup restore command")
        raise typer.Exit(1) from e


@backup_app.command("list")
def backup_list(
    editor: str | None = typer.Argument(None, help="Filter by specific editor"),
    config: Path | None = typer.Option(None, "--config", "-c", help="Configuration file path"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable debug logging"),
    help: bool = typer.Option(
        False,
        "--help",
        callback=help_callback,
        expose_value=False,
        is_eager=True,
        help="Show this message and exit.",
    ),
) -> None:
    """List available backups."""
    if verbose or VERBOSE_MODE:
        configure_debug_logging()

    try:
        manager = MCPManager(config)
        backups = manager.list_backups(editor)

        if not backups:
            if editor:
                print(f"{Fore.YELLOW}No backups found for {editor}.{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}No backups found.{Style.RESET_ALL}")
            return

        # Create backup table
        table = Table(
            title=f"Available Backups{f' for {editor}' if editor else ''}", box=box.ROUNDED
        )
        table.add_column("Backup ID", style="cyan")
        table.add_column("Timestamp", style="blue")
        table.add_column("Type", style="magenta")
        table.add_column("Files", style="green")
        table.add_column("Description", style="yellow")

        for backup in backups:
            backup_type = backup.display_name
            files_info = ", ".join(backup.files_backed_up) if backup.files_backed_up else "None"

            table.add_row(
                backup.backup_id,
                backup.formatted_timestamp,
                backup_type,
                files_info,
                backup.description,
            )

        console.print(table)

        # Show stats
        stats = manager.get_backup_stats()
        print(f"\n{Fore.CYAN}📊 Backup Statistics:{Style.RESET_ALL}")
        print(f"  Total backups: {stats['total_backups']}")
        print(f"  Maximum backups: {stats['max_backups']}")
        print(f"  Storage used: {stats['total_size_mb']} MB")
        print(f"  Backup directory: {stats['backup_directory']}")

    except MCPCommanderError as e:
        print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        if e.details:
            print(f"{Fore.YELLOW}   Details: {e.details}{Style.RESET_ALL}")
        raise typer.Exit(1) from None
    except Exception as e:
        print(f"{Fore.RED}❌ Unexpected error: {e}{Style.RESET_ALL}")
        if verbose or VERBOSE_MODE:
            logger.exception("Unexpected error in backup list command")
        raise typer.Exit(1) from e


@backup_app.command("delete")
def backup_delete(
    backup_id: str | None = typer.Argument(
        None, help="Backup ID to delete (interactive selection if not provided)"
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt"),
    config: Path | None = typer.Option(None, "--config", "-c", help="Configuration file path"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable debug logging"),
    help: bool = typer.Option(
        False,
        "--help",
        callback=help_callback,
        expose_value=False,
        is_eager=True,
        help="Show this message and exit.",
    ),
) -> None:
    """Delete a backup."""
    if verbose or VERBOSE_MODE:
        configure_debug_logging()

    try:
        manager = MCPManager(config)

        # If no backup_id provided, show interactive selection
        if not backup_id:
            backups = manager.list_backups()
            if not backups:
                print(f"{Fore.YELLOW}No backups available to delete.{Style.RESET_ALL}")
                raise typer.Exit(0)

            selected_backup = select_backup(backups, "Select backup to delete")
            if not selected_backup:
                print(f"{Fore.YELLOW}Delete cancelled.{Style.RESET_ALL}")
                raise typer.Exit(0)

            backup_id = selected_backup.backup_id

        # Get backup info
        backup_info = manager.get_backup_info(backup_id)
        if not backup_info:
            print(f"{Fore.RED}❌ Backup not found: {backup_id}{Style.RESET_ALL}")
            raise typer.Exit(1)

        # Confirm deletion
        if not force:
            print(f"\n{Fore.CYAN}📦 Backup to Delete:{Style.RESET_ALL}")
            print(f"  ID: {backup_info.backup_id}")
            print(f"  Timestamp: {backup_info.formatted_timestamp}")
            print(f"  Description: {backup_info.description}")

            if not confirm_action(f"Delete backup {backup_id}? This cannot be undone"):
                print(f"{Fore.YELLOW}Delete cancelled.{Style.RESET_ALL}")
                raise typer.Exit(0)

        # Delete backup
        manager.delete_backup(backup_id)

    except MCPCommanderError as e:
        print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        if e.details:
            print(f"{Fore.YELLOW}   Details: {e.details}{Style.RESET_ALL}")
        raise typer.Exit(1) from None
    except Exception as e:
        print(f"{Fore.RED}❌ Unexpected error: {e}{Style.RESET_ALL}")
        if verbose or VERBOSE_MODE:
            logger.exception("Unexpected error in backup delete command")
        raise typer.Exit(1) from e


@backup_app.command("config")
def backup_config(
    max_backups: int | None = typer.Option(
        None, "--max-backups", help="Set maximum number of backups to keep"
    ),
    show: bool = typer.Option(False, "--show", help="Show current backup configuration"),
    config: Path | None = typer.Option(None, "--config", "-c", help="Configuration file path"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable debug logging"),
    help: bool = typer.Option(
        False,
        "--help",
        callback=help_callback,
        expose_value=False,
        is_eager=True,
        help="Show this message and exit.",
    ),
) -> None:
    """Configure backup settings."""
    if verbose or VERBOSE_MODE:
        configure_debug_logging()

    try:
        manager = MCPManager(config)

        if max_backups is not None:
            # Set maximum backups
            manager.set_max_backups(max_backups)

        if show or max_backups is None:
            # Show current configuration
            stats = manager.get_backup_stats()

            print(f"{Fore.CYAN}📊 Backup Configuration:{Style.RESET_ALL}")
            print(f"  Maximum backups: {stats['max_backups']}")
            print(f"  Current backups: {stats['total_backups']}")
            print(f"  Storage used: {stats['total_size_mb']} MB")
            print(f"  Backup directory: {stats['backup_directory']}")

            if stats["editor_counts"]:
                print(f"\n{Fore.CYAN}📝 Editor Backup Counts:{Style.RESET_ALL}")
                for editor, count in stats["editor_counts"].items():
                    print(f"  {editor}: {count} backup(s)")

    except MCPCommanderError as e:
        print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        if e.details:
            print(f"{Fore.YELLOW}   Details: {e.details}{Style.RESET_ALL}")
        raise typer.Exit(1) from None
    except Exception as e:
        print(f"{Fore.RED}❌ Unexpected error: {e}{Style.RESET_ALL}")
        if verbose or VERBOSE_MODE:
            logger.exception("Unexpected error in backup config command")
        raise typer.Exit(1) from e


@backup_app.command("help")
def backup_help() -> None:
    """Show help for backup commands."""
    print(f"{Fore.CYAN}📖 Backup Commands Help{Style.RESET_ALL}")
    print(f"{Fore.BLUE}{'=' * 30}{Style.RESET_ALL}")
    print()
    print(f"{Fore.GREEN}mcp backup create{Style.RESET_ALL} - Create a backup of MCP configurations")
    print(f"  {Fore.WHITE}mcp backup create{Style.RESET_ALL}")
    print(
        f'  {Fore.WHITE}mcp backup create claude-code --description "Before update"{Style.RESET_ALL}'
    )
    print()
    print(f"{Fore.GREEN}mcp backup restore{Style.RESET_ALL} - Restore a backup")
    print(f"  {Fore.WHITE}mcp backup restore{Style.RESET_ALL}")
    print(f"  {Fore.WHITE}mcp backup restore backup-id-123{Style.RESET_ALL}")
    print()
    print(f"{Fore.GREEN}mcp backup list{Style.RESET_ALL} - List available backups")
    print(f"  {Fore.WHITE}mcp backup list{Style.RESET_ALL}")
    print(f"  {Fore.WHITE}mcp backup list claude-code{Style.RESET_ALL}")
    print()
    print(f"{Fore.GREEN}mcp backup delete{Style.RESET_ALL} - Delete a backup")
    print(f"  {Fore.WHITE}mcp backup delete{Style.RESET_ALL}")
    print(f"  {Fore.WHITE}mcp backup delete backup-id-123{Style.RESET_ALL}")
    print()
    print(f"{Fore.GREEN}mcp backup config{Style.RESET_ALL} - Configure backup settings")
    print(f"  {Fore.WHITE}mcp backup config --show{Style.RESET_ALL}")
    print(f"  {Fore.WHITE}mcp backup config --max-backups 20{Style.RESET_ALL}")
    print()
    print(f"{Fore.YELLOW}💡 Use --help with any subcommand for detailed options{Style.RESET_ALL}")


# =============================================================================
# REMAINING MAIN LEVEL COMMANDS
# =============================================================================
# Note: list, status, and selfdestruct have been moved to 'mcp config' subcommands


@app.command()
def discover(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable debug logging"),
    help: bool = typer.Option(
        False,
        "--help",
        callback=help_callback,
        expose_value=False,
        is_eager=True,
        help="Show this message and exit.",
    ),
) -> None:
    """Discover all MCP configurations on the system."""
    if verbose or VERBOSE_MODE:
        configure_debug_logging()

    try:
        manager = MCPManager()
        manager.print_discovery_report()

        # Populate config with discovered editors
        added_editors = manager.populate_config_with_discovered()

        if added_editors:
            print(f"\n{Fore.CYAN}✅ Updated MCP Commander configuration:{Style.RESET_ALL}")
            for editor_name, config_path in added_editors.items():
                print(f"  + {editor_name.upper():<15} {config_path}")
            print(
                f"\n{Fore.GREEN}Run 'mcp config show' to see the updated configuration.{Style.RESET_ALL}"
            )
        else:
            print(
                f"\n{Fore.YELLOW}No editors were added to configuration (they may already exist).{Style.RESET_ALL}"
            )

    except MCPCommanderError as e:
        print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        if e.details:
            print(f"{Fore.YELLOW}   Details: {e.details}{Style.RESET_ALL}")
        raise typer.Exit(1) from None
    except Exception as e:
        print(f"{Fore.RED}❌ Unexpected error: {e}{Style.RESET_ALL}")
        if verbose or VERBOSE_MODE:
            logger.exception("Unexpected error in discover command")
        raise typer.Exit(1) from e


@app.command()
def editors(
    config: Path | None = typer.Option(None, "--config", "-c", help="Configuration file path"),
    help: bool = typer.Option(
        False,
        "--help",
        callback=help_callback,
        expose_value=False,
        is_eager=True,
        help="Show this message and exit.",
    ),
) -> None:
    """List available editors in configuration."""
    try:
        manager = MCPManager(config)
        available_editors = manager.get_available_editors()

        print(f"{Fore.CYAN}📝 Available Editors:{Style.RESET_ALL}")
        for editor in available_editors:
            print(f"  - {editor}")

    except MCPCommanderError as e:
        print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        raise typer.Exit(1) from None


@app.command()
def examples(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable debug logging"),
    help: bool = typer.Option(
        False,
        "--help",
        callback=help_callback,
        expose_value=False,
        is_eager=True,
        help="Show this message and exit.",
    ),
) -> None:
    """Show examples of MCP server configuration formats."""
    if verbose or VERBOSE_MODE:
        configure_debug_logging()

    from mcpcommander.utils.config_parser import print_transport_examples

    try:
        print_transport_examples()

        # Always show usage examples (no longer dependent on verbose flag)
        print(f"\n{Fore.CYAN}💡 Usage Examples:{Style.RESET_ALL}")
        print(f"{Fore.WHITE}  # Add STDIO server (traditional):{Style.RESET_ALL}")
        print(
            f'{Fore.GREEN}  mcp add server my-server "npx @modelcontextprotocol/server-filesystem /Users/user"{Style.RESET_ALL}'
        )
        print()
        print(f"{Fore.WHITE}  # Add HTTP transport server:{Style.RESET_ALL}")
        http_config = '{"transport": {"type": "http", "host": "localhost", "port": 3000}}'
        print(f"{Fore.GREEN}  mcp add server api-server '{http_config}'{Style.RESET_ALL}")
        print()
        print(f"{Fore.WHITE}  # Add WebSocket server:{Style.RESET_ALL}")
        ws_config = '{"transport": {"type": "websocket", "url": "ws://localhost:8080/mcp"}}'
        print(f"{Fore.GREEN}  mcp add server ws-server '{ws_config}'{Style.RESET_ALL}")
        print()
        print(f"{Fore.WHITE}  # Quick URL format (auto-detects transport):{Style.RESET_ALL}")
        print(
            f'{Fore.GREEN}  mcp add server sse-server "https://example.com/mcp/stream"{Style.RESET_ALL}'
        )

    except Exception as e:
        print(f"{Fore.RED}{UNICODE_CHARS['cross']} Error showing examples: {e}{Style.RESET_ALL}")
        if verbose or VERBOSE_MODE:
            logger.exception("Unexpected error in examples command")
        raise typer.Exit(1) from e


# =============================================================================
# CONFIG COMMANDS
# =============================================================================


@config_app.command("servers")
def config_servers(
    editor: str | None = typer.Argument(None, help="Specific editor to list servers for"),
    config: Path | None = typer.Option(None, "--config", "-c", help="Configuration file path"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable debug logging"),
    help: bool = typer.Option(
        False,
        "--help",
        callback=help_callback,
        expose_value=False,
        is_eager=True,
        help="Show this message and exit.",
    ),
) -> None:
    """List configured MCP servers."""
    if verbose or VERBOSE_MODE:
        configure_debug_logging()
    try:
        manager = MCPManager(config)
        servers = manager.list_servers(editor)

        if not servers or not any(servers.values()):
            print(
                f"{Fore.YELLOW}{UNICODE_CHARS['cross']} No MCP servers configured{Style.RESET_ALL}"
            )
            return

        # Create rich table
        table = Table(title="Configured MCP Servers")
        table.add_column("Editor", style="cyan", no_wrap=True)
        table.add_column("Server Name", style="magenta")
        table.add_column("Transport", style="blue")
        table.add_column("Command/URL", style="green")
        table.add_column("Details", style="white", max_width=30)

        for editor_name, editor_servers in servers.items():
            if not editor_servers:
                continue
            for server_name, server_config in editor_servers.items():
                command = server_config.get("command", "")
                args = server_config.get("args", [])
                transport = server_config.get("transport", {})

                if transport:
                    transport_type = transport.get("type", "Unknown").upper()
                    if transport_type == "HTTP":
                        command_display = f"{transport.get('host', '')}:{transport.get('port', '')}"
                        details = "HTTP Server"
                    elif transport_type == "WEBSOCKET":
                        command_display = transport.get("url", "")
                        details = "WebSocket"
                    else:
                        command_display = str(transport)
                        details = transport_type
                else:
                    transport_type = "STDIO"
                    command_display = command
                    details = " ".join(args[:3]) if args else ""
                    if len(args) > 3:
                        details += "..."

                table.add_row(
                    editor_name.upper(), server_name, transport_type, command_display, details
                )

        console.print(table)

    except MCPCommanderError as e:
        print(f"{Fore.RED}{UNICODE_CHARS['cross']} {e}{Style.RESET_ALL}")
        if e.details:
            print(f"{Fore.YELLOW}   Details: {e.details}{Style.RESET_ALL}")
        raise typer.Exit(1) from None
    except Exception as e:
        print(f"{Fore.RED}❌ Unexpected error: {e}{Style.RESET_ALL}")
        if verbose or VERBOSE_MODE:
            logger.exception("Unexpected error in config servers command")
        raise typer.Exit(1) from e


@config_app.command("show")
def config_show(
    config: Path | None = typer.Option(None, "--config", "-c", help="Configuration file path"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable debug logging"),
    help: bool = typer.Option(
        False,
        "--help",
        callback=help_callback,
        expose_value=False,
        is_eager=True,
        help="Show this message and exit.",
    ),
) -> None:
    """Show status of all editor configurations."""
    if verbose or VERBOSE_MODE:
        configure_debug_logging()
    try:
        manager = MCPManager(config)
        status_info = manager.get_status()

        print(f"{Fore.CYAN}{UNICODE_CHARS['line'] * 50}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}         MCP Commander Configuration Status{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{UNICODE_CHARS['line'] * 50}{Style.RESET_ALL}")

        # Configuration summary
        total_editors = len(status_info.get("editors", {}))
        total_servers = sum(
            len(info.get("servers", {})) for info in status_info.get("editors", {}).values()
        )

        print(f"\n{Fore.WHITE}📋 Configuration Summary:{Style.RESET_ALL}")
        print(f"   📁 Configuration File: {status_info.get('config_file', 'Unknown')}")
        print(f"   🎛️  Configured Editors: {total_editors}")
        print(f"   🚀 Total MCP Servers: {total_servers}")

        # Editor status
        print(f"\n{Fore.WHITE}📊 Editor Status:{Style.RESET_ALL}")
        editors = status_info.get("editors", {})

        if not editors:
            print(f"   {Fore.YELLOW}⚠️  No editors configured{Style.RESET_ALL}")
        else:
            for editor_name, editor_info in editors.items():
                config_path = editor_info.get("config_path", "Unknown")
                exists = editor_info.get("exists", False)
                server_count = len(editor_info.get("servers", {}))

                status_icon = UNICODE_CHARS["checkmark"] if exists else UNICODE_CHARS["cross"]
                status_color = Fore.GREEN if exists else Fore.RED

                print(
                    f"   {status_color}{status_icon} {editor_name.upper():<12} ({server_count} servers){Style.RESET_ALL}"
                )
                print(f"      📄 {config_path}")

        print(f"\n{Fore.CYAN}{UNICODE_CHARS['line'] * 50}{Style.RESET_ALL}")

    except MCPCommanderError as e:
        print(f"{Fore.RED}{UNICODE_CHARS['cross']} {e}{Style.RESET_ALL}")
        if e.details:
            print(f"{Fore.YELLOW}   Details: {e.details}{Style.RESET_ALL}")
        raise typer.Exit(1) from None
    except Exception as e:
        print(f"{Fore.RED}❌ Unexpected error: {e}{Style.RESET_ALL}")
        if verbose or VERBOSE_MODE:
            logger.exception("Unexpected error in config show command")
        raise typer.Exit(1) from e


@config_app.command("path")
def config_path(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable debug logging"),
    help: bool = typer.Option(
        False,
        "--help",
        callback=help_callback,
        expose_value=False,
        is_eager=True,
        help="Show this message and exit.",
    ),
) -> None:
    """Display the absolute path to MCP Commander's configuration file."""
    if verbose or VERBOSE_MODE:
        configure_debug_logging()

    try:
        manager = MCPManager()
        config_path = manager.get_config_path()

        print(f"{Fore.CYAN}📂 MCP Commander Configuration Location{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{UNICODE_CHARS['line'] * 50}{Style.RESET_ALL}")
        print(f"\n{Fore.WHITE}Configuration File:{Style.RESET_ALL}")
        print(f"   📄 {config_path}")
        print(f"\n{Fore.WHITE}Configuration Directory:{Style.RESET_ALL}")
        print(f"   📁 {config_path.parent}")

        # Check if file exists
        if config_path.exists():
            print(
                f"\n{Fore.GREEN}{UNICODE_CHARS['checkmark']} Configuration file exists{Style.RESET_ALL}"
            )
        else:
            print(
                f"\n{Fore.YELLOW}⚠️  Configuration file does not exist (will be created on first use){Style.RESET_ALL}"
            )

        print(f"\n{Fore.CYAN}💡 Usage:{Style.RESET_ALL}")
        print("   You can specify a custom config file with: --config /path/to/config.json")
        print("   The default location follows your OS conventions:")
        print("   • Windows: %APPDATA%\\mcpCommander\\config.json")
        print("   • macOS:   ~/Library/Application Support/mcpCommander/config.json")
        print("   • Linux:   ~/.config/mcpCommander/config.json")

    except Exception as e:
        print(f"{Fore.RED}❌ Error getting config path: {e}{Style.RESET_ALL}")
        if verbose or VERBOSE_MODE:
            logger.exception("Unexpected error in config path command")
        raise typer.Exit(1) from e


@config_app.command("reset")
def config_reset(
    include_backups: bool = typer.Option(
        False, "--include-backups", help="Also remove all backup files"
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable debug logging"),
    help: bool = typer.Option(
        False,
        "--help",
        callback=help_callback,
        expose_value=False,
        is_eager=True,
        help="Show this message and exit.",
    ),
) -> None:
    """Reset MCP Commander configuration to default (empty) state for testing autodiscovery."""
    if verbose or VERBOSE_MODE:
        configure_debug_logging()
    try:
        if not force:
            print(
                f"{Fore.YELLOW}⚠️  This will reset MCP Commander to its default (empty) configuration.{Style.RESET_ALL}"
            )
            print(
                f"{Fore.WHITE}This is useful for testing the autodiscovery functionality.{Style.RESET_ALL}"
            )

            if include_backups:
                print(
                    f"{Fore.RED}⚠️  This will also DELETE ALL BACKUP FILES permanently!{Style.RESET_ALL}"
                )

            if not confirm_action("Are you sure you want to reset the configuration?"):
                print(f"{Fore.CYAN}Operation cancelled{Style.RESET_ALL}")
                return

        manager = MCPManager()
        manager.reset_configuration(include_backups=include_backups)

        print(
            f"{Fore.GREEN}{UNICODE_CHARS['checkmark']} Configuration reset to empty state{Style.RESET_ALL}"
        )

        if include_backups:
            print(
                f"{Fore.GREEN}{UNICODE_CHARS['checkmark']} All backup files removed{Style.RESET_ALL}"
            )

        print(f"\n{Fore.CYAN}💡 Next steps:{Style.RESET_ALL}")
        print("   1. Run 'mcp discover' to find MCP configurations")
        print("   2. Run 'mcp config show' to see the discovered setup")
        print("   3. Start adding servers with 'mcp add server'")

    except MCPCommanderError as e:
        print(f"{Fore.RED}{UNICODE_CHARS['cross']} {e}{Style.RESET_ALL}")
        if e.details:
            print(f"{Fore.YELLOW}   Details: {e.details}{Style.RESET_ALL}")
        raise typer.Exit(1) from None
    except Exception as e:
        print(f"{Fore.RED}❌ Unexpected error: {e}{Style.RESET_ALL}")
        if verbose or VERBOSE_MODE:
            logger.exception("Unexpected error in config reset command")
        raise typer.Exit(1) from e


@config_app.command("help")
def config_help() -> None:
    """Show help for config commands."""
    print(f"{Fore.CYAN}📖 Config Commands Help{Style.RESET_ALL}")
    print(f"{Fore.BLUE}{'=' * 30}{Style.RESET_ALL}")
    print()
    print(f"{Fore.GREEN}mcp config servers{Style.RESET_ALL} - List configured MCP servers")
    print(f"  {Fore.WHITE}mcp config servers{Style.RESET_ALL}")
    print(f"  {Fore.WHITE}mcp config servers claude-code{Style.RESET_ALL}")
    print()
    print(f"{Fore.GREEN}mcp config show{Style.RESET_ALL} - Show configuration status")
    print(f"  {Fore.WHITE}mcp config show{Style.RESET_ALL}")
    print()
    print(f"{Fore.GREEN}mcp config path{Style.RESET_ALL} - Show configuration file path")
    print(f"  {Fore.WHITE}mcp config path{Style.RESET_ALL}")
    print()
    print(f"{Fore.GREEN}mcp config reset{Style.RESET_ALL} - Reset configuration to empty state")
    print(f"  {Fore.WHITE}mcp config reset{Style.RESET_ALL}")
    print(f"  {Fore.WHITE}mcp config reset --include-backups{Style.RESET_ALL}")
    print()
    print(f"{Fore.YELLOW}💡 Use --help with any subcommand for detailed options{Style.RESET_ALL}")


@app.command()
def version(
    help: bool = typer.Option(
        False,
        "--help",
        callback=help_callback,
        expose_value=False,
        is_eager=True,
        help="Show this message and exit.",
    ),
) -> None:
    """Show version information."""
    print(f"MCP Commander version {__version__}")


@app.command()
def help() -> None:
    """Show help information (alias for --help)."""
    # Show help by calling the app with --help
    import sys

    sys.argv = [sys.argv[0], "--help"]
    app()


def main() -> None:
    """Entry point for the CLI application."""
    try:
        app()
    except KeyboardInterrupt:
        print(
            f"\n{Fore.YELLOW}{UNICODE_CHARS['stop']} Operation cancelled by user{Style.RESET_ALL}"
        )
        sys.exit(130)  # Standard exit code for SIGINT
    except Exception as e:
        print(f"{Fore.RED}{UNICODE_CHARS['cross']} Fatal error: {e}{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    main()
