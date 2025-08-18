<div align="center">
  <img src="logo.png" alt="MCP Commander Logo" width="200" height="200" />

  # MCP Commander

  A convenient command-line tool to manage MCP (Model Context Protocol) servers across different code editors.

  [![PyPI Version](https://img.shields.io/pypi/v/mcp-commander)](https://pypi.org/project/mcp-commander/)
  [![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
  [![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://python.org/)
  [![Code Style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
  [![Pytest](https://img.shields.io/badge/Pytest-8.4-red.svg)](https://pytest.org/)
  [![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](#)
  [![Coverage](https://img.shields.io/badge/coverage-85%25-green.svg)](#)
  [![CLI Commands](https://img.shields.io/badge/CLI%20Commands-13-blue.svg)](#-commands)
  [![Type Checking](https://img.shields.io/badge/mypy-enabled-blue.svg)](https://mypy-lang.org/)

</div>

## 🚀 Features

### Core MCP Operations
- **Multi-Editor Support**: Manage MCP servers for Claude Code, Claude Desktop, Cursor, VS Code, and Windsurf
- **Flexible Server Management**: Add, remove, and list servers across all or specific editors
- **Status Monitoring**: Check configuration file status and server counts
- **Rich CLI Interface**: Colorized output with tables and status indicators

### Advanced Management
- **🔍 Auto-Discovery**: Automatically discover all MCP configurations on your system
- **🌍 Add-All Command**: Install servers to ALL discovered MCP configurations at once
- **📊 Status Dashboard**: Comprehensive status overview of all editor configurations
- **⚙️ Configuration Validation**: Pydantic-based configuration validation and error handling

### Developer Experience
- **Type Safety**: Full type hints and mypy compatibility
- **Error Handling**: Detailed error messages with actionable guidance
- **Extensible**: Easy to add support for new editors and MCP clients
- **Testing**: Comprehensive test coverage with pytest

## 📦 Installation

### Option 1: From PyPI (Recommended)
```bash
# Install globally
pip install mcp-commander

# Or using pipx for isolated installation
pipx install mcp-commander
```

### Option 2: From Git Repository
```bash
# Install directly from GitHub
pip install git+https://github.com/nmindz/mcp-commander.git

# Or clone and install
git clone https://github.com/nmindz/mcp-commander.git
cd mcp-commander
pip install .
```

### Option 3: Development Installation
```bash
git clone https://github.com/nmindz/mcp-commander.git
cd mcp-commander
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

### Option 4: Direct Execution (No Installation Required)
```bash
# Clone repository
git clone https://github.com/nmindz/mcp-commander.git
cd mcp-commander

# Install dependencies only
pip install -r requirements-dev.txt

# Method A: Using run.py script
python run.py --help
python run.py list

# Method B: Using shell wrapper
./mcp.sh --help
./mcp.sh discover

# Method C: Using Python module syntax (cleanest)
PYTHONPATH="src:$PYTHONPATH" python -m mcpcommander --help
PYTHONPATH="src:$PYTHONPATH" python -m mcpcommander status
```

### Requirements
- Python 3.12 or higher
- Works on macOS, Windows, and Linux

## 💡 Getting Help

### Contextual Examples
Use `--help --verbose` (or `--help -v`) to see practical examples for any command:
```bash
# Show detailed help with examples
mcp add --help --verbose
mcp add-editor --help --verbose
mcp status --help --verbose

# Regular help (without examples)
mcp add --help
```

### Configuration Examples
View all transport configuration examples:
```bash
# Show all transport examples
mcp examples

# Show examples with usage instructions
mcp examples --verbose
```

## 💻 Commands

### 🔍 Discovery and Status
```bash
# Discover all MCP configurations on your system
mcp discover

# Check status of all editor configurations
mcp status

# List available editors
mcp editors
```

### 💣 Configuration Reset
```bash
# Reset configuration to empty state (with confirmation)
mcp selfdestruct

# Reset configuration and remove all backups
mcp selfdestruct --include-backups

# Reset without confirmation prompts
mcp selfdestruct --force
```

### 📝 Server Management
```bash
# List all configured servers
mcp list

# List servers for a specific editor
mcp list claude-code

# Add server to specific editor
mcp add myserver "npx @modelcontextprotocol/server-filesystem /tmp" claude-code

# Add server to all configured editors
mcp add myserver "npx @modelcontextprotocol/server-filesystem /tmp"
```

### 🌍 Environment Variable Support
```bash
# Copy environment variables from current environment
export MCP_LOG_LEVEL=info
export GIT_SIGN_COMMITS=false
mcp add git-server "npx @cyanheads/git-mcp-server" --from-env=MCP_LOG_LEVEL,GIT_SIGN_COMMITS

# Set explicit environment variables
mcp add api-server "npx my-api-server" --env=DEBUG:true --env=API_KEY:secret123

# Combine both approaches
mcp add hybrid-server "npx server" --from-env=LOG_LEVEL --env=CUSTOM_VAR:custom_value

# Use with JSON configuration (merges environment variables)
mcp add json-server '{"command": "npx", "args": ["server"], "env": {"EXISTING": "value"}}' --env=NEW_VAR:added

# Global verbose mode via environment variable
export MCP_COMMANDER_VERBOSE=1
mcp list  # Will run in verbose mode automatically
```

#### Generated Configuration
When using environment variables, MCP Commander generates server configurations like this:
```json
{
  "mcpServers": {
    "git-mcp-server": {
      "command": "npx",
      "args": ["@cyanheads/git-mcp-server"],
      "env": {
        "MCP_LOG_LEVEL": "info",
        "GIT_SIGN_COMMITS": "false"
      }
    }
  }
}
```

### 🌍 NEW: Add to All Discovered Configurations
```bash
# Automatically discover and install to ALL MCP configurations
mcp add-all myserver "npx @modelcontextprotocol/server-filesystem /tmp"

# Works with JSON configurations too
mcp add-all myserver '{"command": "npx", "args": ["-y", "@modelcontextprotocol/server-memory"]}'
```

### 🗑️ Server Removal
```bash
# Remove server from all configured editors
mcp remove myserver

# Remove server from specific editor
mcp remove myserver cursor
```

### ℹ️ Help and Version
```bash
# Show help
mcp --help
mcp help  # Same as above

# Show version
mcp version
```

## Configuration

MCP Commander automatically manages its configuration in platform-specific user directories:

- **Windows**: `%APPDATA%/mcpCommander/config.json`
- **macOS**: `~/Library/Application Support/mcpCommander/config.json`
- **Linux**: `~/.config/mcpCommander/config.json`

When you first run any command, mcpCommander will automatically:
1. Create the user config directory
2. Migrate any existing `config.json` from the repository
3. Create a default config if none exists

The configuration defines which editors are supported and where their configuration files are located:

```json
{
  "editors": {
    "claude-code": {
      "config_path": "~/.claude.json",
      "jsonpath": "mcpServers"
    },
    "claude-desktop": {
      "config_path": "~/Library/Application Support/Claude/claude_desktop_config.json",
      "jsonpath": "mcpServers"
    },
    "cursor": {
      "config_path": "~/.cursor/mcp.json",
      "jsonpath": "mcpServers"
    }
  }
}
```

### Adding New Editors

To add support for a new editor, simply add an entry to the `editors` object in `config.json`:

```json
{
  "editors": {
    "new-editor": {
      "config_path": "/path/to/editor/config.json",
      "jsonpath": "mcpServers"
    }
  }
}
```

The `jsonpath` field supports simple dot notation for nested JSON paths (e.g., `"config.mcpServers"`).

## File Structure

```
mcpCommander/
├── config.json          # Editor configuration
├── mcp_manager.py       # Main Python script
├── mcp                  # Shell wrapper script
└── README.md           # This file
```

## Examples

### Managing your JIRA MCP server

```bash
# Add JIRA server to all editors
mcp add jira-mcp "~/Projects/me/jira-mcp/server.py"

# List all configured servers
mcp list

# Remove from just Cursor
mcp remove jira-mcp cursor

# Check what's configured
mcp status
```

### Adding a server with complex configuration

```bash
mcp add filesystem '{"command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem", "~/Documents"]}'
```

## 🛠️ Development

### Local Development Setup
```bash
# Clone the repository
git clone https://github.com/nmindz/mcp-commander.git
cd mcp-commander

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install with development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run linting and formatting
black src/ tests/
flake8 src/ tests/
mypy src/
```

### Project Structure
```
mcp-commander/
├── src/mcpcommander/          # Main package
│   ├── core/                  # Core business logic
│   ├── cli/                   # Command-line interface
│   ├── utils/                 # Utilities and helpers
│   └── schemas/               # Pydantic schemas
├── tests/                     # Test suite
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   └── e2e/                   # End-to-end tests
├── docs/                      # Documentation
└── scripts/                   # Automation scripts
```

### Requirements
- Python 3.12 or higher
- Cross-platform (macOS, Windows, Linux)
- Rich CLI output with colorized formatting

## 🆕 What's New in v0.1.3

### 🪟 **Enhanced Windows Support**
- **Fixed Path Resolution**: Complete fix for Windows path detection
  - No more hardcoded Unix paths like `~/Library/Application Support`
  - Proper Windows environment variables (`%USERPROFILE%`, `%APPDATA%`)
  - All editors now work correctly on Windows

### 💣 **Configuration Reset**
- **New `selfdestruct` Command**: Reset MCP Commander to clean state
  - `mcp selfdestruct`: Reset configuration with confirmation
  - `mcp selfdestruct --include-backups`: Also remove all backups
  - `mcp selfdestruct --force`: Skip confirmation prompts
  - Perfect for testing autodiscovery functionality

### 🎯 **Enhanced Discovery Workflow**
- **Active Configuration Population**: `mcp discover` now updates your config
  - Previously was read-only, now actively populates configuration
  - Complete workflow: `selfdestruct` → `discover` → `status`
  - No more empty config files after discovery

### 🚀 **New Editor Support**
- **Windsurf IDE**: Full support for Codeium's Windsurf editor
  - Cross-platform path detection and configuration
  - Automatic discovery and management

## 🔄 Migration from Previous Versions

### 🔍 **Auto-Discovery System**
- Automatically finds all MCP configurations on your system
- Supports Claude Code, Claude Desktop, Cursor, VS Code, Windsurf, and more
- Cross-platform detection (macOS, Windows, Linux)

### 🌍 **Add-All Command**
```bash
# One command to rule them all!
mcp add-all my-server "npx @modelcontextprotocol/server-filesystem /tmp"
```
- Discovers ALL MCP configurations automatically
- Installs server to every found configuration
- Detailed success/failure reporting with colors

### 📊 **Enhanced CLI Experience**
- Rich table formatting for server listings
- Colorized status indicators (✅❌⚠️)
- Comprehensive error messages with actionable guidance
- Verbose logging options for debugging

### 🏗️ **Modern Architecture**
- Enterprise-grade error handling with custom exceptions
- Type safety with comprehensive type hints
- Extensive test coverage (85%+)
- Modern Python packaging with pyproject.toml

## 🔧 Troubleshooting

### Common Issues
- **Configuration not found**: Run `mcp discover` to see all available MCP configurations
- **Permission errors**: Ensure you have write access to editor configuration directories
- **JSON validation errors**: Use `mcp status` to check configuration file integrity
- **Server conflicts**: Use `mcp list` to see existing servers before adding new ones

### Debug Mode
```bash
# Enable verbose output for debugging
mcp add-all myserver "command" --verbose
mcp list --verbose
```

### Getting Help
```bash
# Comprehensive help for any command
mcp --help
mcp add-all --help
```
