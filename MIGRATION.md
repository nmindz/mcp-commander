# MCP Commander v1.0.0 Migration Guide

## ⚠️ Breaking Changes Overview

MCP Commander v1.0.0 introduces a **major CLI restructuring** with breaking changes. This guide helps you migrate from v0.x to v1.0.0.

## 🚨 Removed Commands

The following commands have been **completely removed** and will cause errors:

| **Removed Command** | **Error in v1.0.0+** |
|--------------------|-----------------------|
| `mcp list` | ❌ Command not found |
| `mcp status` | ❌ Command not found |
| `mcp selfdestruct` | ❌ Command not found |

## ✅ New Commands

All configuration management is now under the `mcp config` subcommand:

| **Old Command** | **New Command** | **Purpose** |
|-----------------|-----------------|-------------|
| `mcp list` | `mcp config servers` | List configured MCP servers |
| `mcp status` | `mcp config show` | Show configuration status |
| `mcp selfdestruct` | `mcp config reset` | Reset configuration |
| *(new)* | `mcp config path` | Show config file path |

## 🔄 Step-by-Step Migration

### 1. Update Your Scripts

**Before (v0.x):**
```bash
#!/bin/bash
# This will FAIL in v1.0.0+
mcp list
mcp status
mcp selfdestruct --force
```

**After (v1.0.0+):**
```bash
#!/bin/bash  
# Updated commands for v1.0.0+
mcp config servers
mcp config show
mcp config reset --force
```

### 2. Update Your Aliases

**Before (v0.x):**
```bash
# ~/.bashrc or ~/.zshrc
alias mcplist='mcp list'
alias mcpstatus='mcp status'
alias mcpreset='mcp selfdestruct'
```

**After (v1.0.0+):**
```bash
# ~/.bashrc or ~/.zshrc
alias mcplist='mcp config servers'
alias mcpstatus='mcp config show'
alias mcpreset='mcp config reset'
```

### 3. Update Documentation & READMEs

Search your documentation for old command references:

```bash
# Find old references
grep -r "mcp list\|mcp status\|mcp selfdestruct" docs/

# Update them to new commands
# mcp list → mcp config servers
# mcp status → mcp config show  
# mcp selfdestruct → mcp config reset
```

## 🆕 New Features in v1.0.0

### Enhanced Configuration Management

```bash
# New: Show absolute path to config file
mcp config path

# Improved: Better status display with rich formatting
mcp config show

# Enhanced: List servers with optional editor filter
mcp config servers
mcp config servers claude-code

# Safer: Reset with better confirmation prompts
mcp config reset
mcp config reset --include-backups --force
```

### Better Help System

```bash
# Comprehensive config help
mcp config --help
mcp config help

# Individual command help
mcp config servers --help
mcp config show --help
mcp config reset --help
mcp config path --help
```

## 🔧 Testing Your Migration

### 1. Verify Version
```bash
mcp version
# Should show: MCP Commander version 1.0.0
```

### 2. Test New Commands
```bash
# Test each new command
mcp config path        # Should show config file path
mcp config show        # Should show status
mcp config servers     # Should list servers
mcp config --help      # Should show config help
```

### 3. Confirm Old Commands Fail
```bash
# These should ALL fail with "command not found"
mcp list          # ❌ Should fail
mcp status        # ❌ Should fail  
mcp selfdestruct  # ❌ Should fail
```

## 🚀 Unchanged Commands

These commands work exactly the same:

```bash
# Server management (unchanged)
mcp add server name "command" --all
mcp remove server name
mcp discover
mcp editors
mcp examples

# Backup management (unchanged)
mcp backup create
mcp backup restore
mcp backup list
mcp backup delete

# Editor management (unchanged)
mcp add editor name path
mcp remove editor name

# Utility commands (unchanged)
mcp version
mcp help
```

## 📋 Migration Checklist

- [ ] Update all scripts using `mcp list` → `mcp config servers`
- [ ] Update all scripts using `mcp status` → `mcp config show`
- [ ] Update all scripts using `mcp selfdestruct` → `mcp config reset`
- [ ] Update shell aliases and functions
- [ ] Update documentation and README files
- [ ] Update CI/CD pipelines
- [ ] Test all updated scripts
- [ ] Train team members on new commands
- [ ] Update monitoring/automation tools

## 🆘 Troubleshooting

### Common Errors

**Error:** `mcp: 'list' is not a mcp command`
```bash
# Fix: Use new config subcommand
mcp config servers
```

**Error:** `mcp: 'status' is not a mcp command`
```bash  
# Fix: Use new config subcommand
mcp config show
```

**Error:** `mcp: 'selfdestruct' is not a mcp command`
```bash
# Fix: Use new config subcommand
mcp config reset
```

### Getting Help

```bash
# Show all available commands
mcp --help

# Show config subcommands
mcp config --help

# Show help for specific command
mcp config servers --help
```

## 📞 Support

- **Issues**: https://github.com/nmindz/mcp-commander/issues
- **Discussions**: https://github.com/nmindz/mcp-commander/discussions
- **Documentation**: https://github.com/nmindz/mcp-commander#readme

---

**Need help with migration?** Open an issue with the `migration` label and we'll help you update your setup.