"""Interactive utilities for user selection and confirmation."""

import os
import sys
from collections.abc import Callable
from typing import Any

from colorama import Fore, Style

from mcpcommander.schemas.config_schema import BackupInfo
from mcpcommander.utils.logger import get_logger

logger = get_logger(__name__)


class InteractiveSelector:
    """Interactive selector for choosing items from a list."""

    def __init__(self, items: list[Any], formatter: Callable[[Any], str] | None = None) -> None:
        """Initialize the selector.

        Args:
            items: List of items to select from
            formatter: Function to format items for display (defaults to str())
        """
        self.items = items
        self.formatter = formatter or str
        self.current_index = 0

    def select(self, prompt: str = "Select an item", allow_cancel: bool = True) -> Any | None:
        """Display interactive selection menu.

        Args:
            prompt: Prompt to display
            allow_cancel: Whether to allow canceling the selection

        Returns:
            Selected item or None if canceled
        """
        if not self.items:
            print(f"{Fore.YELLOW}No items available for selection.{Style.RESET_ALL}")
            return None

        if len(self.items) == 1:
            # Only one item, ask for confirmation
            item = self.items[0]
            formatted = self.formatter(item)

            if self._confirm(f"Use {formatted}?"):
                return item
            else:
                return None

        # Check if we can use interactive mode
        if not self._can_use_interactive():
            return self._fallback_selection(prompt, allow_cancel)

        try:
            return self._interactive_selection(prompt, allow_cancel)
        except Exception as e:
            logger.warning(f"Interactive selection failed: {e}")
            return self._fallback_selection(prompt, allow_cancel)

    def _can_use_interactive(self) -> bool:
        """Check if interactive mode is available."""
        # Check if running in a proper terminal
        if not sys.stdin.isatty() or not sys.stdout.isatty():
            return False

        # Check if not running in CI/automated environment
        ci_vars = ["CI", "GITHUB_ACTIONS", "GITLAB_CI", "JENKINS_URL"]
        if any(os.getenv(var) for var in ci_vars):
            return False

        return True

    def _interactive_selection(self, prompt: str, allow_cancel: bool) -> Any | None:
        """Handle interactive selection with keyboard navigation."""
        try:
            # Try to use getch for cross-platform keyboard input
            if os.name == "nt":  # Windows
                import msvcrt

                def getch():
                    return msvcrt.getch().decode("utf-8", errors="ignore")
            else:  # Unix/Linux/macOS
                import termios
                import tty

                def getch():
                    fd = sys.stdin.fileno()
                    old_settings = termios.tcgetattr(fd)
                    try:
                        tty.raw(sys.stdin.fileno())
                        char = sys.stdin.read(1)
                    finally:
                        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                    return char

        except ImportError:
            # Fall back to line-based input
            return self._fallback_selection(prompt, allow_cancel)

        # Hide cursor
        sys.stdout.write("\033[?25l")

        try:
            while True:
                # Clear screen and show menu
                self._draw_menu(prompt, allow_cancel)

                # Get user input
                try:
                    key = getch()
                except (KeyboardInterrupt, EOFError):
                    if allow_cancel:
                        return None
                    continue

                # Handle navigation
                if key in ["q", "\x1b"]:  # 'q' or ESC key
                    if allow_cancel:
                        return None
                elif key in ["k", "A", "\x48"]:  # 'k', up arrow, or up on Windows
                    self.current_index = (self.current_index - 1) % len(self.items)
                elif key in ["j", "B", "\x50"]:  # 'j', down arrow, or down on Windows
                    self.current_index = (self.current_index + 1) % len(self.items)
                elif key in ["\r", "\n", " "]:  # Enter or space
                    return self.items[self.current_index]
                elif key.isdigit():
                    # Direct number selection
                    num = int(key) - 1
                    if 0 <= num < len(self.items):
                        self.current_index = num
                        return self.items[num]

        finally:
            # Show cursor
            sys.stdout.write("\033[?25h")
            # Clear the menu
            sys.stdout.write(f"\033[{len(self.items) + 4}A\033[J")
            sys.stdout.flush()

    def _draw_menu(self, prompt: str, allow_cancel: bool) -> None:
        """Draw the selection menu."""
        # Move to top and clear
        sys.stdout.write("\033[H\033[J")

        # Show prompt
        print(f"{Fore.CYAN}{prompt}:{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{'=' * len(prompt)}{Style.RESET_ALL}")
        print()

        # Show items
        for i, item in enumerate(self.items):
            formatted = self.formatter(item)

            if i == self.current_index:
                # Highlight current selection
                print(f"{Fore.GREEN}► {i + 1}. {formatted}{Style.RESET_ALL}")
            else:
                print(f"  {i + 1}. {formatted}")

        print()

        # Show help
        help_text = "Use ↑↓ or j/k to navigate, Enter/Space to select"
        if allow_cancel:
            help_text += ", ESC/q to cancel"
        print(f"{Fore.YELLOW}{help_text}{Style.RESET_ALL}")

        sys.stdout.flush()

    def _fallback_selection(self, prompt: str, allow_cancel: bool) -> Any | None:
        """Fallback selection using numbered list input."""
        print(f"{Fore.CYAN}{prompt}:{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{'=' * len(prompt)}{Style.RESET_ALL}")
        print()

        # Display numbered list
        for i, item in enumerate(self.items, 1):
            formatted = self.formatter(item)
            print(f"  {i}. {formatted}")

        print()

        while True:
            try:
                if allow_cancel:
                    user_input = (
                        input(f"Select (1-{len(self.items)}) or '0' to cancel: ").strip().lower()
                    )
                    if user_input in ["0", "c", "cancel", "q", "quit"]:
                        return None
                else:
                    user_input = input(f"Select (1-{len(self.items)}): ").strip()

                if user_input.isdigit():
                    choice = int(user_input) - 1
                    if 0 <= choice < len(self.items):
                        return self.items[choice]

                print(f"{Fore.RED}Invalid selection. Please try again.{Style.RESET_ALL}")

            except (KeyboardInterrupt, EOFError):
                if allow_cancel:
                    return None
                print()  # New line after ^C
                continue

    def _confirm(self, message: str, default: bool = True) -> bool:
        """Ask for confirmation."""
        choices = "[Y/n]" if default else "[y/N]"

        try:
            response = input(f"{message} {choices}: ").strip().lower()

            if not response:
                return default
            elif response in ["y", "yes"]:
                return True
            elif response in ["n", "no"]:
                return False
            else:
                return default

        except (KeyboardInterrupt, EOFError):
            return False


class BackupSelector(InteractiveSelector):
    """Specialized selector for backup items."""

    def __init__(self, backups: list[BackupInfo]) -> None:
        """Initialize with backup items."""
        super().__init__(backups, self._format_backup)

    def _format_backup(self, backup: BackupInfo) -> str:
        """Format backup for display."""
        timestamp = backup.formatted_timestamp
        files_info = (
            f"{len(backup.files_backed_up)} editor(s)" if backup.files_backed_up else "0 editors"
        )

        if backup.editor_name:
            return f"{backup.backup_id} - {timestamp} - {backup.editor_name} only"
        else:
            return f"{backup.backup_id} - {timestamp} - {files_info}"


def confirm_action(message: str, default: bool = False, force: bool = False) -> bool:
    """Confirm an action with the user.

    Args:
        message: Confirmation message
        default: Default value if user just presses Enter
        force: Skip confirmation if True

    Returns:
        True if confirmed, False otherwise
    """
    if force:
        return True

    choices = "[y/N]" if not default else "[Y/n]"

    while True:
        try:
            prompt = f"{Fore.YELLOW}{message} {choices}: {Style.RESET_ALL}"
            print(prompt, end="", flush=True)
            response = input().strip().lower()

            if not response:
                return default
            elif response in ["y", "yes"]:
                return True
            elif response in ["n", "no"]:
                return False
            else:
                print(f"{Fore.RED}Please enter 'y' for yes or 'n' for no.{Style.RESET_ALL}")
                continue

        except (KeyboardInterrupt, EOFError):
            print(f"\n{Fore.RED}Cancelled by user{Style.RESET_ALL}")
            return False


def select_backup(
    backups: list[BackupInfo], prompt: str = "Select backup to restore", allow_cancel: bool = True
) -> BackupInfo | None:
    """Interactive backup selection.

    Args:
        backups: List of available backups
        prompt: Prompt message
        allow_cancel: Allow canceling the selection

    Returns:
        Selected backup or None if canceled
    """
    if not backups:
        print(f"{Fore.YELLOW}No backups available.{Style.RESET_ALL}")
        return None

    selector = BackupSelector(backups)
    return selector.select(prompt, allow_cancel)


def get_backup_description() -> str | None:
    """Get backup description from user input.

    Returns:
        Backup description or None if canceled
    """
    try:
        description = input(
            f"{Fore.CYAN}Enter backup description (optional): {Style.RESET_ALL}"
        ).strip()
        return description if description else None
    except (KeyboardInterrupt, EOFError):
        return None
