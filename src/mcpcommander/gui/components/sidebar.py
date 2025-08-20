"""Sidebar navigation component."""

from typing import Optional, Dict, Any

from PySide6.QtCore import Qt, Signal, QSize, QPoint
from PySide6.QtGui import QFont, QIcon, QPixmap, QPainter, QColor, QBrush, QPolygon
from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QWidget,
    QSpacerItem,
    QSizePolicy,
)

from mcpcommander.gui.theme.pyonedark import PyOneDarkColors


class NavigationButton(QPushButton):
    """Custom navigation button for sidebar."""

    def __init__(self, text: str, icon_name: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.page_name = text.lower().replace(" ", "")
        self.icon_name = icon_name
        self.is_active = False
        
        self.setText(text)
        self.setProperty("sidebar", True)
        self.setFixedHeight(48)
        self.setCursor(Qt.PointingHandCursor)
        
        # Set icon
        self.setIcon(self._create_icon(icon_name))
        self.setIconSize(QSize(20, 20))
        
        self.clicked.connect(lambda: self.parent().page_changed.emit(self.page_name))

    def _create_icon(self, icon_name: str) -> QIcon:
        """Create an icon from icon name."""
        # Icon mapping - in a real implementation, you'd use actual icon files or font icons
        icon_paths = {
            "dashboard": self._create_dashboard_icon(),
            "servers": self._create_servers_icon(),
            "editors": self._create_editors_icon(),
            "backup": self._create_backup_icon(),
            "discovery": self._create_discovery_icon(),
            "status": self._create_status_icon(),
            "settings": self._create_settings_icon(),
        }
        
        pixmap = icon_paths.get(icon_name, self._create_default_icon())
        return QIcon(pixmap)

    def _create_dashboard_icon(self) -> QPixmap:
        """Create dashboard icon."""
        pixmap = QPixmap(20, 20)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(PyOneDarkColors.TEXT_SECONDARY)))
        
        # Draw grid pattern
        painter.drawRect(2, 2, 7, 7)
        painter.drawRect(11, 2, 7, 7)
        painter.drawRect(2, 11, 7, 7)
        painter.drawRect(11, 11, 7, 7)
        
        painter.end()
        return pixmap

    def _create_servers_icon(self) -> QPixmap:
        """Create servers icon."""
        pixmap = QPixmap(20, 20)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(PyOneDarkColors.TEXT_SECONDARY)))
        
        # Draw server rack
        painter.drawRoundedRect(4, 2, 12, 4, 1, 1)
        painter.drawRoundedRect(4, 8, 12, 4, 1, 1)
        painter.drawRoundedRect(4, 14, 12, 4, 1, 1)
        
        painter.end()
        return pixmap

    def _create_editors_icon(self) -> QPixmap:
        """Create editors icon."""
        pixmap = QPixmap(20, 20)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(PyOneDarkColors.TEXT_SECONDARY)))
        
        # Draw editor/code icon
        painter.drawRect(3, 3, 14, 14)
        painter.setBrush(QBrush(QColor(PyOneDarkColors.BACKGROUND)))
        painter.drawRect(4, 4, 12, 12)
        
        # Draw code lines
        painter.setBrush(QBrush(QColor(PyOneDarkColors.TEXT_SECONDARY)))
        painter.drawRect(6, 6, 6, 1)
        painter.drawRect(6, 8, 8, 1)
        painter.drawRect(6, 10, 4, 1)
        
        painter.end()
        return pixmap

    def _create_backup_icon(self) -> QPixmap:
        """Create backup icon."""
        pixmap = QPixmap(20, 20)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(PyOneDarkColors.TEXT_SECONDARY)))
        
        # Draw cloud shape
        painter.drawEllipse(6, 8, 8, 6)
        painter.drawEllipse(4, 6, 6, 6)
        painter.drawEllipse(10, 5, 6, 6)
        
        # Draw arrow
        painter.drawRect(9, 10, 2, 4)
        arrow_points = QPolygon([
            QPoint(7, 12), QPoint(10, 9), QPoint(13, 12)
        ])
        painter.drawPolygon(arrow_points)
        
        painter.end()
        return pixmap

    def _create_discovery_icon(self) -> QPixmap:
        """Create discovery icon."""
        pixmap = QPixmap(20, 20)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(PyOneDarkColors.TEXT_SECONDARY)))
        
        # Draw magnifying glass
        painter.drawEllipse(3, 3, 10, 10)
        painter.setBrush(QBrush(QColor(PyOneDarkColors.BACKGROUND)))
        painter.drawEllipse(5, 5, 6, 6)
        
        # Draw handle
        painter.setBrush(QBrush(QColor(PyOneDarkColors.TEXT_SECONDARY)))
        painter.drawRect(12, 12, 6, 2)
        
        painter.end()
        return pixmap

    def _create_status_icon(self) -> QPixmap:
        """Create status icon."""
        pixmap = QPixmap(20, 20)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(PyOneDarkColors.TEXT_SECONDARY)))
        
        # Draw activity/pulse icon
        painter.drawRect(2, 9, 4, 2)
        painter.drawRect(6, 6, 2, 8)
        painter.drawRect(8, 3, 2, 14)
        painter.drawRect(10, 7, 2, 6)
        painter.drawRect(12, 5, 2, 10)
        painter.drawRect(14, 8, 4, 4)
        
        painter.end()
        return pixmap

    def _create_settings_icon(self) -> QPixmap:
        """Create settings icon."""
        pixmap = QPixmap(20, 20)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(PyOneDarkColors.TEXT_SECONDARY)))
        
        # Draw gear shape
        painter.drawEllipse(6, 6, 8, 8)
        painter.setBrush(QBrush(QColor(PyOneDarkColors.BACKGROUND)))
        painter.drawEllipse(8, 8, 4, 4)
        
        # Draw gear teeth
        painter.setBrush(QBrush(QColor(PyOneDarkColors.TEXT_SECONDARY)))
        for i in range(8):
            angle = i * 45
            painter.save()
            painter.translate(10, 10)
            painter.rotate(angle)
            painter.drawRect(-1, -8, 2, 2)
            painter.restore()
        
        painter.end()
        return pixmap

    def _create_default_icon(self) -> QPixmap:
        """Create default icon."""
        pixmap = QPixmap(20, 20)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(PyOneDarkColors.TEXT_SECONDARY)))
        painter.drawEllipse(6, 6, 8, 8)
        painter.end()
        
        return pixmap

    def set_active(self, active: bool) -> None:
        """Set the active state of the button."""
        self.is_active = active
        self.setProperty("active", active)
        self.style().unpolish(self)
        self.style().polish(self)


class Sidebar(QFrame):
    """Navigation sidebar component."""

    # Signals
    page_changed = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(250)
        
        self.buttons: Dict[str, NavigationButton] = {}
        self.active_page = ""
        
        self.setup_ui()

    def setup_ui(self) -> None:
        """Set up the sidebar UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 16, 8, 16)
        layout.setSpacing(4)

        # Header
        header_layout = QHBoxLayout()
        
        app_icon = QLabel()
        app_icon.setPixmap(self._create_app_logo())
        app_icon.setFixedSize(32, 32)
        
        app_title = QLabel("MCP Commander")
        app_title.setObjectName("appTitle")
        app_title.setStyleSheet(f"""
            QLabel#appTitle {{
                color: {PyOneDarkColors.TEXT_PRIMARY};
                font-size: 16px;
                font-weight: 600;
                margin-left: 8px;
            }}
        """)
        
        header_layout.addWidget(app_icon)
        header_layout.addWidget(app_title)
        header_layout.addStretch()
        
        header_widget = QWidget()
        header_widget.setLayout(header_layout)
        layout.addWidget(header_widget)
        
        # Spacer
        layout.addSpacerItem(QSpacerItem(0, 16, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Navigation buttons
        nav_items = [
            ("Dashboard", "dashboard"),
            ("Servers", "servers"),
            ("Editors", "editors"),
            ("Backup", "backup"),
            ("Discovery", "discovery"),
            ("Status", "status"),
            ("Settings", "settings"),
        ]

        for text, icon_name in nav_items:
            button = NavigationButton(text, icon_name, self)
            self.buttons[button.page_name] = button
            layout.addWidget(button)

        # Stretch to push everything to top
        layout.addStretch()

        # Version info at bottom
        version_label = QLabel("v1.0.0")
        version_label.setStyleSheet(f"""
            QLabel {{
                color: {PyOneDarkColors.TEXT_DISABLED};
                font-size: 11px;
                padding: 8px 16px;
            }}
        """)
        layout.addWidget(version_label)

    def _create_app_logo(self) -> QPixmap:
        """Create application logo."""
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw main circle
        painter.setBrush(QBrush(QColor(PyOneDarkColors.PRIMARY)))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, 32, 32)
        
        # Draw inner design
        painter.setBrush(QBrush(QColor("#ffffff")))
        painter.drawEllipse(6, 6, 20, 20)
        
        # Draw "MCP" letters or abstract design
        painter.setBrush(QBrush(QColor(PyOneDarkColors.PRIMARY)))
        painter.drawRect(10, 10, 3, 12)
        painter.drawRect(14, 10, 3, 12)
        painter.drawRect(19, 10, 3, 12)
        
        painter.drawRect(10, 10, 12, 3)
        painter.drawRect(10, 15, 8, 3)
        
        painter.end()
        return pixmap

    def set_active_page(self, page_name: str) -> None:
        """Set the active page."""
        # Deactivate all buttons
        for button in self.buttons.values():
            button.set_active(False)
        
        # Activate selected button
        if page_name in self.buttons:
            self.buttons[page_name].set_active(True)
            self.active_page = page_name
            # Don't emit here to avoid double emission

    def get_active_page(self) -> str:
        """Get the currently active page."""
        return self.active_page