"""Main GUI application window for MCP Commander."""

import sys
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QSize, Signal, QPoint, QRect, QEvent
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QCursor, QPen
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QFrame,
    QPushButton,
    QLabel,
    QStackedWidget,
)

from mcpcommander.core.manager import MCPManager
from mcpcommander.gui.components.sidebar import Sidebar
from mcpcommander.gui.components.notification import NotificationManager
from mcpcommander.gui.theme.pyonedark import PyOneDarkTheme
from mcpcommander.gui.pages import (
    DashboardPage,
    ServersPage,
    EditorsPage,
    BackupPage,
    DiscoveryPage,
    StatusPage,
    SettingsPage,
)
from mcpcommander.utils.logger import get_logger

logger = get_logger(__name__)


class TitleBar(QFrame):
    """Custom title bar for frameless window."""

    # Signals
    close_clicked = Signal()
    minimize_clicked = Signal()
    maximize_clicked = Signal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setFixedHeight(40)
        self.setObjectName("titleBar")
        self.setup_ui()
        self.drag_position = QPoint()
        self.resize_margin = 10  # Match main window's resize margin

    def setup_ui(self) -> None:
        """Set up the title bar UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 8, 0)
        layout.setSpacing(8)

        # App icon and title
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(24, 24)
        self.icon_label.setPixmap(self._create_app_icon())

        self.title_label = QLabel("MCP Commander")
        self.title_label.setObjectName("titleLabel")
        
        layout.addWidget(self.icon_label)
        layout.addWidget(self.title_label)
        layout.addStretch()

        # Window controls
        self.minimize_btn = QPushButton()
        self.maximize_btn = QPushButton()
        self.close_btn = QPushButton()

        # Set icons for window controls
        self.minimize_btn.setIcon(QIcon(self._create_minimize_icon()))
        self.maximize_btn.setIcon(QIcon(self._create_maximize_icon()))
        self.close_btn.setIcon(QIcon(self._create_close_icon()))

        for btn in [self.minimize_btn, self.maximize_btn, self.close_btn]:
            btn.setFixedSize(32, 32)
            btn.setObjectName("windowControl")
            btn.setIconSize(QSize(16, 16))
            btn.setFlat(True)

        self.close_btn.setProperty("close", True)

        # Connect signals
        self.minimize_btn.clicked.connect(self.minimize_clicked.emit)
        self.maximize_btn.clicked.connect(self.maximize_clicked.emit)
        self.close_btn.clicked.connect(self.close_clicked.emit)

        layout.addWidget(self.minimize_btn)
        layout.addWidget(self.maximize_btn)
        layout.addWidget(self.close_btn)

    def _create_app_icon(self) -> QPixmap:
        """Create a simple app icon."""
        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw simple icon
        painter.setBrush(QColor("#61afef"))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(2, 2, 20, 20, 4, 4)
        
        painter.setBrush(QColor("#ffffff"))
        painter.drawRoundedRect(6, 6, 12, 12, 2, 2)
        
        painter.end()
        return pixmap

    def _create_minimize_icon(self) -> QPixmap:
        """Create minimize button icon."""
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(QColor("#abb2bf"), 2))
        
        # Draw minimize line
        painter.drawLine(4, 8, 12, 8)
        
        painter.end()
        return pixmap

    def _create_maximize_icon(self) -> QPixmap:
        """Create maximize/restore button icon."""
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(QColor("#abb2bf"), 2))
        painter.setBrush(Qt.NoBrush)
        
        # Draw maximize square
        painter.drawRect(3, 3, 10, 10)
        
        painter.end()
        return pixmap

    def _create_close_icon(self) -> QPixmap:
        """Create close button icon."""
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(QColor("#abb2bf"), 2))
        
        # Draw X
        painter.drawLine(4, 4, 12, 12)
        painter.drawLine(12, 4, 4, 12)
        
        painter.end()
        return pixmap

    def update_maximize_icon(self, is_maximized: bool) -> None:
        """Update maximize button icon based on window state."""
        if is_maximized:
            # Create restore icon (two overlapping squares)
            pixmap = QPixmap(16, 16)
            pixmap.fill(Qt.transparent)
            
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setPen(QPen(QColor("#abb2bf"), 2))
            painter.setBrush(Qt.NoBrush)
            
            # Draw overlapping restore squares
            painter.drawRect(2, 5, 7, 7)
            painter.drawRect(7, 2, 7, 7)
            
            painter.end()
            self.maximize_btn.setIcon(QIcon(pixmap))
        else:
            self.maximize_btn.setIcon(QIcon(self._create_maximize_icon()))

    def _is_in_resize_area(self, pos: QPoint) -> bool:
        """Check if position is in a resize area."""
        return (pos.x() <= self.resize_margin or 
                pos.x() >= self.width() - self.resize_margin or 
                pos.y() <= self.resize_margin)

    def mousePressEvent(self, event) -> None:
        """Handle mouse press for window dragging."""
        if event.button() == Qt.LeftButton:
            pos = event.position().toPoint()
            
            # Completely ignore events in resize areas
            if self._is_in_resize_area(pos):
                event.ignore()
                return
            
            # Only start dragging if window is not maximized
            if not self.window().isMaximized():
                self.drag_position = event.globalPosition().toPoint() - self.window().frameGeometry().topLeft()
                event.accept()
            else:
                event.ignore()

    def mouseMoveEvent(self, event) -> None:
        """Handle mouse move for window dragging."""
        pos = event.position().toPoint()
        
        # Always ignore events in resize areas
        if self._is_in_resize_area(pos):
            event.ignore()
            return
            
        if event.buttons() == Qt.LeftButton and not self.drag_position.isNull():
            # If window was maximized and user drags, restore it first
            if self.window().isMaximized():
                # Calculate new position to center the window under the cursor
                normal_size = QSize(1200, 800)  # Default restored size
                cursor_pos = event.globalPosition().toPoint()
                new_pos = QPoint(
                    cursor_pos.x() - normal_size.width() // 2,
                    cursor_pos.y() - 20  # Offset for title bar
                )
                
                self.window().showNormal()
                self.window().resize(normal_size)
                self.window().move(new_pos)
                self.drag_position = QPoint(normal_size.width() // 2, 20)
            else:
                self.window().move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
        else:
            # Let event pass through for cursor updates
            event.ignore()

    def mouseDoubleClickEvent(self, event) -> None:
        """Handle double-click to maximize/restore (Windows standard behavior)."""
        if event.button() == Qt.LeftButton:
            pos = event.position().toPoint()
            
            # Don't handle double-click if in resize area
            if self._is_in_resize_area(pos):
                event.ignore()
                return
                
            self.maximize_clicked.emit()
            event.accept()


class MCPCommanderGUI(QMainWindow):
    """Main application window for MCP Commander GUI."""

    def __init__(self, config_path: Optional[Path] = None, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        
        # Initialize backend
        self.manager = MCPManager(config_path)
        
        # Window configuration
        self.setWindowTitle("MCP Commander")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
        
        # Remove window frame for custom title bar
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        # Enable resize functionality  
        self.resize_margin = 10  # Resize margin in pixels (increased for easier detection)
        self.resize_direction = None
        self.resize_start_pos = QPoint()
        self.resize_start_geometry = QRect()
        
        # Enable mouse tracking to detect cursor position without clicking
        self.setMouseTracking(True)
        
        # Apply theme
        self.setStyleSheet(self._get_extended_stylesheet())
        
        # Initialize components
        self.notification_manager = NotificationManager(self)
        
        # Setup UI
        self.setup_ui()
        
        # Install global event filter on application to catch all mouse moves
        app = QApplication.instance()
        if app:
            app.installEventFilter(self)
        
        logger.info("MCP Commander GUI initialized")

    def setup_ui(self) -> None:
        """Set up the main user interface."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Title bar
        self.title_bar = TitleBar(self)
        self.title_bar.close_clicked.connect(self.close)
        self.title_bar.minimize_clicked.connect(self.showMinimized)
        self.title_bar.maximize_clicked.connect(self.toggle_maximize)
        main_layout.addWidget(self.title_bar)
        
        # Content area
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = Sidebar(self)
        self.sidebar.page_changed.connect(self.change_page)
        content_layout.addWidget(self.sidebar)
        
        # Main content area
        self.content_frame = QFrame()
        self.content_frame.setObjectName("contentFrame")
        content_layout.addWidget(self.content_frame)
        
        # Stack widget for pages
        self.stack = QStackedWidget(self.content_frame)
        
        content_frame_layout = QVBoxLayout(self.content_frame)
        content_frame_layout.setContentsMargins(0, 0, 0, 0)
        content_frame_layout.addWidget(self.stack)
        
        # Add content layout to main
        content_widget = QWidget()
        content_widget.setLayout(content_layout)
        main_layout.addWidget(content_widget)
        
        # Initialize pages
        self.setup_pages()
        
        # Set initial page
        self.sidebar.set_active_page("dashboard")
        
        # Ensure mouse tracking propagates through all child widgets
        self._setup_mouse_tracking()

    def setup_pages(self) -> None:
        """Initialize and add all pages to the stack."""
        self.pages = {
            "dashboard": DashboardPage(self.manager, self),
            "servers": ServersPage(self.manager, self),
            "editors": EditorsPage(self.manager, self),
            "backup": BackupPage(self.manager, self),
            "discovery": DiscoveryPage(self.manager, self),
            "status": StatusPage(self.manager, self),
            "settings": SettingsPage(self.manager, self),
        }
        
        # Add pages to stack
        for page_name, page_widget in self.pages.items():
            self.stack.addWidget(page_widget)
            
            # Connect page signals if they have them
            if hasattr(page_widget, 'notification_requested'):
                page_widget.notification_requested.connect(
                    self.notification_manager.show_notification
                )

    def change_page(self, page_name: str) -> None:
        """Change the active page."""
        if page_name in self.pages:
            page_widget = self.pages[page_name]
            self.stack.setCurrentWidget(page_widget)
            
            # Update sidebar active state
            self.sidebar.set_active_page(page_name)
            
            # Refresh page data if method exists
            if hasattr(page_widget, 'refresh'):
                page_widget.refresh()
                
            logger.debug(f"Changed to page: {page_name}")

    def _setup_mouse_tracking(self) -> None:
        """Setup mouse tracking for main window and key child widgets."""
        # Enable mouse tracking for main window
        self.setMouseTracking(True)
        
        # Enable mouse tracking for central widget to ensure events propagate
        central = self.centralWidget()
        if central:
            central.setMouseTracking(True)
            
        # Enable for content frame
        if hasattr(self, 'content_frame'):
            self.content_frame.setMouseTracking(True)

    def toggle_maximize(self) -> None:
        """Toggle between maximized and normal window state."""
        if self.isMaximized():
            self.showNormal()
            self.title_bar.update_maximize_icon(False)
        else:
            self.showMaximized()
            self.title_bar.update_maximize_icon(True)

    def _get_resize_direction(self, pos: QPoint) -> Optional[str]:
        """Determine resize direction based on mouse position."""
        rect = self.rect()
        margin = self.resize_margin
        
        # Ensure position is within window bounds
        if not rect.contains(pos):
            return None
        
        # Check corners first (have priority)
        if pos.x() <= margin and pos.y() <= margin:
            return "top_left"
        elif pos.x() >= rect.width() - margin and pos.y() <= margin:
            return "top_right"
        elif pos.x() <= margin and pos.y() >= rect.height() - margin:
            return "bottom_left"
        elif pos.x() >= rect.width() - margin and pos.y() >= rect.height() - margin:
            return "bottom_right"
        
        # Check edges
        elif pos.x() <= margin:
            return "left"
        elif pos.x() >= rect.width() - margin:
            return "right"
        elif pos.y() <= margin:
            return "top"
        elif pos.y() >= rect.height() - margin:
            return "bottom"
        
        return None

    def _set_cursor_for_resize(self, direction: Optional[str]) -> None:
        """Set appropriate cursor for resize direction."""
        # Clear any existing override first
        app = QApplication.instance()
        if app:
            app.restoreOverrideCursor()
            
        if direction == "top_left" or direction == "bottom_right":
            cursor = Qt.SizeFDiagCursor
        elif direction == "top_right" or direction == "bottom_left":
            cursor = Qt.SizeBDiagCursor
        elif direction == "left" or direction == "right":
            cursor = Qt.SizeHorCursor
        elif direction == "top" or direction == "bottom":
            cursor = Qt.SizeVerCursor
        else:
            cursor = Qt.ArrowCursor
            
        # Only use application override for resize cursors, not arrow cursor
        if direction and cursor != Qt.ArrowCursor:
            if app:
                app.setOverrideCursor(QCursor(cursor))
        else:
            self.setCursor(QCursor(cursor))

    def mousePressEvent(self, event) -> None:
        """Handle mouse press for resizing."""
        if event.button() == Qt.LeftButton:
            pos = event.position().toPoint()
            self.resize_direction = self._get_resize_direction(pos)
            
            if self.resize_direction:
                # Clear any cursor overrides and start resize
                app = QApplication.instance()
                if app:
                    app.restoreOverrideCursor()
                
                self.resize_start_pos = event.globalPosition().toPoint()
                self.resize_start_geometry = self.geometry()
                self.grabMouse()  # Ensure we capture all mouse events during resize
                event.accept()
                return
        
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        """Handle mouse move for resizing and cursor updates."""
        if event.buttons() == Qt.LeftButton and self.resize_direction:
            # Perform resize
            current_pos = event.globalPosition().toPoint()
            diff = current_pos - self.resize_start_pos
            
            new_geometry = QRect(self.resize_start_geometry)
            
            # Calculate new geometry based on resize direction
            if "left" in self.resize_direction:
                new_geometry.setLeft(new_geometry.left() + diff.x())
            if "right" in self.resize_direction:
                new_geometry.setRight(new_geometry.right() + diff.x())
            if "top" in self.resize_direction:
                new_geometry.setTop(new_geometry.top() + diff.y())
            if "bottom" in self.resize_direction:
                new_geometry.setBottom(new_geometry.bottom() + diff.y())
            
            # Apply minimum size constraints
            min_size = self.minimumSize()
            if new_geometry.width() < min_size.width():
                if "left" in self.resize_direction:
                    new_geometry.setLeft(new_geometry.right() - min_size.width())
                else:
                    new_geometry.setWidth(min_size.width())
            
            if new_geometry.height() < min_size.height():
                if "top" in self.resize_direction:
                    new_geometry.setTop(new_geometry.bottom() - min_size.height())
                else:
                    new_geometry.setHeight(min_size.height())
            
            self.setGeometry(new_geometry)
            event.accept()
        else:
            # Always update cursor based on position when not resizing
            if not self.isMaximized():
                pos = event.position().toPoint()
                direction = self._get_resize_direction(pos)
                self._set_cursor_for_resize(direction)
            else:
                self.setCursor(QCursor(Qt.ArrowCursor))
        
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        """Handle mouse release to end resizing."""
        if event.button() == Qt.LeftButton and self.resize_direction:
            self.resize_direction = None
            self.releaseMouse()  # Release mouse grab
            
            # Clear any cursor overrides
            app = QApplication.instance()
            if app:
                app.restoreOverrideCursor()
        
        super().mouseReleaseEvent(event)

    def enterEvent(self, event) -> None:
        """Handle mouse entering the widget."""
        if not self.isMaximized():
            # Re-enable mouse tracking when entering
            self.setMouseTracking(True)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        """Handle mouse leaving the widget."""
        # Clear any application cursor override and reset to arrow
        app = QApplication.instance()
        if app:
            app.restoreOverrideCursor()
        self.setCursor(QCursor(Qt.ArrowCursor))
        super().leaveEvent(event)

    def eventFilter(self, obj, event) -> bool:
        """Filter events to catch mouse moves anywhere in the application."""
        if event.type() == QEvent.Type.MouseMove:
            # Check if mouse is over this window
            if self.underMouse() and not self.isMaximized():
                # Get mouse position relative to this window
                global_pos = event.globalPosition().toPoint()
                local_pos = self.mapFromGlobal(global_pos)
                
                # Check if position is within our window bounds
                if self.rect().contains(local_pos):
                    direction = self._get_resize_direction(local_pos)
                    self._set_cursor_for_resize(direction)
            elif self.underMouse():
                # If maximized, ensure cursor is arrow
                self.setCursor(QCursor(Qt.ArrowCursor))
                
        return False  # Always allow event to continue processing

    def _get_extended_stylesheet(self) -> str:
        """Get extended stylesheet with custom components."""
        base_style = PyOneDarkTheme.get_stylesheet()
        
        custom_style = """
        /* Custom title bar styles */
        QFrame#titleBar {
            background-color: #3c4043;
            border-bottom: 1px solid #2c323c;
        }
        
        QLabel#titleLabel {
            color: #abb2bf;
            font-size: 14px;
            font-weight: 600;
        }
        
        QPushButton#windowControl {
            background-color: #484c54;
            color: #abb2bf;
            border: none;
            border-radius: 4px;
            font-size: 14px;
            font-weight: bold;
        }
        
        QPushButton#windowControl:hover {
            background-color: #5c6370;
            color: #ffffff;
        }
        
        QPushButton#windowControl[close="true"]:hover {
            background-color: #e06c75;
            color: #ffffff;
        }
        
        /* Content frame */
        QFrame#contentFrame {
            background-color: #282c34;
            border: none;
        }
        """
        
        return base_style + custom_style

    def show_notification(self, message: str, notification_type: str = "info", duration: int = 3000) -> None:
        """Show a notification message."""
        self.notification_manager.show_notification(message, notification_type, duration)

    def changeEvent(self, event) -> None:
        """Handle window state changes."""
        if event.type() == event.Type.WindowStateChange:
            # Update maximize button icon based on window state
            self.title_bar.update_maximize_icon(self.isMaximized())
        super().changeEvent(event)

    def closeEvent(self, event) -> None:
        """Handle close event."""
        logger.info("Closing MCP Commander GUI")
        event.accept()


def run_gui(config_path: Optional[Path] = None) -> int:
    """Run the GUI application."""
    app = QApplication(sys.argv)
    app.setApplicationName("MCP Commander")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("MCP Commander")
    
    # Create and show main window
    window = MCPCommanderGUI(config_path)
    window.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(run_gui())