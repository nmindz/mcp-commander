"""Backup and restore functionality for MCP configurations."""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from mcpcommander.schemas.config_schema import BackupConfig, BackupInfo, EditorConfig
from mcpcommander.utils.errors import BackupError, ConfigurationError
from mcpcommander.utils.logger import get_logger

logger = get_logger(__name__)


class BackupManager:
    """Manages backup and restore operations for MCP configurations."""

    def __init__(self, config_path: Path) -> None:
        """Initialize backup manager.
        
        Args:
            config_path: Path to the main mcp-commander config file
        """
        self.config_path = config_path
        self.backup_dir = config_path.parent / "backups"
        self.backup_config_path = self.backup_dir / "backup_config.json"
        self._ensure_backup_directory()
        
    def _ensure_backup_directory(self) -> None:
        """Ensure backup directory exists."""
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Backup directory: {self.backup_dir}")

    def _get_backup_config(self) -> BackupConfig:
        """Load or create backup configuration."""
        if not self.backup_config_path.exists():
            # Create default backup config
            config = BackupConfig()
            self._save_backup_config(config)
            return config
            
        try:
            with open(self.backup_config_path) as f:
                data = json.load(f)
            
            # Parse datetime strings back to datetime objects
            for backup in data.get('backups', []):
                if 'timestamp' in backup and isinstance(backup['timestamp'], str):
                    backup['timestamp'] = datetime.fromisoformat(backup['timestamp'])
                    
            return BackupConfig(**data)
        except Exception as e:
            logger.warning(f"Invalid backup config, creating new: {e}")
            config = BackupConfig()
            self._save_backup_config(config)
            return config

    def _save_backup_config(self, config: BackupConfig) -> None:
        """Save backup configuration."""
        try:
            with open(self.backup_config_path, "w") as f:
                # Convert the config to dict with proper datetime handling
                config_data = config.model_dump()
                
                # Convert datetime objects to strings for JSON serialization
                for backup in config_data.get('backups', []):
                    if 'timestamp' in backup and hasattr(backup['timestamp'], 'isoformat'):
                        backup['timestamp'] = backup['timestamp'].isoformat()
                    elif 'timestamp' in backup and isinstance(backup['timestamp'], str):
                        # Already a string, keep as is
                        pass
                
                json.dump(config_data, f, indent=2)
        except Exception as e:
            raise BackupError(f"Failed to save backup configuration: {e}") from e

    def create_backup(
        self,
        editor_configs: dict[str, EditorConfig] | None = None,
        editor_name: str | None = None,
        description: str | None = None
    ) -> BackupInfo:
        """Create a backup of MCP configurations.
        
        Args:
            editor_configs: Dict of all editor configurations (for all editors backup)
            editor_name: Specific editor name to backup (for single editor backup)
            description: Optional description for the backup
            
        Returns:
            BackupInfo: Information about the created backup
        """
        timestamp = datetime.now()
        backup_id = timestamp.strftime("%Y%m%d_%H%M%S")
        
        if editor_name:
            backup_id = f"{editor_name}_{backup_id}"
            
        backup_info = BackupInfo(
            backup_id=backup_id,
            timestamp=timestamp,
            editor_name=editor_name,
            description=description or f"Backup created at {timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        # Create backup subdirectory
        backup_path = self.backup_dir / backup_id
        backup_path.mkdir(exist_ok=True)
        
        try:
            if editor_name:
                # Backup single editor
                if not editor_configs or editor_name not in editor_configs:
                    raise BackupError(f"Editor '{editor_name}' not found in configurations")
                    
                self._backup_single_editor(editor_configs[editor_name], backup_path, editor_name)
                backup_info.files_backed_up = [editor_name]
            else:
                # Backup all editors
                if not editor_configs:
                    raise BackupError("No editor configurations provided for backup")
                    
                files_backed_up = []
                for name, config in editor_configs.items():
                    try:
                        self._backup_single_editor(config, backup_path, name)
                        files_backed_up.append(name)
                    except Exception as e:
                        logger.warning(f"Failed to backup {name}: {e}")
                        
                backup_info.files_backed_up = files_backed_up
                
            # Save backup metadata
            backup_info_path = backup_path / "backup_info.json"
            with open(backup_info_path, "w") as f:
                # Convert datetime to string for JSON serialization
                backup_data = backup_info.model_dump()
                backup_data['timestamp'] = backup_info.timestamp.isoformat()
                json.dump(backup_data, f, indent=2)
                
            # Update backup registry
            self._add_to_backup_registry(backup_info)
            
            # Clean up old backups if needed
            self._cleanup_old_backups()
            
            logger.info(f"Created backup: {backup_id}")
            return backup_info
            
        except Exception as e:
            # Cleanup failed backup
            if backup_path.exists():
                shutil.rmtree(backup_path, ignore_errors=True)
            raise BackupError(f"Failed to create backup: {e}") from e

    def _backup_single_editor(self, editor_config: EditorConfig, backup_path: Path, editor_name: str) -> None:
        """Backup a single editor configuration.
        
        Args:
            editor_config: Editor configuration to backup
            backup_path: Path to backup directory
            editor_name: Name of the editor
        """
        config_path = Path(editor_config.config_path).expanduser()
        
        if not config_path.exists():
            logger.warning(f"Config file does not exist: {config_path}")
            return
            
        # Create backup filename
        backup_filename = f"{editor_name}_config.json"
        backup_file_path = backup_path / backup_filename
        
        try:
            # Copy the configuration file
            shutil.copy2(config_path, backup_file_path)
            
            # Also save editor metadata
            metadata = {
                "editor_name": editor_name,
                "original_path": str(config_path),
                "jsonpath": editor_config.jsonpath,
                "backup_timestamp": datetime.now().isoformat()
            }
            
            metadata_path = backup_path / f"{editor_name}_metadata.json"
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)
                
            logger.debug(f"Backed up {editor_name} config from {config_path}")
            
        except Exception as e:
            raise BackupError(f"Failed to backup {editor_name}: {e}") from e

    def _add_to_backup_registry(self, backup_info: BackupInfo) -> None:
        """Add backup info to the registry."""
        config = self._get_backup_config()
        config.backups.append(backup_info)
        
        # Sort by timestamp (newest first)
        config.backups.sort(key=lambda x: x.timestamp, reverse=True)
        
        self._save_backup_config(config)

    def _cleanup_old_backups(self) -> None:
        """Remove old backups beyond the maximum count."""
        config = self._get_backup_config()
        
        if len(config.backups) <= config.max_backups:
            return
            
        # Remove excess backups (keep newest ones)
        backups_to_remove = config.backups[config.max_backups:]
        
        for backup in backups_to_remove:
            backup_path = self.backup_dir / backup.backup_id
            if backup_path.exists():
                try:
                    shutil.rmtree(backup_path)
                    logger.debug(f"Removed old backup: {backup.backup_id}")
                except Exception as e:
                    logger.warning(f"Failed to remove old backup {backup.backup_id}: {e}")
                    
        # Update registry
        config.backups = config.backups[:config.max_backups]
        self._save_backup_config(config)

    def list_backups(self, editor_name: str | None = None) -> list[BackupInfo]:
        """List available backups.
        
        Args:
            editor_name: Filter by specific editor name
            
        Returns:
            List of backup information, sorted by timestamp (newest first)
        """
        config = self._get_backup_config()
        
        if editor_name:
            return [b for b in config.backups if b.editor_name == editor_name]
        else:
            return config.backups

    def restore_backup(
        self,
        backup_id: str,
        editor_configs: dict[str, EditorConfig] | None = None,
        force: bool = False
    ) -> dict[str, str]:
        """Restore a backup.
        
        Args:
            backup_id: ID of the backup to restore
            editor_configs: Current editor configurations for validation
            force: Skip confirmation prompts
            
        Returns:
            Dict mapping editor names to restore status messages
        """
        config = self._get_backup_config()
        
        # Find backup info
        backup_info = None
        for backup in config.backups:
            if backup.backup_id == backup_id:
                backup_info = backup
                break
                
        if not backup_info:
            raise BackupError(f"Backup not found: {backup_id}")
            
        backup_path = self.backup_dir / backup_id
        if not backup_path.exists():
            raise BackupError(f"Backup directory not found: {backup_path}")
            
        results = {}
        
        try:
            for editor_name in backup_info.files_backed_up:
                result = self._restore_single_editor(
                    backup_path, editor_name, editor_configs, force
                )
                results[editor_name] = result
                
            logger.info(f"Restored backup: {backup_id}")
            return results
            
        except Exception as e:
            raise BackupError(f"Failed to restore backup {backup_id}: {e}") from e

    def _restore_single_editor(
        self,
        backup_path: Path,
        editor_name: str,
        editor_configs: dict[str, EditorConfig] | None,
        force: bool
    ) -> str:
        """Restore a single editor configuration.
        
        Args:
            backup_path: Path to the backup directory
            editor_name: Name of the editor to restore
            editor_configs: Current editor configurations
            force: Skip validation checks
            
        Returns:
            Status message for the restore operation
        """
        backup_file = backup_path / f"{editor_name}_config.json"
        metadata_file = backup_path / f"{editor_name}_metadata.json"
        
        if not backup_file.exists():
            return f"❌ No backup file found for {editor_name}"
            
        try:
            # Load metadata
            metadata = {}
            if metadata_file.exists():
                with open(metadata_file) as f:
                    metadata = json.load(f)
                    
            # Determine target path
            if editor_configs and editor_name in editor_configs:
                # Use current configuration path
                target_path = Path(editor_configs[editor_name].config_path).expanduser()
            elif metadata and "original_path" in metadata:
                # Use original path from metadata
                target_path = Path(metadata["original_path"]).expanduser()
            else:
                return f"❌ Cannot determine target path for {editor_name}"
                
            # Create directory if needed
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Backup existing file if it exists
            if target_path.exists() and not force:
                backup_existing = target_path.with_suffix(f"{target_path.suffix}.pre_restore")
                shutil.copy2(target_path, backup_existing)
                
            # Copy backup file to target location
            shutil.copy2(backup_file, target_path)
            
            logger.debug(f"Restored {editor_name} config to {target_path}")
            return f"✅ Successfully restored to {target_path}"
            
        except Exception as e:
            logger.error(f"Failed to restore {editor_name}: {e}")
            return f"❌ Failed to restore {editor_name}: {e}"

    def delete_backup(self, backup_id: str) -> None:
        """Delete a backup.
        
        Args:
            backup_id: ID of the backup to delete
        """
        config = self._get_backup_config()
        
        # Find and remove from registry
        backup_info = None
        for i, backup in enumerate(config.backups):
            if backup.backup_id == backup_id:
                backup_info = config.backups.pop(i)
                break
                
        if not backup_info:
            raise BackupError(f"Backup not found: {backup_id}")
            
        # Remove backup directory
        backup_path = self.backup_dir / backup_id
        if backup_path.exists():
            try:
                shutil.rmtree(backup_path)
            except Exception as e:
                raise BackupError(f"Failed to delete backup directory: {e}") from e
                
        # Save updated registry
        self._save_backup_config(config)
        
        logger.info(f"Deleted backup: {backup_id}")

    def get_backup_info(self, backup_id: str) -> BackupInfo | None:
        """Get detailed information about a backup.
        
        Args:
            backup_id: ID of the backup
            
        Returns:
            BackupInfo if found, None otherwise
        """
        config = self._get_backup_config()
        
        for backup in config.backups:
            if backup.backup_id == backup_id:
                return backup
                
        return None

    def set_max_backups(self, max_backups: int) -> None:
        """Set the maximum number of backups to keep.
        
        Args:
            max_backups: Maximum number of backups (must be >= 1)
        """
        if max_backups < 1:
            raise ConfigurationError("Maximum backups must be at least 1")
            
        config = self._get_backup_config()
        config.max_backups = max_backups
        self._save_backup_config(config)
        
        # Clean up if necessary
        self._cleanup_old_backups()
        
        logger.info(f"Set maximum backups to {max_backups}")

    def get_backup_stats(self) -> dict[str, Any]:
        """Get backup statistics.
        
        Returns:
            Dictionary with backup statistics
        """
        config = self._get_backup_config()
        
        total_size = 0
        editor_counts = {}
        
        for backup in config.backups:
            # Calculate backup size
            backup_path = self.backup_dir / backup.backup_id
            if backup_path.exists():
                for file in backup_path.rglob("*"):
                    if file.is_file():
                        total_size += file.stat().st_size
                        
            # Count by editor
            if backup.editor_name:
                editor_counts[backup.editor_name] = editor_counts.get(backup.editor_name, 0) + 1
            else:
                # All-editors backup
                for editor in backup.files_backed_up:
                    editor_counts[editor] = editor_counts.get(editor, 0) + 1
                    
        return {
            "total_backups": len(config.backups),
            "max_backups": config.max_backups,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "backup_directory": str(self.backup_dir),
            "editor_counts": editor_counts,
            "oldest_backup": config.backups[-1].timestamp if config.backups else None,
            "newest_backup": config.backups[0].timestamp if config.backups else None
        }