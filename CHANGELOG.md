# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.2] - 2025-08-13

### Fixed
- **Command Parsing Bug**: Fixed issue where paths containing spaces were incorrectly split during server configuration parsing
  - Replaced regex-based parsing with `shlex.split()` for proper shell-style command parsing
  - Commands with quoted paths (e.g., `"/Applications/Burp Suite Community Edition.app/..."`) now parse correctly
  - Added fallback to regex parsing if shlex fails for edge cases
  - Example: Burp Suite MCP proxy server commands now work properly

### Technical Improvements
- **Improved Command Parser**: Enhanced `ServerConfigParser._split_command()` method in `src/mcpcommander/utils/config_parser.py`
- **Better Error Handling**: Added warning logging for command parsing fallbacks
- **Shell Compatibility**: Commands now parse using shell-like semantics with proper quote handling

## [0.1.1] - 2025-08-12

### Added
- **Environment Variable Support**: New `--from-env` and `--env` options for the `add` and `add-all` commands
  - `--from-env`: Copy environment variables from current environment (e.g., `--from-env=MCP_LOG_LEVEL,GIT_SIGN_COMMITS`)
  - `--env`: Set explicit environment variables with KEY:value format (e.g., `--env=DEBUG:true --env=API_KEY:secret123`)
  - Smart merging: CLI options override existing environment variables in server configurations
  - Warning messages for missing environment variables when using `--from-env`
- **Enhanced CLI Functionality**: New `mcp help` command as an alias to `mcp --help`
- **Global Verbose Mode**: Support for `MCP_COMMANDER_VERBOSE` environment variable
  - Accepts values: `1`, `true`, or `"true"` (case-insensitive) to enable verbose mode globally
  - Works in combination with `-v/--verbose` flags

### Changed
- **Code Quality Infrastructure**: Replaced Black + isort + flake8 with Ruff for unified linting and formatting
  - Faster builds and consistent code style
  - Updated README badge to reflect Ruff usage
  - Simplified development dependencies
- **Type Safety**: Enhanced type annotations with proper handling of built-in types to avoid MyPy conflicts
- **CLI Help System**: Improved help display and command discovery

### Technical Improvements
- **Enhanced Server Configuration Parsing**: Extended to support environment variable injection
- **Better Error Handling**: More descriptive error messages for environment variable parsing failures
- **Test Coverage**: All new functionality covered by existing test suite (maintained 38%+ coverage)

### Usage Examples
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

# Use new help alias
mcp help  # Same as mcp --help
```

### Configuration Output
Generated server configurations now include environment variables:
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

## [0.1.0] - 2025-08-11

### Added
- **Complete MCP Server Management System**: Cross-platform command-line tool for managing MCP (Model Context Protocol) servers
- **Multi-Transport Support**: Support for all MCP transport types:
  - STDIO servers (traditional command-based)
  - HTTP servers with host, port, and path configuration
  - WebSocket servers with URL and headers support
  - Server-Sent Events (SSE) with URL and headers support
- **Cross-Platform Configuration Management**:
  - Automatic user config directory detection (Windows: `%APPDATA%`, macOS: `~/Library/Application Support`, Linux: `~/.config`)
  - Legacy configuration migration from repository to user directories
  - Schema validation with Pydantic models
- **Editor Support**: Built-in support for multiple code editors:
  - Claude Code CLI (`~/.claude.json`)
  - Claude Desktop (`~/Library/Application Support/Claude/claude_desktop_config.json`)
  - Cursor (`~/Library/Application Support/Cursor/User/globalStorage/storage.json`)
  - VS Code with configurable paths and JSONPath support
  - Windsurf editor support
- **Modern CLI Interface**:
  - Built with Typer framework and Rich formatting
  - Contextual help system with `--help --verbose` showing practical examples
  - Colored output and progress indicators
  - Comprehensive error messages with suggestions
- **Advanced Server Discovery**: Automatic detection of existing MCP server configurations across all supported editors
- **Comprehensive Testing Suite**:
  - 43+ unit tests with 85%+ coverage requirement
  - Integration tests for cross-platform compatibility
  - End-to-end workflow testing
  - Mock frameworks for safe testing
- **Enterprise-Grade Development Infrastructure**:
  - Modern Python packaging with `pyproject.toml` (PEP 517/518/621)
  - Pre-commit hooks for code quality (15+ hooks including linting, formatting, security)
  - GitHub Actions CI/CD pipelines for testing and PyPI publishing
  - Comprehensive type hints with mypy validation
  - Structured logging with configurable levels
  - Cross-platform path handling and file operations
- **Developer Experience**:
  - Rich console output with tables and formatting
  - Detailed error messages with context and suggestions
  - Comprehensive API documentation with examples
  - Contributing guidelines and development setup

### Changed
- **Architecture**: Complete transformation from monolithic script to enterprise-grade Python package with proper module structure
- **Configuration Format**: Enhanced to support all transport types while maintaining backward compatibility
- **CLI Interface**: Upgraded from basic argparse to modern Typer framework with Rich formatting
- **Error Handling**: Centralized exception hierarchy with context-aware error messages
- **Testing**: Professional test suite replacing basic validation

### Technical Details
- **Python Support**: Requires Python 3.12+
- **Dependencies**: Minimal core dependencies (colorama, pydantic, typer, rich)
- **Packaging**: Modern setuptools with automated PyPI publishing via trusted publishing
- **Code Quality**: Black formatting, Ruff linting, MyPy type checking, Bandit security scanning
- **Development**: Pre-commit hooks, GitHub Actions, comprehensive test coverage

### Usage Examples
```bash
# Add server to all editors
mcp add my-server "npx @modelcontextprotocol/server-filesystem /tmp"

# Add HTTP server to specific editor
mcp add web-server '{"transport": {"type": "http", "host": "localhost", "port": 8080}}' claude-code

# List all configured servers
mcp list

# Remove server from specific editor
mcp remove my-server cursor

# Show detailed help with examples
mcp add --help --verbose
```

[Unreleased]: https://github.com/nmindz/mcp-commander/compare/v0.1.2...HEAD
[0.1.2]: https://github.com/nmindz/mcp-commander/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/nmindz/mcp-commander/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/nmindz/mcp-commander/releases/tag/v0.1.0
