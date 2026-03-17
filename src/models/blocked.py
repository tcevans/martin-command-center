from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class BlockedItem:
    """Represents a blocked task."""
    id: str
    description: str
    blocked_by: str      # Reason or dependency
    blocked_at: datetime
    priority: str = "medium"  # "low", "medium", "high", "critical"
    assignee: str = ""
    
    @property
    def age_days(self) -> int:
        """Days since blocked."""
        age = datetime.now() - self.blocked_at
        return age.days
    
    @property
    def priority_color(self) -> str:
        """Color based on priority."""
        colors = {
            "critical": "text-error",
            "high": "text-warning",
            "medium": "text-primary",
            "low": "text-success"
        }
        return colors.get(self.priority, "text-primary")
    
    @property
    def priority_icon(self) -> str:
        """Icon based on priority."""
        icons = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🔵",
            "low": "🟢"
        }
        return icons.get(self.priority, "⚪")
    
    @property
    def display_description(self) -> str:
        """Description formatted for display."""
        desc = self.description
        if len(desc) > 60:
            desc = desc[:57] + "..."
        return desc