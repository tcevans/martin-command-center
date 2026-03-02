from dataclasses import dataclass
from pathlib import Path
from typing import List

@dataclass
class Config:
    """Dashboard configuration."""
    
    # Refresh
    REFRESH_INTERVAL: int = 30  # seconds
    
    # Paths
    SESSION_STATE_PATH: Path = Path(
        "~/.openclaw/workspace-project-manager/SESSION-STATE.md"
    ).expanduser()
    
    # GitHub
    GITHUB_REPOS: List[str] = None  # Optional: filter by repo
    
    # Display
    MAX_AGENTS_DISPLAY: int = 10
    MAX_EVENTS_DISPLAY: int = 15
    MAX_BLOCKED_DISPLAY: int = 10
    
    # Colors (Textual color names)
    COLOR_SUCCESS: str = "green"
    COLOR_WARNING: str = "yellow"
    COLOR_ERROR: str = "red"
    COLOR_MUTED: str = "dim"
    COLOR_PRIMARY: str = "blue"
    COLOR_SECONDARY: str = "cyan"
    
    def __post_init__(self):
        if self.GITHUB_REPOS is None:
            self.GITHUB_REPOS = []