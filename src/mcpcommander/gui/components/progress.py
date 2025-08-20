"""Circular progress widget implementation."""

import math
from typing import Optional

from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, Property
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QFontMetrics
from PySide6.QtWidgets import QWidget

from mcpcommander.gui.theme.pyonedark import PyOneDarkColors


class CircularProgress(QWidget):
    """Custom circular progress widget with smooth animations."""

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        size: int = 100,
        progress: float = 0.0,
        animation_duration: int = 1000,
    ) -> None:
        super().__init__(parent)
        
        # Widget properties
        self._size = size
        self._progress = progress
        self._animation_duration = animation_duration
        
        # Visual properties
        self._line_width = 8
        self._line_color = PyOneDarkColors.PRIMARY
        self._background_color = PyOneDarkColors.SURFACE_VARIANT
        self._text_color = PyOneDarkColors.TEXT_PRIMARY
        self._show_percentage = True
        self._show_value = False
        self._max_value = 100.0
        self._current_value = 0.0
        
        # Animation
        self._animation = QPropertyAnimation(self, b"progress")
        self._animation.setDuration(animation_duration)
        self._animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # Setup widget
        self.setFixedSize(size, size)
        self.update()

    @Property(float)
    def progress(self) -> float:
        """Get current progress value (0.0 to 1.0)."""
        return self._progress

    @progress.setter
    def progress(self, value: float) -> None:
        """Set progress value with bounds checking."""
        self._progress = max(0.0, min(1.0, value))
        self._current_value = self._progress * self._max_value
        self.update()

    @Property(int)
    def line_width(self) -> int:
        """Get line width."""
        return self._line_width

    @line_width.setter
    def line_width(self, width: int) -> None:
        """Set line width."""
        self._line_width = max(1, width)
        self.update()

    @Property(str)
    def line_color(self) -> str:
        """Get line color."""
        return self._line_color

    @line_color.setter
    def line_color(self, color: str) -> None:
        """Set line color."""
        self._line_color = color
        self.update()

    @Property(str)
    def background_color(self) -> str:
        """Get background color."""
        return self._background_color

    @background_color.setter
    def background_color(self, color: str) -> None:
        """Set background color."""
        self._background_color = color
        self.update()

    @Property(str)
    def text_color(self) -> str:
        """Get text color."""
        return self._text_color

    @text_color.setter
    def text_color(self, color: str) -> None:
        """Set text color."""
        self._text_color = color
        self.update()

    @Property(bool)
    def show_percentage(self) -> bool:
        """Get show percentage flag."""
        return self._show_percentage

    @show_percentage.setter
    def show_percentage(self, show: bool) -> None:
        """Set show percentage flag."""
        self._show_percentage = show
        self.update()

    @Property(bool)
    def show_value(self) -> bool:
        """Get show value flag."""
        return self._show_value

    @show_value.setter
    def show_value(self, show: bool) -> None:
        """Set show value flag."""
        self._show_value = show
        self.update()

    @Property(float)
    def max_value(self) -> float:
        """Get maximum value."""
        return self._max_value

    @max_value.setter
    def max_value(self, value: float) -> None:
        """Set maximum value."""
        self._max_value = max(0.1, value)
        self._current_value = self._progress * self._max_value
        self.update()

    def set_progress_animated(self, value: float, duration: Optional[int] = None) -> None:
        """Set progress with smooth animation."""
        if duration is None:
            duration = self._animation_duration
            
        self._animation.setDuration(duration)
        self._animation.setStartValue(self._progress)
        self._animation.setEndValue(max(0.0, min(1.0, value)))
        self._animation.start()

    def set_value_animated(self, value: float, duration: Optional[int] = None) -> None:
        """Set value with animation (converts to progress)."""
        progress = value / self._max_value if self._max_value > 0 else 0
        self.set_progress_animated(progress, duration)

    def set_style(
        self,
        line_color: Optional[str] = None,
        background_color: Optional[str] = None,
        text_color: Optional[str] = None,
        line_width: Optional[int] = None,
    ) -> None:
        """Set visual style properties."""
        if line_color is not None:
            self._line_color = line_color
        if background_color is not None:
            self._background_color = background_color
        if text_color is not None:
            self._text_color = text_color
        if line_width is not None:
            self._line_width = max(1, line_width)
        self.update()

    def set_success_style(self) -> None:
        """Apply success styling."""
        self.set_style(line_color=PyOneDarkColors.SUCCESS)

    def set_warning_style(self) -> None:
        """Apply warning styling."""
        self.set_style(line_color=PyOneDarkColors.WARNING)

    def set_error_style(self) -> None:
        """Apply error styling."""
        self.set_style(line_color=PyOneDarkColors.ERROR)

    def set_primary_style(self) -> None:
        """Apply primary styling."""
        self.set_style(line_color=PyOneDarkColors.PRIMARY)

    def paintEvent(self, event) -> None:
        """Paint the circular progress."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Calculate dimensions
        rect = self.rect()
        center_x = rect.width() // 2
        center_y = rect.height() // 2
        radius = min(center_x, center_y) - self._line_width // 2

        # Draw background circle
        pen = QPen(QColor(self._background_color))
        pen.setWidth(self._line_width)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.drawEllipse(center_x - radius, center_y - radius, 2 * radius, 2 * radius)

        # Draw progress arc
        if self._progress > 0:
            pen = QPen(QColor(self._line_color))
            pen.setWidth(self._line_width)
            pen.setCapStyle(Qt.RoundCap)
            painter.setPen(pen)

            # Calculate angles (Qt uses 1/16th degrees, start from top)
            start_angle = 90 * 16  # Start from top (12 o'clock)
            span_angle = -int(self._progress * 360 * 16)  # Negative for clockwise

            painter.drawArc(
                center_x - radius,
                center_y - radius,
                2 * radius,
                2 * radius,
                start_angle,
                span_angle
            )

        # Draw text
        if self._show_percentage or self._show_value:
            painter.setPen(QColor(self._text_color))
            
            # Set font
            font = QFont()
            font.setPointSize(max(8, self._size // 10))
            font.setWeight(QFont.Bold)
            painter.setFont(font)

            # Determine text to display
            text = ""
            if self._show_percentage:
                percentage = int(self._progress * 100)
                text = f"{percentage}%"
            elif self._show_value:
                if self._current_value == int(self._current_value):
                    text = f"{int(self._current_value)}"
                else:
                    text = f"{self._current_value:.1f}"

            # Calculate text position
            font_metrics = QFontMetrics(font)
            text_rect = font_metrics.boundingRect(text)
            text_x = center_x - text_rect.width() // 2
            text_y = center_y + text_rect.height() // 4

            painter.drawText(text_x, text_y, text)

    def sizeHint(self):
        """Return recommended size."""
        return self.size()

    def minimumSizeHint(self):
        """Return minimum size."""
        return self.size()


class IndeterminateProgress(CircularProgress):
    """Indeterminate circular progress widget with spinning animation."""

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        size: int = 100,
        speed: int = 2000,  # Full rotation in milliseconds
    ) -> None:
        super().__init__(parent, size)
        
        self._speed = speed
        self._rotation_angle = 0
        self._arc_length = 0.25  # Length of the arc (0.0 to 1.0)
        
        # Setup rotation animation
        self._rotation_timer = QTimer()
        self._rotation_timer.timeout.connect(self._rotate)
        self._rotation_timer.setInterval(16)  # ~60 FPS
        
        # Hide text for indeterminate progress
        self._show_percentage = False
        self._show_value = False

    def start_animation(self) -> None:
        """Start the spinning animation."""
        self._rotation_timer.start()

    def stop_animation(self) -> None:
        """Stop the spinning animation."""
        self._rotation_timer.stop()

    def set_speed(self, speed: int) -> None:
        """Set rotation speed in milliseconds for full rotation."""
        self._speed = max(100, speed)

    def set_arc_length(self, length: float) -> None:
        """Set the length of the spinning arc (0.0 to 1.0)."""
        self._arc_length = max(0.1, min(1.0, length))

    def _rotate(self) -> None:
        """Update rotation angle."""
        # Calculate rotation increment based on speed
        increment = 360.0 / (self._speed / 16)  # degrees per frame
        self._rotation_angle = (self._rotation_angle + increment) % 360
        self.update()

    def paintEvent(self, event) -> None:
        """Paint the spinning circular progress."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Calculate dimensions
        rect = self.rect()
        center_x = rect.width() // 2
        center_y = rect.height() // 2
        radius = min(center_x, center_y) - self._line_width // 2

        # Draw background circle
        pen = QPen(QColor(self._background_color))
        pen.setWidth(self._line_width)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.drawEllipse(center_x - radius, center_y - radius, 2 * radius, 2 * radius)

        # Draw spinning arc
        pen = QPen(QColor(self._line_color))
        pen.setWidth(self._line_width)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)

        # Calculate arc angles
        start_angle = int((90 - self._rotation_angle) * 16)  # Convert to 1/16th degrees
        span_angle = -int(self._arc_length * 360 * 16)  # Negative for clockwise

        painter.drawArc(
            center_x - radius,
            center_y - radius,
            2 * radius,
            2 * radius,
            start_angle,
            span_angle
        )

    def showEvent(self, event) -> None:
        """Start animation when widget becomes visible."""
        super().showEvent(event)
        self.start_animation()

    def hideEvent(self, event) -> None:
        """Stop animation when widget becomes hidden."""
        super().hideEvent(event)
        self.stop_animation()