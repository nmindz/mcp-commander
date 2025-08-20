"""CLI command examples for verbose help output."""

import sys

from colorama import Fore, Style, init

# Initialize colorama
init()


def get_command_examples() -> dict[str, list[str]]:
    """Get examples for each CLI command."""
    return {
        "add": [
            'mcp add server my-server "npx @modelcontextprotocol/server-filesystem /Users/user"',
            'mcp add server api-server \'{"transport": {"type": "http", "host": "localhost", "port": 3000}}\' claude-code',
            'mcp add server ws-server "ws://localhost:8080/mcp" vscode',
            'mcp add server brave-search "npx -y @modelcontextprotocol/server-brave-search" --config custom.json',
            'mcp add server global-server "npx @modelcontextprotocol/server-filesystem /tmp" --all',
            'mcp add editor windsurf "~/.codeium/windsurf/mcp_config.json" --jsonpath mcpServers',
        ],
        "remove": [
            "mcp remove server my-server",
            "mcp remove server old-server claude-code",
            "mcp remove server test-api vscode",
            "mcp remove editor windsurf",
        ],
        "discover": ["mcp discover", "mcp discover --verbose"],
        "editors": ["mcp editors", "mcp editors --config custom.json"],
        "backup": [
            "mcp backup create",
            "mcp backup create claude-code --description 'Before update'",
            "mcp backup list",
            "mcp backup restore",
            "mcp backup delete",
            "mcp backup config --max-backups 20",
        ],
        "config": [
            "mcp config servers",
            "mcp config servers claude-code",
            "mcp config show",
            "mcp config path",
            "mcp config reset",
            "mcp config reset --include-backups",
        ],
        "examples": ["mcp examples"],
        "version": ["mcp version"],
    }


def should_show_examples() -> bool:
    """Check if we should show examples based on command line args."""
    return "--help" in sys.argv


def print_command_examples(command_name: str) -> None:
    """Print examples for a specific command."""
    examples = get_command_examples()
    command_examples = examples.get(command_name, [])

    if not command_examples:
        return

    print(f"\n{Fore.CYAN}💡 Examples:{Style.RESET_ALL}")
    for example in command_examples:
        print(f"{Fore.GREEN}  {example}{Style.RESET_ALL}")
    print()


def add_examples_to_help(command_name: str) -> None:
    """Add examples to help output if --verbose is used with --help."""
    if should_show_examples():
        print_command_examples(command_name)


class ExampleRichHelpFormatter:
    """Custom help formatter that adds examples when --verbose is used."""

    @staticmethod
    def add_examples_to_command(command_name: str) -> None:
        """Add examples after help is shown."""
        if should_show_examples():
            # Small delay to ensure help is shown first
            import time

            time.sleep(0.1)
            print_command_examples(command_name)
