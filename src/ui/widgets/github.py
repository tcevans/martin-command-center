from textual.widgets import Static
from typing import List

try:
    from ...models.github import GitHubEvent
    from ...config import Config
except ImportError:
    from models.github import GitHubEvent
    from config import Config

class GitHubFeedWidget(Static):
    """Widget to display GitHub activity feed."""

    def __init__(self, id: str = None, classes: str = None):
        super().__init__("GitHub Panel Loading...", id=id, classes=classes)
        self.config = Config()

    def update_events(self, events: List['GitHubEvent']) -> None:
        """Update the widget with new GitHub events."""
        if not events:
            self.update("[text-muted]No GitHub activity[/text-muted]")
            self.remove_class("loading")
            self.add_class("error")
            return

        lines = []
        lines.append("[bold text-secondary]🐙 GitHub Activity[/bold text-secondary]")
        lines.append("")

        for event in events[:self.config.MAX_EVENTS_DISPLAY]:
            icon = event.status_icon
            color = event.status_color
            age = event.age_hours
            lines.append(f"[{color}]{icon}[/{color}] {event.display_title} ({age}h)")

        self.update("\n".join(lines))
        self.remove_class("loading error")
