"""Server discovery page with progress indicators."""

from typing import Optional

from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
)

from mcpcommander.core.manager import MCPManager
from mcpcommander.gui.components.progress import CircularProgress, IndeterminateProgress
from mcpcommander.gui.theme.pyonedark import PyOneDarkColors


class DiscoveryPage(QWidget):
    """Server discovery page."""
    
    # Signals
    notification_requested = Signal(str, str)  # message, type
    
    def __init__(self, manager: MCPManager, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.manager = manager
        self.discovery_running = False
        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup the discovery page UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Server Discovery")
        title_label.setObjectName("pageTitle")
        title_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        
        self.start_discovery_btn = QPushButton("Start Discovery")
        self.start_discovery_btn.setObjectName("primaryButton")
        self.start_discovery_btn.clicked.connect(self.start_discovery)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.start_discovery_btn)
        
        layout.addLayout(header_layout)
        
        # Progress section
        progress_frame = QFrame()
        progress_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {PyOneDarkColors.SURFACE};
                border: 1px solid {PyOneDarkColors.BORDER};
                border-radius: 8px;
            }}
        """)
        progress_layout = QVBoxLayout(progress_frame)
        progress_layout.setContentsMargins(20, 20, 20, 20)
        progress_layout.setSpacing(16)
        
        # Progress indicator
        progress_row = QHBoxLayout()
        
        self.progress_widget = IndeterminateProgress(size=60)
        self.progress_widget.stop_animation()
        
        progress_info = QVBoxLayout()
        self.progress_label = QLabel("Ready to discover MCP servers")
        self.progress_detail = QLabel("Click 'Start Discovery' to scan for available servers")
        self.progress_detail.setStyleSheet(f"color: {PyOneDarkColors.TEXT_SECONDARY};")
        
        progress_info.addWidget(self.progress_label)
        progress_info.addWidget(self.progress_detail)
        
        progress_row.addWidget(self.progress_widget)
        progress_row.addLayout(progress_info)
        progress_row.addStretch()
        
        progress_layout.addLayout(progress_row)
        layout.addWidget(progress_frame)
        
        # Results placeholder
        self.results_label = QLabel("Discovery results will appear here...")
        self.results_label.setAlignment(Qt.AlignCenter)
        self.results_label.setStyleSheet(f"color: {PyOneDarkColors.TEXT_SECONDARY}; font-size: 14px;")
        layout.addWidget(self.results_label)

    def start_discovery(self) -> None:
        """Start server discovery process."""
        if self.discovery_running:
            return
        
        self.discovery_running = True
        self.start_discovery_btn.setEnabled(False)
        self.start_discovery_btn.setText("Discovering...")
        
        # Start progress animation
        self.progress_widget.start_animation()
        self.progress_label.setText("Discovering MCP servers...")
        self.progress_detail.setText("Scanning system for available servers...")
        
        # Simulate discovery process
        self.discovery_timer = QTimer()
        self.discovery_timer.timeout.connect(self.finish_discovery)
        self.discovery_timer.setSingleShot(True)
        self.discovery_timer.start(3000)  # 3 seconds

    def finish_discovery(self) -> None:
        """Finish discovery process."""
        self.discovery_running = False
        self.start_discovery_btn.setEnabled(True)
        self.start_discovery_btn.setText("Start Discovery")
        
        # Stop progress animation
        self.progress_widget.stop_animation()
        self.progress_label.setText("Discovery completed")
        self.progress_detail.setText("Found 3 available MCP servers")
        
        # Show results
        self.results_label.setText("🔍 Found servers: filesystem, sqlite, weather")
        
        self.notification_requested.emit("Server discovery completed successfully", "success")