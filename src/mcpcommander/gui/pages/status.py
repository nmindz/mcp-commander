"""System status monitoring dashboard."""

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


class StatusPage(QWidget):
    """System status page."""
    
    # Signals
    notification_requested = Signal(str, str)  # message, type
    
    def __init__(self, manager: MCPManager, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.manager = manager
        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup the status page UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("System Status")
        title_label.setObjectName("pageTitle")
        title_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        
        check_status_btn = QPushButton("Check Status")
        check_status_btn.clicked.connect(self.check_status)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(check_status_btn)
        
        layout.addLayout(header_layout)
        
        # Placeholder content
        placeholder = QLabel("System status monitoring coming soon...")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet(f"color: {PyOneDarkColors.TEXT_SECONDARY}; font-size: 14px;")
        layout.addWidget(placeholder)

    def check_status(self) -> None:
        """Check system status."""
        self.notification_requested.emit("System status checked - All OK", "success")