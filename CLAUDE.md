# MCP Commander - Development Plan & Maturity Roadmap

## Critical Bug Fix - QPainter.drawCircle Error

### Issue Analysis
**Date**: 2025-08-20
**Priority**: CRITICAL - Application crashes on startup
**Impact**: GUI cannot render properly, crashes during paint events

**Error Details**:
```
AttributeError: 'PySide6.QtGui.QPainter' object has no attribute 'drawCircle'
QPaintDevice: Cannot destroy paint device that is being painted
```

**Root Cause**: 
The `QPainter` class in Qt6/PySide6 doesn't have a `drawCircle` method. The correct method is `drawEllipse`. This error occurs in:
- `src/mcpcommander/gui/components/progress.py` lines 204 and 327

### Technical Implementation

#### Current Problematic Code:
```python
# Line 204: CircularProgress.paintEvent()
painter.drawCircle(center_x, center_y, radius)

# Line 327: IndeterminateProgress.paintEvent()
painter.drawCircle(center_x, center_y, radius)
```

#### Correct Implementation Strategy:
Replace `painter.drawCircle(center_x, center_y, radius)` with:
```python
# Method 1: Using drawEllipse with center point and radii
painter.drawEllipse(QPoint(center_x, center_y), radius, radius)

# Method 2: Using drawEllipse with rectangle bounds (more common)
painter.drawEllipse(center_x - radius, center_y - radius, 2 * radius, 2 * radius)
```

#### Implementation Plan:
1. **Fix CircularProgress.paintEvent()** (line 204)
   - Replace drawCircle with drawEllipse using rectangle bounds
   - Maintain existing visual appearance and positioning
   
2. **Fix IndeterminateProgress.paintEvent()** (line 327)
   - Apply same fix to spinning progress widget
   - Ensure animation continues to work correctly

3. **Testing Strategy**:
   - Verify both determinate and indeterminate progress widgets render correctly
   - Test different sizes and progress values
   - Confirm no paint device destruction errors

#### Code Quality Considerations:
- Use rectangle-based drawEllipse for consistency with Qt best practices
- Maintain existing mathematical calculations for positioning
- Preserve all existing widget properties and animations

### Implementation Results:
✅ **COMPLETED** - All critical GUI fixes successfully implemented and tested:

1. **✅ QPainter.drawCircle Errors Fixed**
   - Replaced `painter.drawCircle()` with `painter.drawEllipse()` in both CircularProgress and IndeterminateProgress classes
   - Application now starts and renders without paint device errors
   - All progress widgets render correctly

2. **✅ Window Resizing Functionality Added**
   - Implemented custom resize grips with 6-pixel margin detection
   - Added 8-directional resize support (corners and edges)
   - Added proper cursor feedback (resize cursors)
   - Enforced minimum size constraints during resize
   - Separated resize handling from title bar drag operations

3. **✅ Title Bar Behavior Enhanced**
   - Fixed double-click to properly toggle maximize/restore (Windows standard behavior)
   - Added "snap-out" functionality when dragging maximized windows
   - Prevented resize operations in title bar area
   - Improved window dragging with proper position calculations

4. **✅ Window Control Button Icons**
   - Replaced text characters with proper vector icons
   - Created minimize, maximize/restore, and close icons using QPainter
   - Added dynamic icon switching (maximize ↔ restore based on window state)
   - Connected window state change events to update icons appropriately
   - Improved visual consistency with 16x16 icon size

5. **✅ Notification System Fixed**
   - Removed problematic shadow rendering causing "black shadows"
   - Fixed positioning to account for title bar height (40px offset)
   - Changed from separate window to proper child widget
   - Added parent resize event filtering for dynamic repositioning
   - Simplified paint event to prevent paint device destruction errors
   - Maintained slide-in/slide-out animations

**Testing Results:**
- Application runs for 15+ minutes without crashes
- All GUI interactions work correctly (resize, maximize, minimize, close)
- Page navigation functions properly
- Regular background operations continue normally
- No QPainter or paint device errors in logs

---

## Project Overview

**MCP Commander** is a command-line tool designed to manage MCP (Model Context Protocol) servers across different code editors. It provides a unified interface for adding, removing, listing, and monitoring MCP server configurations across Claude Code, Claude Desktop, and Cursor.

## Current State vs Target Maturity

### Maturity Gap Analysis (Based on jira-mcp Standards)

| Component | Current State | Target State | Priority |
|-----------|---------------|--------------|----------|
| **Language & Packaging** | Python 3.6+ | Python 3.8+ with modern tooling | High |
| **Project Structure** | Basic (4 files) | Professional structure with proper directories | High |
| **Testing** | None | Comprehensive test suite (unit/integration/e2e) | Critical |
| **Documentation** | Basic README | Comprehensive docs with examples | High |
| **CI/CD** | None | GitHub Actions with automated testing/releases | High |
| **Code Quality** | Basic | Pre-commit hooks, linting, type checking | High |
| **Error Handling** | Basic | Centralized error handling with user-friendly messages | Medium |
| **Logging** | Print statements | Structured logging with levels | Medium |
| **Configuration** | Simple JSON | Schema validation and environment management | Medium |
| **Packaging** | Manual installation | PyPI package with automated releases | High |
| **Versioning** | None | Semantic versioning with automated changelog | Medium |

## Architecture Transformation Plan

### Phase 1: Foundation & Structure (High Priority)
```
mcpCommander/
├── src/
│   ├── mcpcommander/
│   │   ├── __init__.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── manager.py          # MCPManager class
│   │   │   ├── config.py           # Configuration handling
│   │   │   └── editor_handlers.py  # Editor-specific logic
│   │   ├── cli/
│   │   │   ├── __init__.py
│   │   │   └── main.py             # CLI interface
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── logger.py           # Structured logging
│   │   │   ├── errors.py           # Error handling
│   │   │   └── validators.py       # Input validation
│   │   └── schemas/
│   │       ├── __init__.py
│   │       └── config_schema.py    # Pydantic schemas
├── tests/
│   ├── __init__.py
│   ├── conftest.py                 # Pytest configuration
│   ├── unit/
│   │   ├── test_manager.py
│   │   ├── test_config.py
│   │   └── test_cli.py
│   ├── integration/
│   │   └── test_editor_integration.py
│   ├── e2e/
│   │   └── test_workflow.py
│   └── fixtures/
│       └── sample_configs.py
├── docs/
│   ├── README.md
│   ├── CONTRIBUTING.md
│   ├── CHANGELOG.md
│   ├── TROUBLESHOOTING.md
│   └── API.md
├── scripts/
│   ├── setup.py
│   ├── release.py
│   └── validate_config.py
├── .github/
│   └── workflows/
│       ├── test.yml
│       ├── release.yml
│       └── quality.yml
├── pyproject.toml              # Modern Python packaging
├── requirements/
│   ├── base.txt
│   ├── dev.txt
│   └── test.txt
├── .pre-commit-config.yaml     # Pre-commit hooks
├── pytest.ini                 # Test configuration
├── .gitignore
└── CLAUDE.md
```

### Phase 2: Modern Python Tooling
- **Packaging**: Migrate to `pyproject.toml` with `setuptools` or `poetry`
- **Type System**: Add comprehensive type hints with `mypy`
- **Dependencies**: Use `pydantic` for configuration validation
- **CLI Framework**: Migrate from `argparse` to `typer` or `click`
- **Logging**: Implement structured logging with `loguru` or standard `logging`

### Phase 3: Quality & Testing Infrastructure
- **Testing Framework**: `pytest` with coverage reporting
- **Test Types**: Unit, integration, and end-to-end tests
- **Mock Framework**: `pytest-mock` for testing external dependencies
- **Pre-commit Hooks**: Automated code quality checks
- **CI/CD Pipeline**: GitHub Actions for testing and releases

### Phase 4: Distribution & Automation
- **PyPI Package**: Automated package publishing
- **GitHub Releases**: Automated release creation with assets
- **Documentation**: Automated documentation generation
- **Version Management**: Semantic versioning with automated changelog

## Technical Implementation Details

### Current Architecture Analysis

#### Strengths to Preserve
- Clean `MCPManager` class design
- Simple JSONPath implementation
- Cross-editor support architecture
- Unified CLI interface concept

#### Components Requiring Transformation

1. **mcp_manager.py** (256 lines) → **src/mcpcommander/core/manager.py**
   - Add type hints and pydantic models
   - Implement centralized error handling
   - Add structured logging
   - Split into focused modules

2. **CLI Interface** → **src/mcpcommander/cli/main.py**
   - Migrate from argparse to typer
   - Add rich console output formatting
   - Implement command context management

3. **Configuration Management** → **src/mcpcommander/core/config.py**
   - Add schema validation with pydantic
   - Environment variable support
   - Configuration migration tools

## JIRA Development Tracking

### Epic: ZDEVOPS-208
**MCP Commander - Cross-Platform MCP Server Management Tool**
- URL: https://braindeadsec.atlassian.net/browse/ZDEVOPS-208

### Updated Stories with Tasks:
1. **ZDEVOPS-209**: Core MCP Server Management Functionality
   - ZDEVOPS-212: Implement MCPManager class with configuration loading
   - ZDEVOPS-213: Add server addition and removal functionality
   - ZDEVOPS-214: Create server listing and status checking features

2. **ZDEVOPS-210**: Command Line Interface and User Experience
   - ZDEVOPS-215: Implement argparse-based CLI interface

3. **ZDEVOPS-211**: Testing and Quality Assurance
   - ZDEVOPS-216: Create unit tests for MCPManager class
   - ZDEVOPS-217: Add integration tests for CLI operations

### Additional Development Tasks Needed
- **Project Structure Modernization**
- **Python Packaging & Distribution Setup**
- **CI/CD Pipeline Implementation**
- **Documentation Enhancement**
- **Type System Implementation**
- **Error Handling Centralization**
- **Logging System Implementation**

## Development Standards (Based on jira-mcp)

### Code Quality Requirements
```python
# Type hints for all public methods
def add_server(
    self,
    server_name: str,
    server_config: Union[str, Dict[str, Any]],
    editor_name: Optional[str] = None
) -> None:
    """Add a server to all editors or a specific editor."""
```

### Error Handling Pattern
```python
from mcpcommander.utils.errors import MCPCommanderError, ConfigurationError

class MCPManager:
    def add_server(self, server_name: str, server_config: str) -> None:
        try:
            # Implementation
            pass
        except Exception as e:
            raise ConfigurationError(f"Failed to add server '{server_name}': {e}") from e
```

### Testing Requirements
- **Unit Tests**: 90%+ coverage on core functionality
- **Integration Tests**: Editor configuration verification
- **E2E Tests**: Complete workflow validation
- **Pre-commit Testing**: Automated test execution

### Documentation Standards
- **README**: Comprehensive with badges, examples, troubleshooting
- **API Documentation**: All public methods documented
- **CHANGELOG**: Keep-a-Changelog format
- **Contributing Guide**: Development setup and guidelines

## Implementation Priorities

### Phase 1 (Critical - Week 1-2)
1. **Project restructuring** to modern Python layout
2. **Core functionality migration** with type hints
3. **Basic test suite implementation**
4. **PyPI packaging setup**

### Phase 2 (High - Week 3-4)
1. **Comprehensive testing suite**
2. **CI/CD pipeline implementation**
3. **Enhanced error handling and logging**
4. **Documentation overhaul**

### Phase 3 (Medium - Week 5-6)
1. **Pre-commit hooks and quality automation**
2. **Advanced configuration validation**
3. **Cross-platform compatibility**
4. **Performance optimizations**

## Success Metrics

### Quality Indicators
- **Test Coverage**: >90% line coverage
- **Type Coverage**: 100% of public API
- **Documentation**: All public methods documented
- **CI/CD**: Automated testing and releases
- **Distribution**: PyPI package available

### Functionality Benchmarks
- **Performance**: <500ms for typical operations
- **Reliability**: Zero critical bugs in core functionality
- **Usability**: Comprehensive help and error messages
- **Compatibility**: Python 3.8+ cross-platform support

---
*Development roadmap created: 2025-08-11*
*Target completion: 6 weeks*
*JIRA Epic: ZDEVOPS-208*
- When you're working with Jira and you create tasks/stories/epics - You also need to link the Tasks to the Epic, not just the Stories.
- When asked to "add a new feature", check if the feature already has a related task, if not, create it.

- The `config.example.json` file is a reference for the user, not for the application. The application should generate its own config file (either empty or "discovered") from scratch based on the user's current environment and OS.
- It's `mcp config reset` to erase MCP Commander configuration only. It's `mcp config reset --include-backups` to erase both config backups, otherwise backups are kept by default.
- You should still ask the user to confirm, with a y/N prompt (N by default), like it used to, for destructive operations such as `mcp config reset`

## GUI Implementation - Qt6/PySide6 with PyOneDark Theme

### Overview
MCP Commander GUI provides a modern, professional graphical interface using Qt6 (PySide6) with the PyOneDark theme, offering complete feature parity with the CLI while enhancing user experience through visual feedback and intuitive interactions.

### Design Principles & Guidelines

#### Core Principles
1. **Feature Parity**: Every CLI command must have a GUI equivalent
2. **Visual Feedback**: All operations provide immediate visual feedback (progress bars, animations, notifications)
3. **Non-Blocking UI**: Long operations run asynchronously to maintain responsive interface
4. **Consistent Theme**: Strict adherence to PyOneDark dark theme aesthetics
5. **Backend Reuse**: GUI must use existing core.manager and schemas, not duplicate logic
6. **Cross-Platform**: Must work identically on Windows, macOS, and Linux
7. **Accessibility**: Keyboard shortcuts for all major operations
8. **Error Recovery**: Graceful error handling with user-friendly messages

#### Visual Design Standards
- **Color Palette**:
  - Background: #282c34 (main), #21252b (sidebar)
  - Primary: #61afef (blue)
  - Success: #98c379 (green)
  - Warning: #e5c07b (yellow)
  - Error: #e06c75 (red)
  - Accent: #c678dd (purple), #e06c75 (pink)
- **Typography**: 
  - Font: Segoe UI (Windows), SF Pro (macOS), Ubuntu (Linux)
  - Sizes: 16px (headers), 14px (body), 12px (captions)
- **Spacing**: 8px grid system
- **Border Radius**: 8px for cards, 4px for buttons
- **Shadows**: Subtle drop shadows for depth

### GUI Architecture

#### Directory Structure
```
src/mcpcommander/gui/
├── __init__.py                 # GUI module initialization
├── app.py                      # Application entry point (QApplication)
├── main_window.py              # Main window implementation
├── themes/
│   ├── __init__.py
│   ├── pyonedark.py           # PyOneDark theme QSS and palette
│   ├── resources.qrc          # Qt resource file
│   └── icons/                 # SVG icons (light colors for dark theme)
├── widgets/
│   ├── __init__.py
│   ├── sidebar.py             # Collapsible navigation sidebar
│   ├── circular_progress.py   # Custom circular progress widget
│   ├── toggle_switch.py       # iOS-style toggle switches
│   ├── custom_buttons.py      # Styled buttons with ripple effect
│   ├── data_table.py          # Enhanced QTableWidget
│   └── toast.py               # Toast notification widget
├── pages/
│   ├── __init__.py
│   ├── base_page.py           # Base class for all pages
│   ├── dashboard.py           # Home/overview page
│   ├── servers.py             # Server management page
│   ├── editors.py             # Editor configuration page
│   ├── backup.py              # Backup & restore page
│   ├── discovery.py           # Auto-discovery page
│   ├── status.py              # Status monitoring page
│   └── settings.py            # Application settings page
├── dialogs/
│   ├── __init__.py
│   ├── confirm_dialog.py      # Custom confirmation dialogs
│   ├── server_dialog.py       # Add/Edit server dialog
│   └── json_editor.py         # JSON configuration editor
└── utils/
    ├── __init__.py
    ├── animations.py          # QPropertyAnimation utilities
    ├── async_worker.py        # QThread workers for async ops
    └── signals.py             # Custom Qt signals
```

### Component Implementation Guidelines

#### 1. Main Window (`main_window.py`)
- **Frameless Window**: Custom title bar with min/max/close buttons
- **Window Controls**: Draggable title bar, resize grips
- **Layout**: QSplitter with collapsible sidebar (250px) and content area
- **System Tray**: Minimize to tray option with context menu
- **Shortcuts**: 
  - Ctrl+Q: Quit
  - Ctrl+S: Add Server
  - Ctrl+B: Backup
  - F5: Refresh/Discovery

#### 2. Sidebar Navigation (`widgets/sidebar.py`)
- **Structure**: QListWidget with custom delegates
- **Items**: Icon + Label, hover effects, active state
- **Collapse**: Animated width change (250px ↔ 60px)
- **Navigation Items**:
  ```python
  MENU_ITEMS = [
      ("dashboard", "Dashboard", "home.svg"),
      ("servers", "Servers", "server.svg"),
      ("editors", "Editors", "edit.svg"),
      ("backup", "Backup", "save.svg"),
      ("discovery", "Discovery", "search.svg"),
      ("status", "Status", "activity.svg"),
      ("settings", "Settings", "settings.svg"),
  ]
  ```

#### 3. Custom Widgets

##### Circular Progress (`widgets/circular_progress.py`)
- **Properties**: 
  - value: 0-100
  - color: QColor
  - thickness: stroke width
  - animated: bool
- **Animation**: QPropertyAnimation for smooth transitions
- **Text**: Percentage in center

##### Toggle Switch (`widgets/toggle_switch.py`)
- **States**: On/Off with animated slide
- **Signals**: toggled(bool)
- **Customization**: Colors, size, animation duration

##### Data Table (`widgets/data_table.py`)
- **Features**:
  - Sortable columns
  - Search/filter bar
  - Context menu (Edit, Delete, Copy)
  - Alternating row colors
  - Selection highlighting

#### 4. Pages Implementation

##### Dashboard Page (`pages/dashboard.py`)
- **Layout**: Grid of cards
- **Widgets**:
  - 3 circular progress indicators (servers, editors, backups)
  - Quick actions grid (4 buttons)
  - Recent activity list (last 10 operations)
  - System status summary

##### Server Management Page (`pages/servers.py`)
- **Sections**:
  - Add Server Form (name, config JSON, editor dropdown)
  - Server List Table (name, command, editor, actions)
  - Bulk Operations toolbar
- **Validation**: Real-time JSON validation
- **Actions**: Add, Edit, Delete, Test Connection

##### Backup Page (`pages/backup.py`)
- **Create Backup**:
  - Editor selection checkboxes
  - Description text field
  - Create button with progress
- **Restore Section**:
  - Backup list with timestamps
  - Preview dialog before restore
  - Progress bar during restore

##### Discovery Page (`pages/discovery.py`)
- **Animation**: Radar-style scanning animation
- **Progress**: Linear progress bar
- **Results**: Card grid of found configurations
- **Actions**: Import selected, Import all

### Backend Integration

#### Threading Model
```python
class AsyncWorker(QThread):
    """Base class for async operations"""
    progress = Signal(int)
    result = Signal(object)
    error = Signal(str)
    
    def __init__(self, manager: MCPManager, operation: str, **kwargs):
        super().__init__()
        self.manager = manager
        self.operation = operation
        self.kwargs = kwargs
```

#### Manager Integration
- Import `MCPManager` from `mcpcommander.core.manager`
- Use existing schemas from `mcpcommander.schemas`
- Leverage error classes from `mcpcommander.utils.errors`
- Maintain same validation logic

### Launch Integration

#### CLI Command
```python
# In cli/main.py
@app.command()
def gui(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable debug logging"),
) -> None:
    """Launch the graphical user interface."""
    try:
        from mcpcommander.gui.app import launch_gui
        launch_gui(verbose=verbose)
    except ImportError:
        print("GUI dependencies not installed. Install with: pip install mcp-commander[gui]")
```

### Testing Strategy

#### Unit Tests
- Test each custom widget independently
- Mock backend calls
- Verify signal/slot connections

#### Integration Tests  
- Test page-to-backend communication
- Verify async operations
- Test error handling

#### UI Tests
```python
# tests/gui/test_main_window.py
def test_sidebar_navigation(qtbot):
    """Test sidebar page switching"""
    window = MainWindow()
    qtbot.addWidget(window)
    
    # Click servers item
    qtbot.mouseClick(window.sidebar.items[1], Qt.LeftButton)
    assert window.content_stack.currentIndex() == 1
```

### Installation & Dependencies

#### Required Packages
```toml
[project.optional-dependencies]
gui = [
    "PySide6>=6.5.0",
    "qasync>=0.27.0",  # Async Qt support
    "Pillow>=10.0.0",  # Image processing
]
```

#### Installation Command
```bash
# Install with GUI support
pip install mcp-commander[gui]

# Or for development
pip install -e ".[gui,dev]"
```

### Development Guidelines

#### Code Organization
1. Each page inherits from `BasePage` class
2. Custom widgets emit signals for actions
3. Pages connect to signals and call backend
4. Async operations use QThread workers
5. All strings in constants for i18n readiness

#### State Management
- Application state in `MainWindow`
- Page state local to each page
- Settings persisted via QSettings
- Backend state via MCPManager

#### Error Handling
```python
def handle_operation(self):
    try:
        result = self.manager.operation()
        self.show_success(f"Operation completed: {result}")
    except MCPCommanderError as e:
        self.show_error(f"Operation failed: {e}")
    except Exception as e:
        self.show_error(f"Unexpected error: {e}")
        logger.exception("Unexpected error in operation")
```

### Performance Considerations

#### Optimization Guidelines
1. **Lazy Loading**: Load pages on first access
2. **Virtual Lists**: Use QListView for large datasets
3. **Debouncing**: Debounce search inputs (300ms)
4. **Caching**: Cache discovery results for 5 minutes
5. **Threading**: All I/O operations in QThread

#### Memory Management
- Properly parent all widgets
- Disconnect signals when destroying widgets
- Clear data models when switching pages
- Use deleteLater() for dynamic widgets

### Future Enhancements

#### Planned Features
1. **Themes**: Light theme option
2. **Plugins**: Extension system for custom pages
3. **Export**: Export configurations to file
4. **Import**: Bulk import from file
5. **Profiles**: Multiple configuration profiles
6. **Hotkeys**: Global hotkeys for quick access
7. **Update Check**: Auto-update notifications
8. **Telemetry**: Optional usage analytics

### Troubleshooting

#### Common Issues
1. **High DPI**: Set QT_SCALE_FACTOR environment variable
2. **Font Issues**: Install system fonts package
3. **Dark Theme**: Ensure OS dark mode is enabled
4. **Performance**: Disable animations on older systems

### Resources & Attribution

#### PyOneDark Theme
- Original by: Wanderson M. Pimenta
- License: MIT
- Repository: https://github.com/Wanderson-Magalhaes/PyOneDark_Qt_Widgets_Modern_GUI
- Attribution: Must maintain copyright notice in theme files

#### Icons
- Material Design Icons (Apache 2.0)
- Customize colors to match theme

---
*GUI Implementation added: 2025-01-20*
*Based on PyOneDark theme with MIT license*
- Please also observe the LICENSE for the PySide6 interface repository and use it while respecting the LICENSE requirements.