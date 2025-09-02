"""Notification system for the GUI."""

from typing import Optional
from enum import Enum

from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint, Signal, QRect, QEvent
from PySide6.QtGui import QColor, QPainter, QBrush, QPen, QFont
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QPushButton

from mcpcommander.gui.theme.pyonedark import PyOneDarkColors


class NotificationType(Enum):
    """Notification types with associated colors."""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class NotificationWidget(QWidget):
    """Individual notification widget."""
    
    # Signals
    close_requested = Signal()
    
    def __init__(
        self,
        message: str,
        notification_type: NotificationType = NotificationType.INFO,
        parent: Optional[QWidget] = None
    ) -> None:
        super().__init__(parent)
        
        self.notification_type = notification_type
        self.message = message
        
        # Setup UI
        self.setFixedHeight(80)
        self.setMinimumWidth(300)
        self.setMaximumWidth(500)
        
        # Set object name for styling
        self.setObjectName("notificationWidget")
        
        self.setup_ui()
        self.apply_styling()

    def setup_ui(self) -> None:
        """Setup the notification UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        # Content layout
        content_layout = QVBoxLayout()
        content_layout.setSpacing(4)

        # Title based on type
        title_text = {
            NotificationType.INFO: "Information",
            NotificationType.SUCCESS: "Success",
            NotificationType.WARNING: "Warning",
            NotificationType.ERROR: "Error",
        }.get(self.notification_type, "Notification")

        self.title_label = QLabel(title_text)
        self.title_label.setObjectName("notificationTitle")
        self.title_label.setFont(QFont("Segoe UI", 10, QFont.Bold))

        # Message label
        self.message_label = QLabel(self.message)
        self.message_label.setObjectName("notificationMessage")
        self.message_label.setWordWrap(True)
        self.message_label.setFont(QFont("Segoe UI", 9))

        content_layout.addWidget(self.title_label)
        content_layout.addWidget(self.message_label)
        content_layout.addStretch()

        layout.addLayout(content_layout)
        layout.addStretch()

        # Close button
        self.close_button = QPushButton("×")
        self.close_button.setObjectName("notificationClose")
        self.close_button.setFixedSize(20, 20)
        self.close_button.clicked.connect(self.close_requested.emit)
        
        layout.addWidget(self.close_button)

    def apply_styling(self) -> None:
        """Apply styling based on notification type."""
        # Color mapping
        colors = {
            NotificationType.INFO: PyOneDarkColors.PRIMARY,
            NotificationType.SUCCESS: PyOneDarkColors.SUCCESS,
            NotificationType.WARNING: PyOneDarkColors.WARNING,
            NotificationType.ERROR: PyOneDarkColors.ERROR,
        }
        
        accent_color = colors.get(self.notification_type, PyOneDarkColors.PRIMARY)
        
        style = f"""
        QWidget#notificationWidget {{
            background-color: {PyOneDarkColors.SURFACE};
            border: 1px solid {PyOneDarkColors.BORDER};
            border-left: 4px solid {accent_color};
            border-radius: 6px;
        }}
        
        QLabel#notificationTitle {{
            color: {accent_color};
            font-weight: bold;
        }}
        
        QLabel#notificationMessage {{
            color: {PyOneDarkColors.TEXT_PRIMARY};
        }}
        
        QPushButton#notificationClose {{
            background-color: transparent;
            color: {PyOneDarkColors.TEXT_SECONDARY};
            border: none;
            border-radius: 10px;
            font-size: 14px;
            font-weight: bold;
        }}
        
        QPushButton#notificationClose:hover {{
            background-color: {PyOneDarkColors.ERROR};
            color: white;
        }}
        """
        
        self.setStyleSheet(style)

    def paintEvent(self, event) -> None:
        """Custom paint event for rounded corners (removed problematic shadow)."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Get colors
        colors = {
            NotificationType.INFO: PyOneDarkColors.PRIMARY,
            NotificationType.SUCCESS: PyOneDarkColors.SUCCESS,
            NotificationType.WARNING: PyOneDarkColors.WARNING,
            NotificationType.ERROR: PyOneDarkColors.ERROR,
        }
        
        accent_color = colors.get(self.notification_type, PyOneDarkColors.PRIMARY)
        
        # Draw main background with border
        rect = self.rect()
        painter.setBrush(QBrush(QColor(PyOneDarkColors.SURFACE)))
        painter.setPen(QPen(QColor(PyOneDarkColors.BORDER), 1))
        painter.drawRoundedRect(rect, 6, 6)
        
        # Draw accent border (left edge)
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QColor(accent_color), 4))
        painter.drawLine(2, 6, 2, self.height() - 6)
        
        painter.end()


class NotificationManager(QWidget):
    """Manages and displays notifications."""
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        
        # Setup container as a proper child widget
        self.setParent(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        
        # Make it always on top of parent but not a separate window
        self.raise_()
        
        # Notification tracking
        self.notifications: list[NotificationWidget] = []
        self.max_notifications = 5
        self.notification_spacing = 10
        
        # Setup layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(self.notification_spacing)
        self.layout.addStretch()
        
        # Set background to transparent
        self.setStyleSheet("NotificationManager { background-color: transparent; }")
        
        # Position and show
        self.update_position()
        self.show()
        
        # Connect to parent resize events if parent exists
        if parent:
            parent.installEventFilter(self)

    def show_notification(
        self,
        message: str,
        notification_type: str = "info",
        duration: int = 5000
    ) -> None:
        """Show a new notification."""
        # Convert string type to enum
        type_map = {
            "info": NotificationType.INFO,
            "success": NotificationType.SUCCESS,
            "warning": NotificationType.WARNING,
            "error": NotificationType.ERROR,
        }
        
        notif_type = type_map.get(notification_type.lower(), NotificationType.INFO)
        
        # Create notification widget
        notification = NotificationWidget(message, notif_type, self)
        notification.close_requested.connect(lambda: self.remove_notification(notification))
        
        # Add to layout
        self.layout.insertWidget(self.layout.count() - 1, notification)
        self.notifications.append(notification)
        
        # Remove oldest if too many
        if len(self.notifications) > self.max_notifications:
            oldest = self.notifications.pop(0)
            self.remove_notification(oldest)
        
        # Auto-hide timer
        if duration > 0:
            timer = QTimer(self)
            timer.setSingleShot(True)
            timer.timeout.connect(lambda: self.remove_notification(notification))
            timer.start(duration)
            
            # Store timer reference to prevent garbage collection
            notification.timer = timer
        
        # Animate in
        self.animate_in(notification)
        
        # Update position
        self.update_position()

    def remove_notification(self, notification: NotificationWidget) -> None:
        """Remove a notification with animation."""
        if notification in self.notifications:
            self.notifications.remove(notification)
            self.animate_out(notification)

    def animate_in(self, notification: NotificationWidget) -> None:
        """Animate notification appearance."""
        # Start from right side (off-screen)
        start_pos = QPoint(self.width() + 100, notification.y())
        end_pos = QPoint(0, notification.y())
        
        # Setup animation
        animation = QPropertyAnimation(notification, b"pos")
        animation.setDuration(300)
        animation.setStartValue(start_pos)
        animation.setEndValue(end_pos)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # Store animation reference
        notification.in_animation = animation
        animation.start()

    def animate_out(self, notification: NotificationWidget) -> None:
        """Animate notification removal."""
        # Animate to right side (off-screen)
        start_pos = notification.pos()
        end_pos = QPoint(self.width() + 100, notification.y())
        
        # Setup animation
        animation = QPropertyAnimation(notification, b"pos")
        animation.setDuration(250)
        animation.setStartValue(start_pos)
        animation.setEndValue(end_pos)
        animation.setEasingCurve(QEasingCurve.InCubic)
        
        # Remove widget when animation completes
        def on_finished():
            self.layout.removeWidget(notification)
            notification.deleteLater()
            self.update_position()
        
        animation.finished.connect(on_finished)
        animation.start()

    def update_position(self) -> None:
        """Update the position of the notification manager."""
        if self.parent():
            parent_rect = self.parent().rect()
            
            # Position in top-right corner with margin, accounting for title bar
            margin = 20
            title_bar_height = 40
            width = 400
            height = self.calculate_height()
            
            # Position below title bar
            x = parent_rect.width() - width - margin
            y = title_bar_height + margin
            
            # Ensure we don't go outside parent bounds
            if height > 0:
                max_height = parent_rect.height() - title_bar_height - (margin * 2)
                height = min(height, max_height)
            
            self.setGeometry(x, y, width, height)

    def calculate_height(self) -> int:
        """Calculate required height for all notifications."""
        if not self.notifications:
            return 0
        
        total_height = 0
        for notification in self.notifications:
            total_height += notification.height() + self.notification_spacing
        
        # Remove last spacing and add some padding
        return max(0, total_height - self.notification_spacing) + 20

    def resizeEvent(self, event) -> None:
        """Handle resize events."""
        super().resizeEvent(event)
        self.update_position()

    def eventFilter(self, obj, event) -> bool:
        """Filter events from parent to update position on resize."""
        if event.type() == QEvent.Type.Resize:
            # Update position when parent is resized
            self.update_position()
        return super().eventFilter(obj, event)

    def clear_all(self) -> None:
        """Clear all notifications."""
        for notification in self.notifications.copy():
            self.remove_notification(notification)