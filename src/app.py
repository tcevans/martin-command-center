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
    
    BINDINGS = [
        ("p", "toggle_auto_refresh", "Pause/Resume Auto-Refresh"),
        ("r", "refresh_all_manual", "Refresh All Now"),
    ]

    CSS = """
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
        border: solid $panel-lighten-1;
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
        color: red;
    }
    
    .success {
        color: green;
    }
    
    .warning {
        color: yellow;
    }
    """
    
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.data_fetcher = DataFetcher(self.config)
        self.last_refresh = None
        self.agent_timer = None
        self.project_timer = None
        self.blocked_timer = None
        self.github_timer = None
    
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
        self.agent_timer = self.set_interval(self.config.REFRESH_INTERVAL_AGENTS, self.refresh_agents, pause=not self.config.AUTO_REFRESH_ENABLED)
        self.project_timer = self.set_interval(self.config.REFRESH_INTERVAL_PROJECTS, self.refresh_projects, pause=not self.config.AUTO_REFRESH_ENABLED)
        self.blocked_timer = self.set_interval(self.config.REFRESH_INTERVAL_BLOCKED, self.refresh_blocked, pause=not self.config.AUTO_REFRESH_ENABLED)
        self.github_timer = self.set_interval(self.config.REFRESH_INTERVAL_GITHUB, self.refresh_github, pause=not self.config.AUTO_REFRESH_ENABLED)
        self.refresh_all()  # Initial fetch

    def action_toggle_auto_refresh(self) -> None:
        """Toggle auto-refresh state."""
        self.config.AUTO_REFRESH_ENABLED = not self.config.AUTO_REFRESH_ENABLED
        if self.config.AUTO_REFRESH_ENABLED:
            if self.agent_timer: self.agent_timer.resume()
            if self.project_timer: self.project_timer.resume()
            if self.blocked_timer: self.blocked_timer.resume()
            if self.github_timer: self.github_timer.resume()
        else:
            if self.agent_timer: self.agent_timer.pause()
            if self.project_timer: self.project_timer.pause()
            if self.blocked_timer: self.blocked_timer.pause()
            if self.github_timer: self.github_timer.pause()
        self._update_refresh_time()

    def action_refresh_all_manual(self) -> None:
        """Manually trigger a full refresh."""
        self.refresh_all()
    
    @work(exclusive=True)
    async def refresh_all(self) -> None:
        """Fetch all data and update UI."""
        self.refresh_agents()
        self.refresh_projects()
        self.refresh_blocked()
        self.refresh_github()

    @work(exclusive=True)
    async def refresh_agents(self) -> None:
        try:
            agents = await self.data_fetcher.fetch_agents()
            self.update_agent_panel(agents)
            self._update_refresh_time()
        except Exception as e:
            self.update_status(f"Error fetching agents: {str(e)}", error=True)

    @work(exclusive=True)
    async def refresh_projects(self) -> None:
        try:
            projects = await self.data_fetcher.fetch_projects()
            self.update_project_panel(projects)
            self._update_refresh_time()
        except Exception as e:
            self.update_status(f"Error fetching projects: {str(e)}", error=True)

    @work(exclusive=True)
    async def refresh_blocked(self) -> None:
        try:
            blocked = await self.data_fetcher.fetch_blocked()
            self.update_blocked_panel(blocked)
            self._update_refresh_time()
        except Exception as e:
            self.update_status(f"Error fetching blocked items: {str(e)}", error=True)

    @work(exclusive=True)
    async def refresh_github(self) -> None:
        try:
            github = await self.data_fetcher.fetch_github()
            self.update_github_panel(github)
            self._update_refresh_time()
        except Exception as e:
            self.update_status(f"Error fetching github data: {str(e)}", error=True)

    def _update_refresh_time(self) -> None:
        self.last_refresh = datetime.now()
        status = "Active" if self.config.AUTO_REFRESH_ENABLED else "Paused"
        self.update_status(f"Last updated: {self.last_refresh.strftime('%H:%M:%S')} | Auto-Refresh: {status} | ● Connected")

    def update_agent_panel(self, agents) -> None:
        """Update agent panel."""
        agent_panel = self.query_one("#agent-panel", Static)
        if agents:
            agent_text = self._render_agents(agents)
            agent_panel.update(agent_text)
            agent_panel.remove_class("loading error")
        else:
            agent_panel.update("[dim]No active agents[/dim]")
            agent_panel.remove_class("loading")
            agent_panel.add_class("error")

    def update_project_panel(self, projects) -> None:
        """Update project panel."""
        project_panel = self.query_one("#project-panel", Static)
        if projects:
            project_text = self._render_projects(projects)
            project_panel.update(project_text)
            project_panel.remove_class("loading error")
        else:
            project_panel.update("[dim]No project data available[/dim]")
            project_panel.remove_class("loading")
            project_panel.add_class("error")

    def update_blocked_panel(self, blocked) -> None:
        """Update blocked panel."""
        blocked_panel = self.query_one("#blocked-panel", Static)
        if blocked:
            blocked_text = self._render_blocked(blocked)
            blocked_panel.update(blocked_text)
            blocked_panel.remove_class("loading error")
        else:
            blocked_panel.update("[dim]No blocked items[/dim]")
            blocked_panel.remove_class("loading")

    def update_github_panel(self, github) -> None:
        """Update GitHub panel."""
        github_panel = self.query_one("#github-panel", Static)
        if github:
            github_text = self._render_github(github)
            github_panel.update(github_text)
            github_panel.remove_class("loading error")
        else:
            github_panel.update("[dim]No GitHub activity[/dim]")
            github_panel.remove_class("loading")
            github_panel.add_class("error")

    def update_panels(self, data) -> None:
        """Push data to individual panels."""
        self.update_agent_panel(data.agents)
        self.update_project_panel(data.projects)
        self.update_blocked_panel(data.blocked)
        self.update_github_panel(data.github)
    
    def _render_agents(self, agents) -> str:
        """Render agents panel."""
        lines = []
        lines.append("[bold cyan]🤖 Active Agents[/bold cyan]")
        lines.append("")
        
        for i, agent in enumerate(agents[:self.config.MAX_AGENTS_DISPLAY]):
            status_icon = "●" if agent.is_active else "○"
            color = "green" if agent.is_active else "dim"
            age = agent.age_minutes
            lines.append(f"[{color}]{status_icon}[/{color}] {agent.agent_type} ({age}m)")
        
        if len(agents) > self.config.MAX_AGENTS_DISPLAY:
            lines.append(f"[dim]... and {len(agents) - self.config.MAX_AGENTS_DISPLAY} more[/dim]")
        
        return "\n".join(lines)
    
    def _render_projects(self, projects) -> str:
        """Render projects panel."""
        lines = []
        lines.append("[bold cyan]📊 Project Health[/bold cyan]")
        lines.append("")
        
        for project in projects[:5]:  # Show top 5 projects
            health_bar = "█" * int(project.health * 10) + "░" * (10 - int(project.health * 10))
            color = project.health_color
            lines.append(f"[{color}]{health_bar}[/{color}] {project.name[:20]}")
        
        return "\n".join(lines)
    
    def _render_blocked(self, blocked) -> str:
        """Render blocked panel."""
        lines = []
        lines.append("[bold cyan]🚧 Blocked Items[/bold cyan]")
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
        lines.append("[bold cyan]🐙 GitHub Activity[/bold cyan]")
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
            status_bar.update(f"[red]❌ {message}[/red]")
        else:
            status_bar.update(message)

if __name__ == "__main__":
    app = CommandCenterApp()
    app.run()