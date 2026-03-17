from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Static
from textual import work
import asyncio
from datetime import datetime

try:
    from .config import Config
    from .data.fetcher import DataFetcher
except ImportError:
    # Handle direct module execution
    from config import Config
    from data.fetcher import DataFetcher

class CommandCenterApp(App):
    """Main dashboard application."""
    
    CSS = """
    /* Typography base */
    Screen {
        text-style: none;
    }

    /* Main layout */
    #main-grid {
        layout: horizontal;
        height: 100%;
        padding: 1;
    }
    
    #left-col {
        width: 25%;
        margin-right: 1;
    }
    
    #center-col {
        width: 40%;
        margin-right: 1;
    }
    
    #right-col {
        width: 35%;
    }
    
    /* Panel styling */
    .panel {
        height: 1fr;
        border: solid $primary;
        padding: 1;
        margin-bottom: 1;
    }
    
    /* Status bar */
    #status-bar {
        dock: bottom;
        height: 1;
        background: $panel-darken-1;
        content-align: right middle;
        padding: 0 2;
    }
    
    /* Loading state */
    .loading {
        text-style: dim;
    }
    
    .error {
        color: $error;
    }
    
    .success {
        color: $success;
    }
    
    .warning {
        color: $warning;
    }
    """
    
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.data_fetcher = DataFetcher(self.config)
        self.last_refresh = None
    
    def compose(self) -> ComposeResult:
        """Create all panels and widgets."""
        yield Horizontal(
            Vertical(
                Static("Agent Panel Loading...", id="agent-panel", classes="panel loading"),
                id="left-col"
            ),
            Vertical(
                Static("Project Panel Loading...", id="project-panel", classes="panel loading"),
                Static("Blocked Panel Loading...", id="blocked-panel", classes="panel loading"),
                id="center-col"
            ),
            Vertical(
                Static("GitHub Panel Loading...", id="github-panel", classes="panel loading"),
                id="right-col"
            ),
            id="main-grid"
        )
        yield Static("Status: Initializing...", id="status-bar")
    
    def on_mount(self) -> None:
        """Start timer and initial data fetch."""
        self.set_interval(self.config.REFRESH_INTERVAL, self.refresh_all)
        self.refresh_all()  # Initial fetch
    
    @work(exclusive=True)
    async def refresh_all(self) -> None:
        """Fetch all data and update UI."""
        try:
            self.update_status("Refreshing data...")
            data = await self.data_fetcher.fetch_all()
            self.update_panels(data)
            self.last_refresh = datetime.now()
            self.update_status(f"Last updated: {self.last_refresh.strftime('%H:%M:%S')} | Refresh: {self.config.REFRESH_INTERVAL}s | ● Connected")
        except Exception as e:
            self.update_status(f"Error: {str(e)}", error=True)
    
    def update_panels(self, data) -> None:
        """Push data to individual panels."""
        # Update agent panel
        agent_panel = self.query_one("#agent-panel", Static)
        if data.agents:
            agent_text = self._render_agents(data.agents)
            agent_panel.update(agent_text)
            agent_panel.remove_class("loading error")
        else:
            agent_panel.update("[text-muted]No active agents[/text-muted]")
            agent_panel.remove_class("loading")
            agent_panel.add_class("error")
        
        # Update project panel
        project_panel = self.query_one("#project-panel", Static)
        if data.projects:
            project_text = self._render_projects(data.projects)
            project_panel.update(project_text)
            project_panel.remove_class("loading error")
        else:
            project_panel.update("[text-muted]No project data available[/text-muted]")
            project_panel.remove_class("loading")
            project_panel.add_class("error")
        
        # Update blocked panel
        blocked_panel = self.query_one("#blocked-panel", Static)
        if data.blocked:
            blocked_text = self._render_blocked(data.blocked)
            blocked_panel.update(blocked_text)
            blocked_panel.remove_class("loading error")
        else:
            blocked_panel.update("[text-muted]No blocked items[/text-muted]")
            blocked_panel.remove_class("loading")
        
        # Update GitHub panel
        github_panel = self.query_one("#github-panel", Static)
        if data.github:
            github_text = self._render_github(data.github)
            github_panel.update(github_text)
            github_panel.remove_class("loading error")
        else:
            github_panel.update("[text-muted]No GitHub activity[/text-muted]")
            github_panel.remove_class("loading")
            github_panel.add_class("error")
    
    def _render_agents(self, agents) -> str:
        """Render agents panel."""
        lines = []
        lines.append("[bold text-secondary]🤖 Active Agents[/bold text-secondary]")
        lines.append("")
        
        for i, agent in enumerate(agents[:self.config.MAX_AGENTS_DISPLAY]):
            status_icon = "●" if agent.is_active else "○"
            color = "text-success" if agent.is_active else "text-muted"
            age = agent.age_minutes
            lines.append(f"[{color}]{status_icon}[/{color}] {agent.agent_type} ({age}m)")
        
        if len(agents) > self.config.MAX_AGENTS_DISPLAY:
            lines.append(f"[text-muted]... and {len(agents) - self.config.MAX_AGENTS_DISPLAY} more[/text-muted]")
        
        return "\n".join(lines)
    
    def _render_projects(self, projects) -> str:
        """Render projects panel."""
        lines = []
        lines.append("[bold text-secondary]📊 Project Health[/bold text-secondary]")
        lines.append("")
        
        for project in projects[:5]:  # Show top 5 projects
            health_bar = "█" * int(project.health * 10) + "░" * (10 - int(project.health * 10))
            color = project.health_color
            lines.append(f"[{color}]{health_bar}[/{color}] {project.name[:20]}")
        
        return "\n".join(lines)
    
    def _render_blocked(self, blocked) -> str:
        """Render blocked panel."""
        lines = []
        lines.append("[bold text-secondary]🚧 Blocked Items[/bold text-secondary]")
        lines.append("")
        
        for item in blocked[:self.config.MAX_BLOCKED_DISPLAY]:
            icon = item.priority_icon
            color = item.priority_color
            days = item.age_days
            lines.append(f"[{color}]{icon}[/{color}] {item.display_description} ({days}d)")
        
        return "\n".join(lines)
    
    def _render_github(self, events) -> str:
        """Render GitHub panel."""
        lines = []
        lines.append("[bold text-secondary]🐙 GitHub Activity[/bold text-secondary]")
        lines.append("")
        
        for event in events[:self.config.MAX_EVENTS_DISPLAY]:
            icon = event.status_icon
            color = event.status_color
            age = event.age_hours
            lines.append(f"[{color}]{icon}[/{color}] {event.display_title} ({age}h)")
        
        return "\n".join(lines)
    
    def update_status(self, message: str, error: bool = False) -> None:
        """Update status bar."""
        status_bar = self.query_one("#status-bar", Static)
        if error:
            status_bar.update(f"[text-error]❌ {message}[/text-error]")
        else:
            status_bar.update(message)

if __name__ == "__main__":
    app = CommandCenterApp()
    app.run()