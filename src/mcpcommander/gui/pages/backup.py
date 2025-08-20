"""Backup and restore management page."""

from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
)

from mcpcommander.core.manager import MCPManager
from mcpcommander.gui.theme.pyonedark import PyOneDarkColors


class BackupPage(QWidget):
    """Backup and restore page."""
    
    # Signals
    notification_requested = Signal(str, str)  # message, type
    
    def __init__(self, manager: MCPManager, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.manager = manager
        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup the backup page UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Backup & Restore")
        title_label.setObjectName("pageTitle")
        title_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        
        create_backup_btn = QPushButton("Create Backup")
        create_backup_btn.setObjectName("primaryButton")
        create_backup_btn.clicked.connect(self.create_backup)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(create_backup_btn)
        
        layout.addLayout(header_layout)
        
        # Placeholder content
        placeholder = QLabel("Backup and restore functionality coming soon...")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet(f"color: {PyOneDarkColors.TEXT_SECONDARY}; font-size: 14px;")
        layout.addWidget(placeholder)

    def create_backup(self) -> None:
        """Create a new backup."""
        self.notification_requested.emit("Backup created successfully", "success")