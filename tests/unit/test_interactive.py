"""Unit tests for interactive utilities."""

import io
import sys
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from mcpcommander.schemas.config_schema import BackupInfo
from mcpcommander.utils.interactive import (
    InteractiveSelector,
    confirm_action,
    get_backup_description,
    select_backup,
)


class TestInteractiveSelector:
    """Test InteractiveSelector functionality."""

    def test_init_with_default_formatter(self):
        """Test initialization with default formatter."""
        items = ["item1", "item2", "item3"]
        selector = InteractiveSelector(items)
        
        assert selector.items == items
        assert selector.formatter == str
        assert selector.current_index == 0

    def test_init_with_custom_formatter(self):
        """Test initialization with custom formatter."""
        items = [1, 2, 3]
        formatter = lambda x: f"Item {x}"
        selector = InteractiveSelector(items, formatter)
        
        assert selector.items == items
        assert selector.formatter == formatter
        assert selector.current_index == 0

    @patch('builtins.input')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_select_with_direct_selection(self, mock_stdout, mock_input):
        """Test selection with direct number input."""
        items = ["item1", "item2", "item3"]
        selector = InteractiveSelector(items)
        
        # User inputs "2" to select the second item (index 1)
        mock_input.return_value = "2"
        
        result = selector.select("Choose an item:")
        
        assert result == "item2"
        
        # Check that prompt was displayed
        output = mock_stdout.getvalue()
        assert "Choose an item:" in output
        assert "1. item1" in output
        assert "2. item2" in output
        assert "3. item3" in output

    @patch('builtins.input')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_select_with_zero_cancel(self, mock_stdout, mock_input):
        """Test selection with zero to cancel."""
        items = ["item1", "item2"]
        selector = InteractiveSelector(items)
        
        mock_input.return_value = "0"
        
        result = selector.select("Choose an item:", allow_cancel=True)
        
        assert result is None

    @patch('builtins.input')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_select_with_cancel_disabled(self, mock_stdout, mock_input):
        """Test selection with cancel disabled."""
        items = ["item1", "item2"]
        selector = InteractiveSelector(items)
        
        # First try to cancel (0), then select item 1
        mock_input.side_effect = ["0", "1"]
        
        result = selector.select("Choose an item:", allow_cancel=False)
        
        assert result == "item1"

    @patch('builtins.input')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_select_with_invalid_input(self, mock_stdout, mock_input):
        """Test selection with invalid input followed by valid input."""
        items = ["item1", "item2"]
        selector = InteractiveSelector(items)
        
        # Invalid inputs followed by valid selection
        mock_input.side_effect = ["invalid", "99", "1"]
        
        result = selector.select("Choose an item:")
        
        assert result == "item1"

    @patch('builtins.input')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_select_empty_list(self, mock_stdout, mock_input):
        """Test selection with empty item list."""
        items = []
        selector = InteractiveSelector(items)
        
        result = selector.select("Choose an item:")
        
        assert result is None
        output = mock_stdout.getvalue()
        assert "No items available" in output

    @patch('builtins.input')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_select_with_custom_formatter(self, mock_stdout, mock_input):
        """Test selection with custom formatter."""
        items = [{"name": "test1", "value": 1}, {"name": "test2", "value": 2}]
        formatter = lambda x: f"{x['name']} (value: {x['value']})"
        selector = InteractiveSelector(items, formatter)
        
        mock_input.return_value = "1"
        
        result = selector.select("Choose an item:")
        
        assert result == {"name": "test1", "value": 1}
        output = mock_stdout.getvalue()
        assert "test1 (value: 1)" in output
        assert "test2 (value: 2)" in output

    @patch('builtins.input')
    @patch('mcpcommander.utils.interactive.InteractiveSelector._can_use_interactive', return_value=False)
    def test_select_keyboard_interrupt(self, mock_can_use_interactive, mock_input):
        """Test selection with keyboard interrupt."""
        items = ["item1", "item2"]
        selector = InteractiveSelector(items)
        
        mock_input.side_effect = KeyboardInterrupt()
        
        result = selector.select("Choose an item:")
        
        assert result is None

    @patch('builtins.input')
    @patch('mcpcommander.utils.interactive.InteractiveSelector._can_use_interactive', return_value=False)
    def test_select_eof_error(self, mock_can_use_interactive, mock_input):
        """Test selection with EOF error."""
        items = ["item1", "item2"]
        selector = InteractiveSelector(items)
        
        mock_input.side_effect = EOFError()
        
        result = selector.select("Choose an item:")
        
        assert result is None


class TestConfirmAction:
    """Test confirm_action functionality."""

    def test_confirm_action_with_force(self):
        """Test confirmation with force flag."""
        result = confirm_action("Are you sure?", force=True)
        assert result is True

    @patch('builtins.input')
    def test_confirm_action_yes_responses(self, mock_input):
        """Test confirmation with various yes responses."""
        yes_responses = ["y", "Y", "yes", "Yes", "YES"]
        
        for response in yes_responses:
            mock_input.return_value = response
            result = confirm_action("Are you sure?")
            assert result is True

    @patch('builtins.input')
    def test_confirm_action_no_responses(self, mock_input):
        """Test confirmation with various no responses."""
        no_responses = ["n", "N", "no", "No", "NO"]
        
        for response in no_responses:
            mock_input.return_value = response
            result = confirm_action("Are you sure?")
            assert result is False

    @patch('builtins.input')
    def test_confirm_action_empty_input_default_false(self, mock_input):
        """Test confirmation with empty input and default False."""
        mock_input.return_value = ""
        result = confirm_action("Are you sure?", default=False)
        assert result is False

    @patch('builtins.input')
    def test_confirm_action_empty_input_default_true(self, mock_input):
        """Test confirmation with empty input and default True."""
        mock_input.return_value = ""
        result = confirm_action("Are you sure?", default=True)
        assert result is True

    @patch('builtins.input')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_confirm_action_invalid_then_valid(self, mock_stdout, mock_input):
        """Test confirmation with invalid input followed by valid input."""
        mock_input.side_effect = ["maybe", "invalid", "y"]
        
        result = confirm_action("Are you sure?")
        
        assert result is True
        output = mock_stdout.getvalue()
        assert "Please enter" in output  # Error message should be shown

    @patch('builtins.input')
    def test_confirm_action_keyboard_interrupt(self, mock_input):
        """Test confirmation with keyboard interrupt."""
        mock_input.side_effect = KeyboardInterrupt()
        
        result = confirm_action("Are you sure?")
        
        assert result is False

    @patch('builtins.input')
    def test_confirm_action_eof_error(self, mock_input):
        """Test confirmation with EOF error."""
        mock_input.side_effect = EOFError()
        
        result = confirm_action("Are you sure?")
        
        assert result is False

    @patch('builtins.input')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_confirm_action_prompt_format(self, mock_stdout, mock_input):
        """Test confirmation prompt formatting."""
        mock_input.return_value = "y"
        
        # Test with default=False
        confirm_action("Delete files?", default=False)
        output = mock_stdout.getvalue()
        assert "Delete files? [y/N]:" in output
        
        # Reset stdout
        mock_stdout.truncate(0)
        mock_stdout.seek(0)
        
        # Test with default=True
        confirm_action("Continue?", default=True)
        output = mock_stdout.getvalue()
        assert "Continue? [Y/n]:" in output


class TestSelectBackup:
    """Test select_backup functionality."""

    def create_backup_info(self, backup_id: str, editors: list[str], description: str = None) -> BackupInfo:
        """Create a test BackupInfo object."""
        return BackupInfo(
            backup_id=backup_id,
            timestamp=datetime.now(),
            files_backed_up=editors,
            description=description or f"Test backup {backup_id}"
        )

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_select_backup_empty_list(self, mock_stdout):
        """Test backup selection with empty list."""
        result = select_backup([])
        
        assert result is None
        output = mock_stdout.getvalue()
        assert "No backups available" in output

    @patch('mcpcommander.utils.interactive.BackupSelector')
    def test_select_backup_with_backups(self, mock_selector_class):
        """Test backup selection with available backups."""
        backups = [
            self.create_backup_info("backup1", ["claude-code"]),
            self.create_backup_info("backup2", ["cursor"], "Test backup")
        ]
        
        mock_selector = MagicMock()
        mock_selector.select.return_value = backups[0]
        mock_selector_class.return_value = mock_selector
        
        result = select_backup(backups, "Select backup:")
        
        assert result == backups[0]
        mock_selector_class.assert_called_once_with(backups)
        mock_selector.select.assert_called_once_with("Select backup:", True)

    @patch('mcpcommander.utils.interactive.BackupSelector')
    def test_select_backup_custom_prompt(self, mock_selector_class):
        """Test backup selection with custom prompt."""
        backups = [self.create_backup_info("backup1", ["claude-code"])]
        
        mock_selector = MagicMock()
        mock_selector.select.return_value = backups[0]
        mock_selector_class.return_value = mock_selector
        
        result = select_backup(backups, "Choose a backup:", allow_cancel=False)
        
        assert result == backups[0]
        mock_selector.select.assert_called_once_with("Choose a backup:", False)

    @patch('mcpcommander.utils.interactive.BackupSelector')
    def test_select_backup_cancel(self, mock_selector_class):
        """Test backup selection with cancellation."""
        backups = [self.create_backup_info("backup1", ["claude-code"])]
        
        mock_selector = MagicMock()
        mock_selector.select.return_value = None  # User cancelled
        mock_selector_class.return_value = mock_selector
        
        result = select_backup(backups)
        
        assert result is None

    def test_select_backup_formatter_function(self):
        """Test that backup selection uses correct formatter."""
        # We can't easily test the formatter directly, but we can verify
        # that BackupInfo objects have the right display properties
        backup = self.create_backup_info("test_backup_20250818", ["claude-code"], "Test description")
        
        # These properties should be available for formatting
        assert hasattr(backup, 'backup_id')
        assert hasattr(backup, 'formatted_timestamp')  
        assert hasattr(backup, 'display_name')
        assert hasattr(backup, 'description')


class TestGetBackupDescription:
    """Test get_backup_description functionality."""

    @patch('builtins.input')
    def test_get_backup_description_with_text(self, mock_input):
        """Test getting backup description with user input."""
        mock_input.return_value = "My test backup"
        
        result = get_backup_description()
        
        assert result == "My test backup"

    @patch('builtins.input')
    def test_get_backup_description_empty(self, mock_input):
        """Test getting backup description with empty input."""
        mock_input.return_value = ""
        
        result = get_backup_description()
        
        assert result is None

    @patch('builtins.input')
    def test_get_backup_description_whitespace_only(self, mock_input):
        """Test getting backup description with whitespace only."""
        mock_input.return_value = "   "
        
        result = get_backup_description()
        
        assert result is None

    @patch('builtins.input')
    def test_get_backup_description_with_leading_trailing_spaces(self, mock_input):
        """Test getting backup description with leading/trailing spaces."""
        mock_input.return_value = "  My backup  "
        
        result = get_backup_description()
        
        assert result == "My backup"

    @patch('builtins.input')
    def test_get_backup_description_keyboard_interrupt(self, mock_input):
        """Test getting backup description with keyboard interrupt."""
        mock_input.side_effect = KeyboardInterrupt()
        
        result = get_backup_description()
        
        assert result is None

    @patch('builtins.input')
    def test_get_backup_description_eof_error(self, mock_input):
        """Test getting backup description with EOF error."""
        mock_input.side_effect = EOFError()
        
        result = get_backup_description()
        
        assert result is None

    @patch('builtins.input')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_get_backup_description_prompt(self, mock_stdout, mock_input):
        """Test backup description prompt format."""
        mock_input.return_value = "test"
        
        get_backup_description()
        
        # The actual prompt is displayed via input(), so we can't easily check it
        # But we can verify the function works without errors
        assert mock_input.called


class TestInteractiveErrorHandling:
    """Test error handling in interactive components."""

    @patch('builtins.input')
    @patch('mcpcommander.utils.interactive.logger')
    @patch('mcpcommander.utils.interactive.InteractiveSelector._can_use_interactive', return_value=False)
    def test_interactive_selector_with_logging(self, mock_can_use_interactive, mock_logger, mock_input):
        """Test that interactive components use logging properly."""
        items = ["item1", "item2"]
        selector = InteractiveSelector(items)
        
        mock_input.side_effect = KeyboardInterrupt()
        
        result = selector.select("Choose:")
        
        assert result is None
        # Logger should be available for error logging

    def test_interactive_components_import_correctly(self):
        """Test that all interactive components can be imported."""
        # This test ensures all components are properly defined
        from mcpcommander.utils.interactive import (
            InteractiveSelector,
            confirm_action, 
            get_backup_description,
            select_backup
        )
        
        assert InteractiveSelector is not None
        assert confirm_action is not None
        assert get_backup_description is not None
        assert select_backup is not None


class TestInteractivePlatformCompatibility:
    """Test platform-specific behavior of interactive components."""

    @patch('sys.platform', 'win32')
    @patch('builtins.input')
    def test_windows_compatibility(self, mock_input):
        """Test interactive components work on Windows."""
        mock_input.return_value = "y"
        
        result = confirm_action("Test?")
        
        assert result is True

    @patch('sys.platform', 'linux')
    @patch('builtins.input')
    def test_linux_compatibility(self, mock_input):
        """Test interactive components work on Linux."""
        mock_input.return_value = "y"
        
        result = confirm_action("Test?")
        
        assert result is True

    @patch('sys.platform', 'darwin')
    @patch('builtins.input')
    def test_macos_compatibility(self, mock_input):
        """Test interactive components work on macOS."""
        mock_input.return_value = "y"
        
        result = confirm_action("Test?")
        
        assert result is True