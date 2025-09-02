"""Server management page with CRUD operations."""

from typing import Optional, Dict, Any, List
import json

from PySide6.QtCore import Qt, Signal, QThread, QObject, QTimer
from PySide6.QtGui import QFont, QIcon, QPixmap, QPainter, QColor
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QScrollArea,
    QSpacerItem,
    QSizePolicy,
    QMessageBox,
    QGroupBox,
    QCheckBox,
)

from mcpcommander.core.manager import MCPManager
from mcpcommander.schemas.config_schema import ServerConfig
from mcpcommander.gui.theme.pyonedark import PyOneDarkColors
from mcpcommander.utils.logger import get_logger

logger = get_logger(__name__)


class ServerDialog(QDialog):
    """Dialog for adding/editing servers."""
    
    def __init__(
        self,
        parent: Optional[QWidget] = None,
        server_name: str = "",
        server_config: Optional[Dict[str, Any]] = None,
        edit_mode: bool = False
    ) -> None:
        super().__init__(parent)
        
        self.server_name = server_name
        self.server_config = server_config or {}
        self.edit_mode = edit_mode
        
        self.setWindowTitle("Edit Server" if edit_mode else "Add Server")
        self.setModal(True)
        self.setMinimumSize(500, 400)
        
        self.setup_ui()
        self.apply_styling()
        
        if edit_mode and server_config:
            self.populate_fields()

    def setup_ui(self) -> None:
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        # Header
        header_label = QLabel("Edit Server Configuration" if self.edit_mode else "Add New Server")
        header_label.setObjectName("dialogTitle")
        header_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        layout.addWidget(header_label)
        
        # Form
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(12)
        
        # Server name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g., filesystem, sqlite, weather")
        if self.edit_mode:
            self.name_edit.setText(self.server_name)
            self.name_edit.setEnabled(False)  # Don't allow name changes in edit mode
        form_layout.addRow("Server Name:", self.name_edit)
        
        # Command
        self.command_edit = QLineEdit()
        self.command_edit.setPlaceholderText("e.g., npx @modelcontextprotocol/server-filesystem")
        form_layout.addRow("Command:", self.command_edit)
        
        # Arguments
        self.args_edit = QTextEdit()
        self.args_edit.setMaximumHeight(80)
        self.args_edit.setPlaceholderText('One argument per line, e.g.:\n/path/to/directory\n--option\nvalue')
        form_layout.addRow("Arguments:", self.args_edit)
        
        # Environment Variables
        env_group = QGroupBox("Environment Variables")
        env_layout = QVBoxLayout(env_group)
        
        self.env_edit = QTextEdit()
        self.env_edit.setMaximumHeight(100)
        self.env_edit.setPlaceholderText('JSON format, e.g.:\n{\n  "DEBUG": "1",\n  "PATH": "/custom/path"\n}')
        env_layout.addWidget(self.env_edit)
        
        form_layout.addRow(env_group)
        
        # Target editors
        editors_group = QGroupBox("Target Editors")
        editors_layout = QVBoxLayout(editors_group)
        
        self.editor_checkboxes = {}
        editors = ["claude-code", "claude-desktop", "cursor"]  # TODO: Get from manager
        
        for editor in editors:
            checkbox = QCheckBox(editor.replace("-", " ").title())
            checkbox.setChecked(True)  # Default to all editors
            self.editor_checkboxes[editor] = checkbox
            editors_layout.addWidget(checkbox)
        
        form_layout.addRow(editors_group)
        
        layout.addWidget(form_widget)
        
        # JSON Preview
        preview_group = QGroupBox("Configuration Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_edit = QTextEdit()
        self.preview_edit.setReadOnly(True)
        self.preview_edit.setMaximumHeight(120)
        self.preview_edit.setFont(QFont("Consolas", 9))
        preview_layout.addWidget(self.preview_edit)
        
        layout.addWidget(preview_group)
        
        # Connect for live preview
        self.command_edit.textChanged.connect(self.update_preview)
        self.args_edit.textChanged.connect(self.update_preview)
        self.env_edit.textChanged.connect(self.update_preview)
        
        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Initial preview
        self.update_preview()

    def populate_fields(self) -> None:
        """Populate fields with existing server configuration."""
        if not self.server_config:
            return
        
        self.command_edit.setText(self.server_config.get("command", ""))
        
        # Args
        args = self.server_config.get("args", [])
        if args:
            self.args_edit.setPlainText("\n".join(args))
        
        # Environment variables
        env = self.server_config.get("env", {})
        if env:
            self.env_edit.setPlainText(json.dumps(env, indent=2))

    def update_preview(self) -> None:
        """Update the JSON preview."""
        try:
            config = self.get_server_config()
            preview_text = json.dumps(config.dict(), indent=2)
            self.preview_edit.setPlainText(preview_text)
        except Exception as e:
            self.preview_edit.setPlainText(f"Invalid configuration: {e}")

    def get_server_config(self) -> ServerConfig:
        """Get the server configuration from form fields."""
        # Parse arguments
        args_text = self.args_edit.toPlainText().strip()
        args = [line.strip() for line in args_text.split('\n') if line.strip()] if args_text else []
        
        # Parse environment variables
        env_text = self.env_edit.toPlainText().strip()
        env = {}
        if env_text:
            try:
                env = json.loads(env_text)
            except json.JSONDecodeError:
                # Try to parse as simple key=value pairs
                for line in env_text.split('\n'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        env[key.strip()] = value.strip()
        
        return ServerConfig(
            command=self.command_edit.text().strip(),
            args=args if args else None,
            env=env if env else None
        )

    def get_selected_editors(self) -> List[str]:
        """Get list of selected editors."""
        return [editor for editor, checkbox in self.editor_checkboxes.items() if checkbox.isChecked()]

    def validate_input(self) -> tuple[bool, str]:
        """Validate form input."""
        if not self.name_edit.text().strip():
            return False, "Server name is required"
        
        if not self.command_edit.text().strip():
            return False, "Command is required"
        
        if not self.get_selected_editors():
            return False, "At least one editor must be selected"
        
        # Validate environment variables JSON
        env_text = self.env_edit.toPlainText().strip()
        if env_text:
            try:
                json.loads(env_text)
            except json.JSONDecodeError:
                # Check if it's key=value format
                valid_pairs = True
                for line in env_text.split('\n'):
                    if line.strip() and '=' not in line:
                        valid_pairs = False
                        break
                
                if not valid_pairs:
                    return False, "Environment variables must be valid JSON or key=value pairs"
        
        return True, ""

    def accept(self) -> None:
        """Accept dialog with validation."""
        valid, error_msg = self.validate_input()
        if not valid:
            QMessageBox.warning(self, "Validation Error", error_msg)
            return
        
        super().accept()

    def apply_styling(self) -> None:
        """Apply dialog styling."""
        style = f"""
        QDialog {{
            background-color: {PyOneDarkColors.BACKGROUND};
            color: {PyOneDarkColors.TEXT_PRIMARY};
        }}
        
        QLabel#dialogTitle {{
            color: {PyOneDarkColors.TEXT_PRIMARY};
            font-weight: bold;
        }}
        
        QLineEdit, QTextEdit {{
            background-color: {PyOneDarkColors.SURFACE};
            color: {PyOneDarkColors.TEXT_PRIMARY};
            border: 1px solid {PyOneDarkColors.BORDER};
            border-radius: 4px;
            padding: 8px;
        }}
        
        QLineEdit:focus, QTextEdit:focus {{
            border-color: {PyOneDarkColors.PRIMARY};
        }}
        
        QGroupBox {{
            font-weight: bold;
            color: {PyOneDarkColors.TEXT_PRIMARY};
            border: 1px solid {PyOneDarkColors.BORDER};
            border-radius: 4px;
            margin-top: 10px;
            padding-top: 10px;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 8px;
            background-color: {PyOneDarkColors.BACKGROUND};
        }}
        
        QCheckBox {{
            color: {PyOneDarkColors.TEXT_PRIMARY};
        }}
        """
        
        self.setStyleSheet(style)


class ServerWorker(QObject):
    """Worker for server operations."""
    
    # Signals
    servers_loaded = Signal(dict)
    server_added = Signal(str, str)  # server_name, message
    server_removed = Signal(str, str)  # server_name, message
    server_updated = Signal(str, str)  # server_name, message
    error_occurred = Signal(str)
    
    def __init__(self, manager: MCPManager) -> None:
        super().__init__()
        self.manager = manager

    def load_servers(self) -> None:
        """Load servers from all editors."""
        try:
            servers = self.manager.list_servers()
            self.servers_loaded.emit(servers)
        except Exception as e:
            logger.error(f"Failed to load servers: {e}")
            self.error_occurred.emit(f"Failed to load servers: {e}")

    def add_server(self, name: str, config: ServerConfig, editors: List[str]) -> None:
        """Add server to specified editors."""
        try:
            for editor in editors:
                self.manager.add_server(name, config, editor)
            
            editor_list = ", ".join(editors)
            self.server_added.emit(name, f"Server '{name}' added to {editor_list}")
            
        except Exception as e:
            logger.error(f"Failed to add server: {e}")
            self.error_occurred.emit(f"Failed to add server: {e}")

    def remove_server(self, name: str, editors: List[str]) -> None:
        """Remove server from specified editors."""
        try:
            for editor in editors:
                self.manager.remove_server(name, editor)
            
            editor_list = ", ".join(editors)
            self.server_removed.emit(name, f"Server '{name}' removed from {editor_list}")
            
        except Exception as e:
            logger.error(f"Failed to remove server: {e}")
            self.error_occurred.emit(f"Failed to remove server: {e}")


class ServersPage(QWidget):
    """Server management page."""
    
    # Signals
    notification_requested = Signal(str, str)  # message, type
    
    def __init__(self, manager: MCPManager, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        
        self.manager = manager
        self.servers_data: Dict[str, Dict[str, Any]] = {}
        
        # Worker thread
        self.worker_thread = QThread()
        self.worker = ServerWorker(manager)
        self.worker.moveToThread(self.worker_thread)
        
        # Connect worker signals
        self.worker.servers_loaded.connect(self.update_servers_table)
        self.worker.server_added.connect(self.on_server_added)
        self.worker.server_removed.connect(self.on_server_removed)
        self.worker.error_occurred.connect(self.handle_error)
        self.worker_thread.started.connect(self.worker.load_servers)
        
        self.setup_ui()
        self.load_servers()

    def setup_ui(self) -> None:
        """Setup the servers page UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Server Management")
        title_label.setObjectName("pageTitle")
        title_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        
        # Action buttons
        self.add_btn = QPushButton("Add Server")
        self.add_btn.setObjectName("primaryButton")
        self.add_btn.clicked.connect(self.add_server)
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.add_btn)
        header_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Search and filter
        filter_layout = QHBoxLayout()
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search servers...")
        self.search_edit.textChanged.connect(self.filter_servers)
        
        self.editor_filter = QComboBox()
        self.editor_filter.addItems(["All Editors", "Claude Code", "Claude Desktop", "Cursor"])
        self.editor_filter.currentTextChanged.connect(self.filter_servers)
        
        filter_layout.addWidget(QLabel("Search:"))
        filter_layout.addWidget(self.search_edit)
        filter_layout.addWidget(QLabel("Filter by Editor:"))
        filter_layout.addWidget(self.editor_filter)
        filter_layout.addStretch()
        
        layout.addLayout(filter_layout)
        
        # Servers table
        self.servers_table = QTableWidget()
        self.servers_table.setColumnCount(5)
        self.servers_table.setHorizontalHeaderLabels([
            "Server Name", "Command", "Editors", "Status", "Actions"
        ])
        
        # Configure table
        header = self.servers_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        self.servers_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.servers_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.servers_table)
        
        self.apply_styling()

    def apply_styling(self) -> None:
        """Apply page styling."""
        style = f"""
        QLabel#pageTitle {{
            color: {PyOneDarkColors.TEXT_PRIMARY};
            font-weight: bold;
        }}
        
        QPushButton#primaryButton {{
            background-color: {PyOneDarkColors.PRIMARY};
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: 500;
        }}
        
        QPushButton#primaryButton:hover {{
            background-color: #528bdb;
        }}
        
        QLineEdit {{
            background-color: {PyOneDarkColors.SURFACE};
            color: {PyOneDarkColors.TEXT_PRIMARY};
            border: 1px solid {PyOneDarkColors.BORDER};
            border-radius: 4px;
            padding: 6px 8px;
        }}
        
        QLineEdit:focus {{
            border-color: {PyOneDarkColors.PRIMARY};
        }}
        
        QComboBox {{
            background-color: {PyOneDarkColors.SURFACE};
            color: {PyOneDarkColors.TEXT_PRIMARY};
            border: 1px solid {PyOneDarkColors.BORDER};
            border-radius: 4px;
            padding: 6px 8px;
        }}
        
        QTableWidget {{
            background-color: {PyOneDarkColors.SURFACE};
            color: {PyOneDarkColors.TEXT_PRIMARY};
            border: 1px solid {PyOneDarkColors.BORDER};
            border-radius: 6px;
            gridline-color: {PyOneDarkColors.SEPARATOR};
        }}
        
        QTableWidget::item {{
            padding: 8px;
            border-bottom: 1px solid {PyOneDarkColors.SEPARATOR};
        }}
        
        QTableWidget::item:selected {{
            background-color: {PyOneDarkColors.PRIMARY};
            color: white;
        }}
        
        QHeaderView::section {{
            background-color: {PyOneDarkColors.SURFACE_VARIANT};
            color: {PyOneDarkColors.TEXT_PRIMARY};
            border: none;
            border-bottom: 1px solid {PyOneDarkColors.BORDER};
            padding: 8px 12px;
            font-weight: 600;
        }}
        """
        
        self.setStyleSheet(style)

    def load_servers(self) -> None:
        """Load servers data."""
        if not self.worker_thread.isRunning():
            self.worker_thread.start()

    def refresh(self) -> None:
        """Refresh servers data."""
        logger.info("Refreshing servers data")
        self.worker.load_servers()

    def update_servers_table(self, servers_data: Dict[str, Dict[str, Any]]) -> None:
        """Update the servers table with new data."""
        self.servers_data = servers_data
        
        # Create a flattened list of servers
        all_servers = {}
        for editor, editor_servers in servers_data.items():
            for server_name, server_config in editor_servers.items():
                if server_name not in all_servers:
                    all_servers[server_name] = {
                        "config": server_config,
                        "editors": []
                    }
                all_servers[server_name]["editors"].append(editor)
        
        # Update table
        self.servers_table.setRowCount(len(all_servers))
        
        for row, (server_name, server_info) in enumerate(all_servers.items()):
            config = server_info["config"]
            editors = server_info["editors"]
            
            # Server name
            self.servers_table.setItem(row, 0, QTableWidgetItem(server_name))
            
            # Command
            command = config.get("command", "")
            self.servers_table.setItem(row, 1, QTableWidgetItem(command))
            
            # Editors
            editors_text = ", ".join([e.replace("-", " ").title() for e in editors])
            self.servers_table.setItem(row, 2, QTableWidgetItem(editors_text))
            
            # Status (placeholder)
            status_item = QTableWidgetItem("Active")
            status_item.setForeground(QColor(PyOneDarkColors.SUCCESS))
            self.servers_table.setItem(row, 3, status_item)
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 4, 4, 4)
            actions_layout.setSpacing(4)
            
            edit_btn = QPushButton("Edit")
            edit_btn.setObjectName("actionButton")
            edit_btn.clicked.connect(lambda checked, name=server_name: self.edit_server(name))
            
            remove_btn = QPushButton("Remove")
            remove_btn.setObjectName("dangerButton")
            remove_btn.clicked.connect(lambda checked, name=server_name: self.remove_server(name))
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(remove_btn)
            actions_layout.addStretch()
            
            self.servers_table.setCellWidget(row, 4, actions_widget)
        
        # Apply additional button styling
        self.apply_button_styling()

    def apply_button_styling(self) -> None:
        """Apply styling to action buttons."""
        button_style = f"""
        QPushButton#actionButton {{
            background-color: {PyOneDarkColors.PRIMARY};
            color: white;
            border: none;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
        }}
        
        QPushButton#actionButton:hover {{
            background-color: #528bdb;
        }}
        
        QPushButton#dangerButton {{
            background-color: {PyOneDarkColors.ERROR};
            color: white;
            border: none;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
        }}
        
        QPushButton#dangerButton:hover {{
            background-color: #d55a64;
        }}
        """
        
        # Apply to all action buttons
        for row in range(self.servers_table.rowCount()):
            actions_widget = self.servers_table.cellWidget(row, 4)
            if actions_widget:
                actions_widget.setStyleSheet(button_style)

    def filter_servers(self) -> None:
        """Filter servers based on search and editor selection."""
        search_text = self.search_edit.text().lower()
        editor_filter = self.editor_filter.currentText()
        
        for row in range(self.servers_table.rowCount()):
            # Get row data
            server_name = self.servers_table.item(row, 0).text().lower()
            command = self.servers_table.item(row, 1).text().lower()
            editors = self.servers_table.item(row, 2).text()
            
            # Check search filter
            search_match = (search_text in server_name or 
                           search_text in command or 
                           search_text in editors.lower())
            
            # Check editor filter
            editor_match = (editor_filter == "All Editors" or 
                           editor_filter.replace(" ", "-").lower() in editors.lower())
            
            # Show/hide row
            self.servers_table.setRowHidden(row, not (search_match and editor_match))

    def add_server(self) -> None:
        """Show add server dialog."""
        dialog = ServerDialog(self)
        if dialog.exec() == QDialog.Accepted:
            try:
                server_name = dialog.name_edit.text().strip()
                server_config = dialog.get_server_config()
                selected_editors = dialog.get_selected_editors()
                
                # Add server using worker
                self.worker.add_server(server_name, server_config, selected_editors)
                
            except Exception as e:
                self.notification_requested.emit(f"Failed to add server: {e}", "error")

    def edit_server(self, server_name: str) -> None:
        """Show edit server dialog."""
        # Find server config from any editor that has it
        server_config = None
        for editor_servers in self.servers_data.values():
            if server_name in editor_servers:
                server_config = editor_servers[server_name]
                break
        
        if not server_config:
            self.notification_requested.emit(f"Server '{server_name}' not found", "error")
            return
        
        dialog = ServerDialog(self, server_name, server_config, edit_mode=True)
        if dialog.exec() == QDialog.Accepted:
            try:
                new_config = dialog.get_server_config()
                selected_editors = dialog.get_selected_editors()
                
                # Remove from all editors first, then add to selected ones
                # This handles the case where editors were deselected
                current_editors = []
                for editor, editor_servers in self.servers_data.items():
                    if server_name in editor_servers:
                        current_editors.append(editor)
                
                # Remove from editors that are no longer selected
                for editor in current_editors:
                    if editor not in selected_editors:
                        self.worker.remove_server(server_name, [editor])
                
                # Add/update in selected editors
                self.worker.add_server(server_name, new_config, selected_editors)
                
            except Exception as e:
                self.notification_requested.emit(f"Failed to edit server: {e}", "error")

    def remove_server(self, server_name: str) -> None:
        """Remove server after confirmation."""
        # Find which editors have this server
        editors_with_server = []
        for editor, editor_servers in self.servers_data.items():
            if server_name in editor_servers:
                editors_with_server.append(editor)
        
        if not editors_with_server:
            self.notification_requested.emit(f"Server '{server_name}' not found", "error")
            return
        
        # Confirm removal
        editor_list = ", ".join([e.replace("-", " ").title() for e in editors_with_server])
        reply = QMessageBox.question(
            self,
            "Confirm Removal",
            f"Remove server '{server_name}' from {editor_list}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.worker.remove_server(server_name, editors_with_server)

    def on_server_added(self, server_name: str, message: str) -> None:
        """Handle server added signal."""
        self.notification_requested.emit(message, "success")
        self.refresh()

    def on_server_removed(self, server_name: str, message: str) -> None:
        """Handle server removed signal."""
        self.notification_requested.emit(message, "success")
        self.refresh()

    def handle_error(self, error_message: str) -> None:
        """Handle worker errors."""
        logger.error(f"Servers page error: {error_message}")
        self.notification_requested.emit(error_message, "error")

    def closeEvent(self, event) -> None:
        """Clean up on close."""
        self.worker_thread.quit()
        self.worker_thread.wait()
        event.accept()