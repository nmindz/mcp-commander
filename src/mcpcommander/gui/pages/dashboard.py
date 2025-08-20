"""Dashboard page with system overview and statistics."""

from typing import Optional, Dict, Any, List
from datetime import datetime

from PySide6.QtCore import Qt, Signal, QTimer, QThread, QObject
from PySide6.QtGui import QFont, QPixmap, QPainter, QColor, QBrush
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QFrame,
    QPushButton,
    QScrollArea,
    QSpacerItem,
    QSizePolicy,
)

from mcpcommander.core.manager import MCPManager
from mcpcommander.gui.components.progress import CircularProgress
from mcpcommander.gui.theme.pyonedark import PyOneDarkColors
from mcpcommander.utils.logger import get_logger

logger = get_logger(__name__)


class StatCard(QFrame):
    """Individual statistics card widget."""
    
    def __init__(
        self,
        title: str,
        value: str,
        subtitle: str = "",
        color: str = PyOneDarkColors.PRIMARY,
        parent: Optional[QWidget] = None
    ) -> None:
        super().__init__(parent)
        
        self.title = title
        self.value = value
        self.subtitle = subtitle
        self.color = color
        
        self.setup_ui()
        self.apply_styling()

    def setup_ui(self) -> None:
        """Setup the stat card UI."""
        self.setFixedHeight(120)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(8)
        
        # Title
        title_label = QLabel(self.title)
        title_label.setObjectName("statTitle")
        title_label.setFont(QFont("Segoe UI", 10))
        
        # Value
        value_label = QLabel(self.value)
        value_label.setObjectName("statValue")
        value_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        
        # Subtitle
        subtitle_label = QLabel(self.subtitle)
        subtitle_label.setObjectName("statSubtitle")
        subtitle_label.setFont(QFont("Segoe UI", 9))
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        if self.subtitle:
            layout.addWidget(subtitle_label)
        layout.addStretch()

    def apply_styling(self) -> None:
        """Apply card styling."""
        style = f"""
        QFrame {{
            background-color: {PyOneDarkColors.SURFACE};
            border: 1px solid {PyOneDarkColors.BORDER};
            border-radius: 8px;
            border-left: 4px solid {self.color};
        }}
        
        QFrame:hover {{
            background-color: {PyOneDarkColors.SURFACE_VARIANT};
        }}
        
        QLabel#statTitle {{
            color: {PyOneDarkColors.TEXT_SECONDARY};
            font-weight: 500;
        }}
        
        QLabel#statValue {{
            color: {self.color};
            font-weight: bold;
        }}
        
        QLabel#statSubtitle {{
            color: {PyOneDarkColors.TEXT_DISABLED};
        }}
        """
        
        self.setStyleSheet(style)

    def update_value(self, value: str, subtitle: str = "") -> None:
        """Update the card value and subtitle."""
        self.value = value
        if subtitle:
            self.subtitle = subtitle
        
        # Find and update labels
        for child in self.findChildren(QLabel):
            if child.objectName() == "statValue":
                child.setText(value)
            elif child.objectName() == "statSubtitle" and subtitle:
                child.setText(subtitle)


class SystemStatusWidget(QFrame):
    """System status overview widget."""
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        
        self.setup_ui()
        self.apply_styling()

    def setup_ui(self) -> None:
        """Setup the system status UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(16)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("System Status")
        title_label.setObjectName("widgetTitle")
        title_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        
        status_indicator = QLabel("●")
        status_indicator.setObjectName("statusIndicator")
        status_indicator.setFont(QFont("Segoe UI", 16))
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(status_indicator)
        
        layout.addLayout(header_layout)
        
        # Status items
        self.create_status_item(layout, "MCP Commander", "Running", True)
        self.create_status_item(layout, "Configuration", "Valid", True)
        self.create_status_item(layout, "Editors", "3 Detected", True)
        self.create_status_item(layout, "Servers", "5 Active", True)

    def create_status_item(self, parent_layout: QVBoxLayout, label: str, status: str, is_ok: bool) -> None:
        """Create a status item."""
        item_layout = QHBoxLayout()
        
        label_widget = QLabel(label)
        label_widget.setFont(QFont("Segoe UI", 10))
        
        status_widget = QLabel(status)
        status_widget.setObjectName("statusValue")
        status_widget.setFont(QFont("Segoe UI", 10))
        
        indicator = QLabel("●")
        indicator.setFont(QFont("Segoe UI", 12))
        if is_ok:
            indicator.setStyleSheet(f"color: {PyOneDarkColors.SUCCESS};")
        else:
            indicator.setStyleSheet(f"color: {PyOneDarkColors.ERROR};")
        
        item_layout.addWidget(label_widget)
        item_layout.addStretch()
        item_layout.addWidget(status_widget)
        item_layout.addWidget(indicator)
        
        parent_layout.addLayout(item_layout)

    def apply_styling(self) -> None:
        """Apply widget styling."""
        style = f"""
        QFrame {{
            background-color: {PyOneDarkColors.SURFACE};
            border: 1px solid {PyOneDarkColors.BORDER};
            border-radius: 8px;
        }}
        
        QLabel#widgetTitle {{
            color: {PyOneDarkColors.TEXT_PRIMARY};
            font-weight: bold;
        }}
        
        QLabel#statusIndicator {{
            color: {PyOneDarkColors.SUCCESS};
        }}
        
        QLabel#statusValue {{
            color: {PyOneDarkColors.TEXT_SECONDARY};
        }}
        
        QLabel {{
            color: {PyOneDarkColors.TEXT_PRIMARY};
        }}
        """
        
        self.setStyleSheet(style)


class RecentActivityWidget(QFrame):
    """Recent activity and logs widget."""
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        
        self.activity_items = []
        self.setup_ui()
        self.apply_styling()
        self.populate_sample_data()

    def setup_ui(self) -> None:
        """Setup the recent activity UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(16)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Recent Activity")
        title_label.setObjectName("widgetTitle")
        title_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        
        view_all_btn = QPushButton("View All")
        view_all_btn.setObjectName("linkButton")
        view_all_btn.setFlat(True)
        view_all_btn.setCursor(Qt.PointingHandCursor)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(view_all_btn)
        
        layout.addLayout(header_layout)
        
        # Scroll area for activity items
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setMaximumHeight(200)
        
        # Activity container
        self.activity_container = QWidget()
        self.activity_layout = QVBoxLayout(self.activity_container)
        self.activity_layout.setContentsMargins(0, 0, 0, 0)
        self.activity_layout.setSpacing(8)
        
        scroll_area.setWidget(self.activity_container)
        layout.addWidget(scroll_area)

    def add_activity_item(self, message: str, timestamp: datetime, activity_type: str = "info") -> None:
        """Add a new activity item."""
        item_widget = QWidget()
        item_widget.setObjectName("activityItem")
        item_layout = QHBoxLayout(item_widget)
        item_layout.setContentsMargins(8, 8, 8, 8)
        item_layout.setSpacing(12)
        
        # Type indicator
        indicator = QLabel("●")
        indicator.setFont(QFont("Segoe UI", 10))
        
        type_colors = {
            "info": PyOneDarkColors.PRIMARY,
            "success": PyOneDarkColors.SUCCESS,
            "warning": PyOneDarkColors.WARNING,
            "error": PyOneDarkColors.ERROR,
        }
        
        color = type_colors.get(activity_type, PyOneDarkColors.PRIMARY)
        indicator.setStyleSheet(f"color: {color};")
        
        # Message
        message_label = QLabel(message)
        message_label.setFont(QFont("Segoe UI", 9))
        message_label.setWordWrap(True)
        message_label.setStyleSheet(f"color: {PyOneDarkColors.TEXT_PRIMARY}; background: transparent;")
        
        # Timestamp
        time_label = QLabel(timestamp.strftime("%H:%M"))
        time_label.setFont(QFont("Segoe UI", 8))
        time_label.setObjectName("timeLabel")
        time_label.setStyleSheet(f"color: {PyOneDarkColors.TEXT_DISABLED}; background: transparent;")
        
        item_layout.addWidget(indicator)
        item_layout.addWidget(message_label)
        item_layout.addStretch()
        item_layout.addWidget(time_label)
        
        self.activity_layout.insertWidget(0, item_widget)  # Insert at top
        
        # Keep only recent items
        if self.activity_layout.count() > 10:
            old_item = self.activity_layout.takeAt(10)
            if old_item.widget():
                old_item.widget().deleteLater()

    def populate_sample_data(self) -> None:
        """Populate with sample activity data."""
        import random
        from datetime import timedelta
        
        activities = [
            ("Server 'filesystem' added to Claude Code", "success"),
            ("Configuration backup created", "info"),
            ("Editor discovery completed", "info"),
            ("Server 'sqlite' removed from Cursor", "warning"),
            ("System status check completed", "success"),
        ]
        
        base_time = datetime.now()
        for i, (message, activity_type) in enumerate(activities):
            timestamp = base_time - timedelta(minutes=i * 15)
            self.add_activity_item(message, timestamp, activity_type)

    def apply_styling(self) -> None:
        """Apply widget styling."""
        style = f"""
        QFrame {{
            background-color: {PyOneDarkColors.SURFACE};
            border: 1px solid {PyOneDarkColors.BORDER};
            border-radius: 8px;
        }}
        
        QLabel#widgetTitle {{
            color: {PyOneDarkColors.TEXT_PRIMARY};
            font-weight: bold;
        }}
        
        QPushButton#linkButton {{
            color: {PyOneDarkColors.PRIMARY};
            text-decoration: none;
            font-weight: 500;
            padding: 4px 8px;
            border: none;
            background: transparent;
        }}
        
        QPushButton#linkButton:hover {{
            color: {PyOneDarkColors.ACCENT_BLUE};
            text-decoration: underline;
        }}
        
        QLabel#timeLabel {{
            color: {PyOneDarkColors.TEXT_DISABLED};
        }}
        
        QLabel {{
            color: {PyOneDarkColors.TEXT_PRIMARY};
        }}
        
        QWidget#activityItem {{
            background-color: transparent;
            border-bottom: 1px solid {PyOneDarkColors.SEPARATOR};
        }}
        
        QWidget#activityItem:hover {{
            background-color: {PyOneDarkColors.HOVER};
        }}
        
        QScrollArea {{
            border: none;
            background: transparent;
        }}
        """
        
        self.setStyleSheet(style)


class DashboardWorker(QObject):
    """Worker for loading dashboard data asynchronously."""
    
    # Signals
    data_loaded = Signal(dict)
    error_occurred = Signal(str)
    
    def __init__(self, manager: MCPManager) -> None:
        super().__init__()
        self.manager = manager

    def load_dashboard_data(self) -> None:
        """Load dashboard data from manager."""
        try:
            # Get system statistics
            data = {
                "total_servers": self._count_total_servers(),
                "active_editors": self._count_active_editors(),
                "recent_backups": self._count_recent_backups(),
                "system_status": self._get_system_status(),
                "editor_stats": self._get_editor_stats(),
            }
            
            self.data_loaded.emit(data)
            
        except Exception as e:
            logger.error(f"Failed to load dashboard data: {e}")
            self.error_occurred.emit(str(e))

    def _count_total_servers(self) -> int:
        """Count total configured servers across all editors."""
        try:
            servers = self.manager.list_servers()
            total = 0
            for editor_servers in servers.values():
                total += len(editor_servers)
            return total
        except Exception:
            return 0

    def _count_active_editors(self) -> int:
        """Count editors with valid configurations."""
        try:
            status = self.manager.status()
            active = 0
            for editor_status in status.values():
                if editor_status.get("exists", False):
                    active += 1
            return active
        except Exception:
            return 0

    def _count_recent_backups(self) -> int:
        """Count recent backups (placeholder)."""
        # TODO: Implement backup counting when backup system is ready
        return 3

    def _get_system_status(self) -> str:
        """Get overall system status."""
        try:
            status = self.manager.status()
            if all(s.get("exists", False) for s in status.values()):
                return "All Systems Operational"
            else:
                return "Some Issues Detected"
        except Exception:
            return "Status Unknown"

    def _get_editor_stats(self) -> Dict[str, int]:
        """Get per-editor statistics."""
        try:
            servers = self.manager.list_servers()
            return {editor: len(editor_servers) for editor, editor_servers in servers.items()}
        except Exception:
            return {}


class DashboardPage(QWidget):
    """Main dashboard page widget."""
    
    # Signals
    notification_requested = Signal(str, str)  # message, type
    
    def __init__(self, manager: MCPManager, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        
        self.manager = manager
        self.stat_cards: Dict[str, StatCard] = {}
        
        # Worker thread for async operations
        self.worker_thread = QThread()
        self.worker = DashboardWorker(manager)
        self.worker.moveToThread(self.worker_thread)
        
        # Connect worker signals
        self.worker.data_loaded.connect(self.update_dashboard)
        self.worker.error_occurred.connect(self.handle_error)
        self.worker_thread.started.connect(self.worker.load_dashboard_data)
        
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
        
        self.setup_ui()
        self.load_initial_data()

    def setup_ui(self) -> None:
        """Setup the dashboard UI."""
        # Main scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Main container
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(24)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Dashboard")
        title_label.setObjectName("pageTitle")
        title_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setObjectName("primaryButton")
        refresh_btn.clicked.connect(self.refresh)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Statistics cards
        stats_layout = QGridLayout()
        stats_layout.setSpacing(16)
        
        # Create stat cards
        self.stat_cards["servers"] = StatCard(
            "Total Servers", "0", "Across all editors", PyOneDarkColors.PRIMARY
        )
        self.stat_cards["editors"] = StatCard(
            "Active Editors", "0", "Configured and ready", PyOneDarkColors.SUCCESS
        )
        self.stat_cards["backups"] = StatCard(
            "Recent Backups", "0", "Last 7 days", PyOneDarkColors.WARNING
        )
        self.stat_cards["status"] = StatCard(
            "System Health", "Good", "All systems operational", PyOneDarkColors.ACCENT_GREEN
        )
        
        # Add cards to grid
        stats_layout.addWidget(self.stat_cards["servers"], 0, 0)
        stats_layout.addWidget(self.stat_cards["editors"], 0, 1)
        stats_layout.addWidget(self.stat_cards["backups"], 0, 2)
        stats_layout.addWidget(self.stat_cards["status"], 0, 3)
        
        layout.addLayout(stats_layout)
        
        # Content row
        content_layout = QHBoxLayout()
        content_layout.setSpacing(16)
        
        # Left column
        left_column = QVBoxLayout()
        left_column.setSpacing(16)
        
        # System status widget
        self.system_status = SystemStatusWidget()
        left_column.addWidget(self.system_status)
        
        # Quick actions
        actions_frame = QFrame()
        actions_frame.setObjectName("actionsFrame")
        actions_layout = QVBoxLayout(actions_frame)
        actions_layout.setContentsMargins(20, 16, 20, 16)
        actions_layout.setSpacing(12)
        
        actions_title = QLabel("Quick Actions")
        actions_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        actions_layout.addWidget(actions_title)
        
        # Action buttons  
        def navigate_to_servers():
            # Navigate up the widget hierarchy to find the main window
            main_window = self
            while main_window and not hasattr(main_window, 'change_page'):
                main_window = main_window.parent()
            
            if main_window and hasattr(main_window, 'change_page'):
                main_window.change_page("servers")
            else:
                self.notification_requested.emit("Navigate to Servers page to add new server", "info")
        
        def navigate_to_discovery():
            main_window = self
            while main_window and not hasattr(main_window, 'change_page'):
                main_window = main_window.parent()
            
            if main_window and hasattr(main_window, 'change_page'):
                main_window.change_page("discovery")
            else:
                self.notification_requested.emit("Navigate to Discovery page to scan for servers", "info")
        
        def navigate_to_backup():
            main_window = self
            while main_window and not hasattr(main_window, 'change_page'):
                main_window = main_window.parent()
            
            if main_window and hasattr(main_window, 'change_page'):
                main_window.change_page("backup")
            else:
                self.notification_requested.emit("Navigate to Backup page to create backup", "info")
        
        for text, icon, action in [
            ("Add New Server", "＋", navigate_to_servers),
            ("Run Discovery", "🔍", navigate_to_discovery),
            ("Create Backup", "💾", navigate_to_backup),
            ("View Logs", "📄", lambda: self.notification_requested.emit("Log viewer not yet implemented", "info")),
        ]:
            btn = QPushButton(f"{icon} {text}")
            btn.setObjectName("actionButton")
            btn.clicked.connect(action)
            actions_layout.addWidget(btn)
        
        left_column.addWidget(actions_frame)
        left_column.addStretch()
        
        # Right column - Recent activity
        right_column = QVBoxLayout()
        self.recent_activity = RecentActivityWidget()
        right_column.addWidget(self.recent_activity)
        right_column.addStretch()
        
        content_layout.addLayout(left_column, 1)
        content_layout.addLayout(right_column, 1)
        
        layout.addLayout(content_layout)
        
        # Set container in scroll area
        scroll_area.setWidget(container)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)
        
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
        
        QFrame#actionsFrame {{
            background-color: {PyOneDarkColors.SURFACE};
            border: 1px solid {PyOneDarkColors.BORDER};
            border-radius: 8px;
        }}
        
        QPushButton#actionButton {{
            background-color: transparent;
            color: {PyOneDarkColors.TEXT_PRIMARY};
            text-align: left;
            padding: 12px 16px;
            border: 1px solid {PyOneDarkColors.BORDER};
            border-radius: 6px;
            font-size: 13px;
        }}
        
        QPushButton#actionButton:hover {{
            background-color: {PyOneDarkColors.HOVER};
            border-color: {PyOneDarkColors.PRIMARY};
        }}
        
        QScrollArea {{
            border: none;
            background: transparent;
        }}
        """
        
        self.setStyleSheet(style)

    def load_initial_data(self) -> None:
        """Load initial dashboard data."""
        if not self.worker_thread.isRunning():
            self.worker_thread.start()

    def refresh(self) -> None:
        """Refresh dashboard data."""
        logger.info("Refreshing dashboard data")
        
        # Restart worker thread if needed
        if not self.worker_thread.isRunning():
            self.worker_thread.start()
        else:
            # Emit signal to load data
            self.worker.load_dashboard_data()

    def update_dashboard(self, data: Dict[str, Any]) -> None:
        """Update dashboard with new data."""
        try:
            # Update stat cards
            self.stat_cards["servers"].update_value(str(data.get("total_servers", 0)))
            self.stat_cards["editors"].update_value(str(data.get("active_editors", 0)))
            self.stat_cards["backups"].update_value(str(data.get("recent_backups", 0)))
            
            # Update system status
            status_text = data.get("system_status", "Unknown")
            self.stat_cards["status"].update_value("Good" if "Operational" in status_text else "Issues")
            
            logger.debug("Dashboard updated successfully")
            
        except Exception as e:
            logger.error(f"Failed to update dashboard: {e}")
            self.handle_error(str(e))

    def handle_error(self, error_message: str) -> None:
        """Handle worker errors."""
        logger.error(f"Dashboard error: {error_message}")
        self.notification_requested.emit(f"Dashboard error: {error_message}", "error")

    def closeEvent(self, event) -> None:
        """Clean up on close."""
        self.refresh_timer.stop()
        self.worker_thread.quit()
        self.worker_thread.wait()
        event.accept()