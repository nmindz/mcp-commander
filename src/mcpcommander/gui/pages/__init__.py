"""GUI pages package."""

from mcpcommander.gui.pages.dashboard import DashboardPage
from mcpcommander.gui.pages.servers import ServersPage
from mcpcommander.gui.pages.editors import EditorsPage
from mcpcommander.gui.pages.backup import BackupPage
from mcpcommander.gui.pages.discovery import DiscoveryPage
from mcpcommander.gui.pages.status import StatusPage
from mcpcommander.gui.pages.settings import SettingsPage

__all__ = [
    "DashboardPage",
    "ServersPage",
    "EditorsPage",
    "BackupPage",
    "DiscoveryPage",
    "StatusPage",
    "SettingsPage",
]