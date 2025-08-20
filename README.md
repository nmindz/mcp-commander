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
  [![CLI Commands](https://img.shields.io/badge/CLI%20Commands-15-blue.svg)](#-commands)
  [![Type Checking](https://img.shields.io/badge/mypy-enabled-blue.svg)](https://mypy-lang.org/)

</div>

> **⚠️ BREAKING CHANGES in v1.0.0**: CLI commands have been restructured! See [Migration Guide](#-whats-new-in-v100---major-cli-restructure) below.

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
PYTHONPATH="src:$PYTHONPATH" python -m mcpcommander config show
```

### Requirements
- Python 3.12 or higher
- Works on macOS, Windows, and Linux

## 💡 Getting Help

### Contextual Examples
Use `--help` to see detailed help with practical examples for any command:
```bash
# Show complete help with examples (default behavior)
mcp add --help
mcp add editor --help
mcp config show --help

# Alternative help syntax
mcp add help
mcp remove help
mcp backup help

# Enable debug output with verbose flag
mcp add server myserver "command" --verbose
mcp config servers --verbose
```

### Configuration Examples
View all transport configuration examples:
```bash
# Show all transport examples
mcp examples

# Show examples with usage instructions
mcp examples
```

## 💻 Commands

### 🔍 Discovery and Status
```bash
# Discover all MCP configurations on your system
mcp discover

# Check status of all editor configurations
mcp config show

# List available editors
mcp editors
```

### ⚙️ Configuration Management
```bash
# Show configuration status and editor overview
mcp config show

# List all configured MCP servers
mcp config servers

# List servers for specific editor
mcp config servers claude-code

# Show absolute path to configuration file
mcp config path

# Reset configuration to empty state (with confirmation)
mcp config reset

# Reset configuration and remove all backups
mcp config reset --include-backups

# Reset without confirmation prompts
mcp config reset --force
```

### 📝 Server Management
```bash
# Add server to specific editor
mcp add server myserver "npx @modelcontextprotocol/server-filesystem /tmp" claude-code

# Add server to all discovered editors (replaces add-all)
mcp add server myserver "npx @modelcontextprotocol/server-filesystem /tmp" --all

# Remove server from editors
mcp remove server myserver

# Remove server from specific editor  
mcp remove server myserver claude-code
```

### 🌍 Environment Variable Support
```bash
# Copy environment variables from current environment
export MCP_LOG_LEVEL=info
export GIT_SIGN_COMMITS=false
mcp add server git-server "npx @cyanheads/git-mcp-server" --from-env=MCP_LOG_LEVEL,GIT_SIGN_COMMITS

# Set explicit environment variables
mcp add server api-server "npx my-api-server" --env=DEBUG:true --env=API_KEY:secret123

# Combine both approaches
mcp add server hybrid-server "npx server" --from-env=LOG_LEVEL --env=CUSTOM_VAR:custom_value

# Use with JSON configuration (merges environment variables)
mcp add server json-server '{"command": "npx", "args": ["server"], "env": {"EXISTING": "value"}}' --env=NEW_VAR:added

# Global verbose mode via environment variable
export MCP_COMMANDER_VERBOSE=1
mcp config servers  # Will run in verbose mode automatically
```

### 🎛️ Editor Management
```bash
# Add support for custom editor
mcp add editor my-editor "/path/to/config.json"

# Add editor with custom JSONPath
mcp add editor my-editor "/path/to/config.json" --jsonpath="servers"

# Remove editor support
mcp remove editor my-editor

# List available editors
mcp editors
```

### 💾 Backup Management
```bash
# Create backup of all configurations
mcp backup create

# Create backup of specific editor
mcp backup create claude-code --description "Before update"

# List all backups
mcp backup list

# List backups for specific editor
mcp backup list claude-code

# Restore backup (interactive selection)
mcp backup restore

# Restore specific backup
mcp backup restore backup-id-123

# Delete backup (interactive selection)
mcp backup delete

# Configure backup settings
mcp backup config --max-backups 20
mcp backup config --show
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
mcp add server myserver "npx @modelcontextprotocol/server-filesystem /tmp" --all

# Works with JSON configurations too
mcp add server myserver '{"command": "npx", "args": ["-y", "@modelcontextprotocol/server-memory"]}' --all

# Get help for add commands
mcp add help
mcp add server help
```

### 🗑️ Server Removal
```bash
# Remove server from all configured editors
mcp remove server myserver

# Remove server from specific editor
mcp remove server myserver cursor

# Get help for remove commands
mcp remove help
mcp remove server help
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
mcp add server jira-mcp "~/Projects/me/jira-mcp/server.py" --all

# List all configured servers
mcp config servers

# Remove from just Cursor
mcp remove server jira-mcp cursor

# Check what's configured
mcp config show
```

### Adding a server with complex configuration

```bash
mcp add server filesystem '{"command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem", "~/Documents"]}'
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

## 🚀 What's New in v1.0.0 - Major CLI Restructure

### 🔄 **BREAKING CHANGES - CLI Restructure**
**MCP Commander v1.0.0 introduces a major CLI restructuring for better organization and usability.**

#### **🆕 New `mcp config` Command Group**
All MCP Commander configuration management is now under the `mcp config` subcommand:

| **OLD Command** | **NEW Command** | **Description** |
|-----------------|-----------------|-----------------|
| `mcp list` | `mcp config servers` | List configured MCP servers |
| `mcp status` | `mcp config show` | Show configuration status |  
| `mcp selfdestruct` | `mcp config reset` | Reset configuration to empty state |
| *(new)* | `mcp config path` | Show configuration file path |

#### **✨ What's Improved**
- **Better Organization**: Configuration commands logically grouped under `mcp config`
- **Clearer Intent**: Commands clearly indicate they manage MCP Commander's own configuration
- **Enhanced Help**: Each subcommand group has comprehensive help and examples
- **Consistent Structure**: Follows modern CLI patterns for better discoverability

#### **🔄 Migration Path**
**All old commands still work in this version but will be removed in v1.1.0:**

```bash
# OLD (still works but deprecated)
mcp list                    # ⚠️ Will be removed in v1.1.0
mcp status                  # ⚠️ Will be removed in v1.1.0  
mcp selfdestruct            # ⚠️ Will be removed in v1.1.0

# NEW (recommended - use these now!)
mcp config servers          # ✅ List servers
mcp config show             # ✅ Show status
mcp config reset            # ✅ Reset configuration
mcp config path             # ✅ Show config path (new!)
```

### 🎯 **Enhanced Configuration Management**
- **New `mcp config path`**: Shows absolute path to configuration file
- **Improved `mcp config show`**: Better status formatting with comprehensive editor overview
- **Enhanced `mcp config reset`**: Safer reset process with clear confirmations
- **Better Help System**: Each config subcommand has detailed help with examples

### 📦 **Production Ready - v1.0.0**
- **Stable API**: CLI interface is now stable and production-ready  
- **Semantic Versioning**: Following strict semantic versioning from v1.0.0
- **Comprehensive Testing**: Full test coverage for all CLI commands
- **Type Safety**: Complete type hints and mypy validation

## 🔄 Previous Version Features (Still Available)

### 🔍 **Auto-Discovery System**
- Automatically finds all MCP configurations on your system  
- Supports Claude Code, Claude Desktop, Cursor, VS Code, Windsurf, and more
- Cross-platform detection (macOS, Windows, Linux)

### 🌍 **Add-All Command**
```bash
# One command to rule them all!
mcp add server my-server "npx @modelcontextprotocol/server-filesystem /tmp" --all
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
- **JSON validation errors**: Use `mcp config show` to check configuration file integrity
- **Server conflicts**: Use `mcp config servers` to see existing servers before adding new ones

### Debug Mode
```bash
# Enable debug output with verbose flag
mcp add server myserver "command" --all --verbose
mcp config servers --verbose
```

### Getting Help
```bash
# Comprehensive help for any command
mcp --help
mcp add --help
mcp add server --help
mcp backup --help
```
