"""
PyOneDark Theme Implementation for MCP Commander GUI

This theme is based on the PyOneDark theme by Wanderson M. Pimenta
GitHub: https://github.com/wandersonwagner/PyOneDark

The MIT License (MIT)

Copyright (c) 2023 Wanderson M. Pimenta

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from typing import Dict, Any


class PyOneDarkColors:
    """PyOneDark color palette."""
    
    # Main colors from PyOneDark theme
    BACKGROUND = "#282c34"
    SURFACE = "#3c4043"
    SURFACE_VARIANT = "#484c54"
    PRIMARY = "#61afef"
    SECONDARY = "#98c379"
    SUCCESS = "#98c379"
    WARNING = "#e5c07b"
    ERROR = "#e06c75"
    
    # Text colors
    TEXT_PRIMARY = "#abb2bf"
    TEXT_SECONDARY = "#7d8590"
    TEXT_DISABLED = "#5c6370"
    
    # Accent colors
    ACCENT_PURPLE = "#c678dd"
    ACCENT_CYAN = "#56b6c2"
    ACCENT_ORANGE = "#d19a66"
    ACCENT_RED = "#e06c75"
    ACCENT_GREEN = "#98c379"
    ACCENT_BLUE = "#61afef"
    
    # Interactive states
    HOVER = "#3e4651"
    PRESSED = "#2c3038"
    FOCUS = "#61afef"
    DISABLED = "#4b5263"
    
    # Borders and separators
    BORDER = "#2c323c"
    SEPARATOR = "#21252b"


class PyOneDarkTheme:
    """PyOneDark theme implementation for MCP Commander."""
    
    @classmethod
    def get_stylesheet(cls) -> str:
        """Get complete stylesheet for the application."""
        return f"""
/* ========================================
   MCP Commander - PyOneDark Theme
   Based on PyOneDark by Wanderson M. Pimenta
   https://github.com/wandersonwagner/PyOneDark
   ======================================== */

/* Main Application */
QMainWindow {{
    background-color: {PyOneDarkColors.BACKGROUND};
    color: {PyOneDarkColors.TEXT_PRIMARY};
    border: none;
}}

/* Frame and containers */
QFrame {{
    background-color: {PyOneDarkColors.BACKGROUND};
    border: none;
    color: {PyOneDarkColors.TEXT_PRIMARY};
}}

QFrame[frameShape="1"] {{
    border: 1px solid {PyOneDarkColors.BORDER};
}}

/* Sidebar */
QFrame#sidebar {{
    background-color: {PyOneDarkColors.SURFACE};
    border-right: 1px solid {PyOneDarkColors.BORDER};
    min-width: 250px;
    max-width: 250px;
}}

/* Sidebar buttons */
QPushButton[sidebar="true"] {{
    background-color: transparent;
    border: none;
    color: {PyOneDarkColors.TEXT_SECONDARY};
    text-align: left;
    padding: 12px 20px;
    font-size: 14px;
    font-weight: 500;
    border-radius: 8px;
    margin: 2px 8px;
}}

QPushButton[sidebar="true"]:hover {{
    background-color: {PyOneDarkColors.HOVER};
    color: {PyOneDarkColors.TEXT_PRIMARY};
}}

QPushButton[sidebar="true"]:pressed {{
    background-color: {PyOneDarkColors.PRESSED};
}}

QPushButton[sidebar="true"][active="true"] {{
    background-color: {PyOneDarkColors.PRIMARY};
    color: #ffffff;
}}

/* Regular buttons */
QPushButton {{
    background-color: {PyOneDarkColors.SURFACE};
    color: {PyOneDarkColors.TEXT_PRIMARY};
    border: 1px solid {PyOneDarkColors.BORDER};
    padding: 8px 16px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 500;
}}

QPushButton:hover {{
    background-color: {PyOneDarkColors.HOVER};
    border-color: {PyOneDarkColors.PRIMARY};
}}

QPushButton:pressed {{
    background-color: {PyOneDarkColors.PRESSED};
}}

QPushButton:disabled {{
    background-color: {PyOneDarkColors.DISABLED};
    color: {PyOneDarkColors.TEXT_DISABLED};
    border-color: {PyOneDarkColors.DISABLED};
}}

/* Primary button */
QPushButton[primary="true"] {{
    background-color: {PyOneDarkColors.PRIMARY};
    color: #ffffff;
    border: none;
}}

QPushButton[primary="true"]:hover {{
    background-color: #528bdb;
}}

QPushButton[primary="true"]:pressed {{
    background-color: #4682c4;
}}

/* Success button */
QPushButton[success="true"] {{
    background-color: {PyOneDarkColors.SUCCESS};
    color: #ffffff;
    border: none;
}}

QPushButton[success="true"]:hover {{
    background-color: #85b368;
}}

/* Error/danger button */
QPushButton[error="true"] {{
    background-color: {PyOneDarkColors.ERROR};
    color: #ffffff;
    border: none;
}}

QPushButton[error="true"]:hover {{
    background-color: #d55a64;
}}

/* Labels */
QLabel {{
    color: {PyOneDarkColors.TEXT_PRIMARY};
    background-color: transparent;
    border: none;
}}

QLabel[heading="true"] {{
    font-size: 18px;
    font-weight: 600;
    color: {PyOneDarkColors.TEXT_PRIMARY};
}}

QLabel[subheading="true"] {{
    font-size: 14px;
    font-weight: 500;
    color: {PyOneDarkColors.TEXT_SECONDARY};
}}

QLabel[caption="true"] {{
    font-size: 12px;
    color: {PyOneDarkColors.TEXT_SECONDARY};
}}

/* Line edits */
QLineEdit {{
    background-color: {PyOneDarkColors.SURFACE};
    color: {PyOneDarkColors.TEXT_PRIMARY};
    border: 1px solid {PyOneDarkColors.BORDER};
    padding: 8px 12px;
    border-radius: 4px;
    font-size: 13px;
}}

QLineEdit:focus {{
    border-color: {PyOneDarkColors.PRIMARY};
    background-color: {PyOneDarkColors.SURFACE_VARIANT};
}}

QLineEdit:disabled {{
    background-color: {PyOneDarkColors.DISABLED};
    color: {PyOneDarkColors.TEXT_DISABLED};
}}

/* Line edits within cards should have subtle borders */
QFrame QLineEdit {{
    border: 1px solid {PyOneDarkColors.SEPARATOR};
    border-radius: 3px;
    padding: 6px 8px;
}}

QFrame QLineEdit:focus {{
    border-color: {PyOneDarkColors.PRIMARY};
}}

/* Text edits */
QTextEdit, QPlainTextEdit {{
    background-color: {PyOneDarkColors.SURFACE};
    color: {PyOneDarkColors.TEXT_PRIMARY};
    border: 1px solid {PyOneDarkColors.BORDER};
    border-radius: 4px;
    padding: 8px;
    font-family: "Consolas", "Monaco", monospace;
    font-size: 12px;
}}

QTextEdit:focus, QPlainTextEdit:focus {{
    border-color: {PyOneDarkColors.PRIMARY};
}}

/* Text edits within cards should have subtle borders */
QFrame QTextEdit, QFrame QPlainTextEdit {{
    border: 1px solid {PyOneDarkColors.SEPARATOR};
    border-radius: 3px;
    padding: 6px;
}}

QFrame QTextEdit:focus, QFrame QPlainTextEdit:focus {{
    border-color: {PyOneDarkColors.PRIMARY};
}}

/* Combo boxes */
QComboBox {{
    background-color: {PyOneDarkColors.SURFACE};
    color: {PyOneDarkColors.TEXT_PRIMARY};
    border: 1px solid {PyOneDarkColors.BORDER};
    padding: 6px 12px;
    border-radius: 6px;
    font-size: 13px;
}}

QComboBox:hover {{
    border-color: {PyOneDarkColors.PRIMARY};
}}

QComboBox::drop-down {{
    border: none;
    width: 20px;
}}

QComboBox::down-arrow {{
    image: none;
    border: 5px solid transparent;
    border-top: 5px solid {PyOneDarkColors.TEXT_SECONDARY};
    margin-right: 5px;
}}

QComboBox QAbstractItemView {{
    background-color: {PyOneDarkColors.SURFACE};
    color: {PyOneDarkColors.TEXT_PRIMARY};
    border: 1px solid {PyOneDarkColors.BORDER};
    selection-background-color: {PyOneDarkColors.PRIMARY};
    outline: none;
}}

/* List widgets */
QListWidget {{
    background-color: {PyOneDarkColors.SURFACE};
    color: {PyOneDarkColors.TEXT_PRIMARY};
    border: 1px solid {PyOneDarkColors.BORDER};
    border-radius: 6px;
    outline: none;
}}

QListWidget::item {{
    padding: 8px 12px;
    border-bottom: 1px solid {PyOneDarkColors.SEPARATOR};
}}

QListWidget::item:hover {{
    background-color: {PyOneDarkColors.HOVER};
}}

QListWidget::item:selected {{
    background-color: {PyOneDarkColors.PRIMARY};
    color: #ffffff;
}}

/* Table widgets */
QTableWidget {{
    background-color: {PyOneDarkColors.SURFACE};
    color: {PyOneDarkColors.TEXT_PRIMARY};
    border: 1px solid {PyOneDarkColors.BORDER};
    border-radius: 6px;
    gridline-color: {PyOneDarkColors.SEPARATOR};
    outline: none;
}}

QTableWidget::item {{
    padding: 8px;
    border-bottom: 1px solid {PyOneDarkColors.SEPARATOR};
}}

QTableWidget::item:hover {{
    background-color: {PyOneDarkColors.HOVER};
}}

QTableWidget::item:selected {{
    background-color: {PyOneDarkColors.PRIMARY};
    color: #ffffff;
}}

QHeaderView::section {{
    background-color: {PyOneDarkColors.SURFACE_VARIANT};
    color: {PyOneDarkColors.TEXT_PRIMARY};
    border: none;
    border-bottom: 1px solid {PyOneDarkColors.BORDER};
    padding: 8px 12px;
    font-weight: 600;
}}

/* Tree widgets */
QTreeWidget {{
    background-color: {PyOneDarkColors.SURFACE};
    color: {PyOneDarkColors.TEXT_PRIMARY};
    border: 1px solid {PyOneDarkColors.BORDER};
    border-radius: 6px;
    outline: none;
}}

QTreeWidget::item {{
    padding: 4px 8px;
    border-bottom: 1px solid {PyOneDarkColors.SEPARATOR};
}}

QTreeWidget::item:hover {{
    background-color: {PyOneDarkColors.HOVER};
}}

QTreeWidget::item:selected {{
    background-color: {PyOneDarkColors.PRIMARY};
    color: #ffffff;
}}

/* Progress bars */
QProgressBar {{
    background-color: {PyOneDarkColors.SURFACE};
    border: 1px solid {PyOneDarkColors.BORDER};
    border-radius: 8px;
    text-align: center;
    color: {PyOneDarkColors.TEXT_PRIMARY};
    font-weight: 500;
}}

QProgressBar::chunk {{
    background-color: {PyOneDarkColors.PRIMARY};
    border-radius: 7px;
}}

QProgressBar[success="true"]::chunk {{
    background-color: {PyOneDarkColors.SUCCESS};
}}

QProgressBar[warning="true"]::chunk {{
    background-color: {PyOneDarkColors.WARNING};
}}

QProgressBar[error="true"]::chunk {{
    background-color: {PyOneDarkColors.ERROR};
}}

/* Scroll bars */
QScrollBar:vertical {{
    background-color: {PyOneDarkColors.SURFACE};
    width: 12px;
    border-radius: 6px;
}}

QScrollBar::handle:vertical {{
    background-color: {PyOneDarkColors.TEXT_SECONDARY};
    border-radius: 6px;
    min-height: 20px;
    margin: 2px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {PyOneDarkColors.PRIMARY};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    background: none;
    border: none;
}}

QScrollBar:horizontal {{
    background-color: {PyOneDarkColors.SURFACE};
    height: 12px;
    border-radius: 6px;
}}

QScrollBar::handle:horizontal {{
    background-color: {PyOneDarkColors.TEXT_SECONDARY};
    border-radius: 6px;
    min-width: 20px;
    margin: 2px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {PyOneDarkColors.PRIMARY};
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    background: none;
    border: none;
}}

/* Tab widgets */
QTabWidget::pane {{
    border: 1px solid {PyOneDarkColors.BORDER};
    border-radius: 6px;
    background-color: {PyOneDarkColors.SURFACE};
}}

QTabBar::tab {{
    background-color: {PyOneDarkColors.SURFACE_VARIANT};
    color: {PyOneDarkColors.TEXT_SECONDARY};
    padding: 8px 16px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}}

QTabBar::tab:hover {{
    background-color: {PyOneDarkColors.HOVER};
    color: {PyOneDarkColors.TEXT_PRIMARY};
}}

QTabBar::tab:selected {{
    background-color: {PyOneDarkColors.PRIMARY};
    color: #ffffff;
}}

/* Checkboxes */
QCheckBox {{
    color: {PyOneDarkColors.TEXT_PRIMARY};
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 2px solid {PyOneDarkColors.BORDER};
    border-radius: 4px;
    background-color: {PyOneDarkColors.SURFACE};
}}

QCheckBox::indicator:hover {{
    border-color: {PyOneDarkColors.PRIMARY};
}}

QCheckBox::indicator:checked {{
    background-color: {PyOneDarkColors.PRIMARY};
    border-color: {PyOneDarkColors.PRIMARY};
    image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEwIDNMNC41IDguNUwyIDYiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPgo=);
}}

/* Radio buttons */
QRadioButton {{
    color: {PyOneDarkColors.TEXT_PRIMARY};
    spacing: 8px;
}}

QRadioButton::indicator {{
    width: 18px;
    height: 18px;
    border: 2px solid {PyOneDarkColors.BORDER};
    border-radius: 10px;
    background-color: {PyOneDarkColors.SURFACE};
}}

QRadioButton::indicator:hover {{
    border-color: {PyOneDarkColors.PRIMARY};
}}

QRadioButton::indicator:checked {{
    background-color: {PyOneDarkColors.PRIMARY};
    border-color: {PyOneDarkColors.PRIMARY};
}}

QRadioButton::indicator:checked::after {{
    content: "";
    width: 8px;
    height: 8px;
    border-radius: 4px;
    background-color: #ffffff;
    position: absolute;
    top: 3px;
    left: 3px;
}}

/* Tool tips */
QToolTip {{
    background-color: {PyOneDarkColors.SURFACE_VARIANT};
    color: {PyOneDarkColors.TEXT_PRIMARY};
    border: 1px solid {PyOneDarkColors.BORDER};
    border-radius: 4px;
    padding: 6px 8px;
    font-size: 12px;
}}

/* Status bar */
QStatusBar {{
    background-color: {PyOneDarkColors.SURFACE};
    color: {PyOneDarkColors.TEXT_SECONDARY};
    border-top: 1px solid {PyOneDarkColors.BORDER};
}}

/* Menu bar */
QMenuBar {{
    background-color: {PyOneDarkColors.SURFACE};
    color: {PyOneDarkColors.TEXT_PRIMARY};
    border-bottom: 1px solid {PyOneDarkColors.BORDER};
}}

QMenuBar::item {{
    padding: 6px 12px;
}}

QMenuBar::item:hover {{
    background-color: {PyOneDarkColors.HOVER};
}}

/* Menus */
QMenu {{
    background-color: {PyOneDarkColors.SURFACE};
    color: {PyOneDarkColors.TEXT_PRIMARY};
    border: 1px solid {PyOneDarkColors.BORDER};
    border-radius: 6px;
}}

QMenu::item {{
    padding: 8px 16px;
}}

QMenu::item:hover {{
    background-color: {PyOneDarkColors.HOVER};
}}

QMenu::item:selected {{
    background-color: {PyOneDarkColors.PRIMARY};
    color: #ffffff;
}}

/* Splitters */
QSplitter::handle {{
    background-color: {PyOneDarkColors.BORDER};
}}

QSplitter::handle:horizontal {{
    width: 2px;
}}

QSplitter::handle:vertical {{
    height: 2px;
}}
"""

    @classmethod
    def get_colors(cls) -> Dict[str, str]:
        """Get color dictionary for programmatic access."""
        return {
            "background": PyOneDarkColors.BACKGROUND,
            "surface": PyOneDarkColors.SURFACE,
            "surface_variant": PyOneDarkColors.SURFACE_VARIANT,
            "primary": PyOneDarkColors.PRIMARY,
            "secondary": PyOneDarkColors.SECONDARY,
            "success": PyOneDarkColors.SUCCESS,
            "warning": PyOneDarkColors.WARNING,
            "error": PyOneDarkColors.ERROR,
            "text_primary": PyOneDarkColors.TEXT_PRIMARY,
            "text_secondary": PyOneDarkColors.TEXT_SECONDARY,
            "text_disabled": PyOneDarkColors.TEXT_DISABLED,
            "hover": PyOneDarkColors.HOVER,
            "pressed": PyOneDarkColors.PRESSED,
            "focus": PyOneDarkColors.FOCUS,
            "border": PyOneDarkColors.BORDER,
            "separator": PyOneDarkColors.SEPARATOR,
        }

    @classmethod
    def get_accent_colors(cls) -> Dict[str, str]:
        """Get accent colors for charts and data visualization."""
        return {
            "purple": PyOneDarkColors.ACCENT_PURPLE,
            "cyan": PyOneDarkColors.ACCENT_CYAN,
            "orange": PyOneDarkColors.ACCENT_ORANGE,
            "red": PyOneDarkColors.ACCENT_RED,
            "green": PyOneDarkColors.ACCENT_GREEN,
            "blue": PyOneDarkColors.ACCENT_BLUE,
        }