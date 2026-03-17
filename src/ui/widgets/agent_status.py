from textual.widgets import Static
from textual.app import ComposeResult

class AgentStatusWidget(Static):
    """Custom widget for displaying agent status with icons and color coding."""

    DEFAULT_CSS = """
    AgentStatusWidget {
        height: auto;
        padding: 1;
        margin-bottom: 1;
        border: solid $panel-lighten-1;
        background: $surface;
    }
    """

    def __init__(self, agent, **kwargs):
        super().__init__(**kwargs)
        self.agent = agent

    def compose(self) -> ComposeResult:
        status = getattr(self.agent, "status", "unknown").lower()
        agent_type = getattr(self.agent, "agent_type", "Unknown")
        model = getattr(self.agent, "model", "Unknown")
        if not model:
            model = "Unknown"
        age = getattr(self.agent, "age_minutes", 0)

        status_map = {
            "active": ("🟢", "green"),
            "idle": ("🟡", "yellow"),
            "waiting": ("🔴", "red"),
            "blocked": ("🔴", "red"),
        }
        icon, color = status_map.get(status, ("⚪", "white"))

        yield Static(f"[{color}]{icon}[/{color}] [bold]{agent_type}[/bold]")
        yield Static(f"Status: [{color}]{status}[/{color}] | Age: {age}m")
        yield Static(f"Model: [dim]{model}[/dim]")
