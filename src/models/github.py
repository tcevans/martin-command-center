from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class GitHubEvent:
    """Represents a GitHub activity event."""
    type: str            # "pr", "run", "issue"
    title: str
    status: str          # "open", "closed", "success", "failure", "pending"
    repo: str
    timestamp: datetime
    url: str = ""
    author: str = ""
    number: Optional[int] = None
    
    @property
    def status_icon(self) -> str:
        """Icon based on status."""
        icons = {
            "success": "✓",
            "failure": "✗",
            "pending": "⏳",
            "open": "🔓",
            "closed": "🔒",
            "merged": "🔀"
        }
        return icons.get(self.status, "•")
    
    @property
    def status_color(self) -> str:
        """Color based on status."""
        colors = {
            "success": "text-success",
            "failure": "text-error",
            "pending": "text-warning",
            "open": "text-primary",
            "closed": "text-muted"
        }
        return colors.get(self.status, "white")
    
    @property
    def age_hours(self) -> int:
        """Hours since event."""
        age = datetime.now() - self.timestamp
        return int(age.total_seconds() / 3600)
    
    @property
    def display_title(self) -> str:
        """Title formatted for display."""
        title = self.title
        if len(title) > 50:
            title = title[:47] + "..."
        return title