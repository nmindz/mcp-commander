"""Application settings page."""

from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QCheckBox,
    QGroupBox,
    QFormLayout,
    QLineEdit,
    QSpinBox,
)

from mcpcommander.core.manager import MCPManager
from mcpcommander.gui.theme.pyonedark import PyOneDarkColors


class SettingsPage(QWidget):
    """Application settings page."""
    
    # Signals
    notification_requested = Signal(str, str)  # message, type
    
    def __init__(self, manager: MCPManager, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.manager = manager
        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup the settings page UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Settings")
        title_label.setObjectName("pageTitle")
        title_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        
        save_btn = QPushButton("Save Settings")
        save_btn.setObjectName("primaryButton")
        save_btn.clicked.connect(self.save_settings)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(save_btn)
        
        layout.addLayout(header_layout)
        
        # General settings
        general_group = QGroupBox("General")
        general_layout = QFormLayout(general_group)
        
        self.auto_refresh = QCheckBox("Auto-refresh data")
        self.auto_refresh.setChecked(True)
        general_layout.addRow("Refresh:", self.auto_refresh)
        
        self.refresh_interval = QSpinBox()
        self.refresh_interval.setRange(10, 300)
        self.refresh_interval.setValue(30)
        self.refresh_interval.setSuffix(" seconds")
        general_layout.addRow("Refresh Interval:", self.refresh_interval)
        
        layout.addWidget(general_group)
        
        # GUI settings
        gui_group = QGroupBox("Interface")
        gui_layout = QFormLayout(gui_group)
        
        self.show_notifications = QCheckBox("Show notifications")
        self.show_notifications.setChecked(True)
        gui_layout.addRow("Notifications:", self.show_notifications)
        
        self.theme_selector = QLineEdit("PyOneDark")
        self.theme_selector.setReadOnly(True)
        gui_layout.addRow("Theme:", self.theme_selector)
        
        layout.addWidget(gui_group)
        
        # Advanced settings
        advanced_group = QGroupBox("Advanced")
        advanced_layout = QFormLayout(advanced_group)
        
        self.debug_mode = QCheckBox("Enable debug logging")
        advanced_layout.addRow("Debug:", self.debug_mode)
        
        self.config_path = QLineEdit()
        self.config_path.setPlaceholderText("Default configuration path")
        advanced_layout.addRow("Config Path:", self.config_path)
        
        layout.addWidget(advanced_group)
        
        layout.addStretch()
        
        self.apply_styling()

    def apply_styling(self) -> None:
        """Apply settings page styling."""
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
        
        QGroupBox {{
            font-weight: bold;
            color: {PyOneDarkColors.TEXT_PRIMARY};
            border: 1px solid {PyOneDarkColors.BORDER};
            border-radius: 8px;
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
        
        QLineEdit, QSpinBox {{
            background-color: {PyOneDarkColors.SURFACE};
            color: {PyOneDarkColors.TEXT_PRIMARY};
            border: 1px solid {PyOneDarkColors.BORDER};
            border-radius: 4px;
            padding: 6px 8px;
        }}
        """
        
        self.setStyleSheet(style)

    def save_settings(self) -> None:
        """Save current settings."""
        # TODO: Implement settings persistence
        self.notification_requested.emit("Settings saved successfully", "success")