# Martin's Command Center - Architecture Design

**Created:** 2026-03-02  
**Architect:** Arthur  
**Implementer:** Kalen

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        MARTIN'S COMMAND CENTER                          │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐│
│  │   AGENT STATUS  │  │  PROJECT HEALTH │  │   GITHUB ACTIVITY       ││
│  │    (Left)       │  │    (Center)     │  │      (Right)            ││
│  │                 │  │                 │  │                         ││
│  │ • Active agents │  │ • Health scores │  │ • Recent PRs            ││
│  │ • Session count │  │ • Blocked items │  │ • CI status             ││
│  │ • Tasks running │  │ • Warnings      │  │ • Issues                ││
│  └─────────────────┘  └─────────────────┘  └─────────────────────────┘│
├─────────────────────────────────────────────────────────────────────────┤
│  STATUS BAR: Last updated: HH:MM:SS | Refresh: 30s | ● Connected      │
└─────────────────────────────────────────────────────────────────────────┘
```

**Core Design Principles:**
- **Single-screen dashboard** - No navigation, all data visible at once
- **Async-first** - Non-blocking data fetching from all sources
- **Reactive UI** - Textual's reactive attributes auto-update on data change
- **Fail-gracefully** - Individual panel failures don't crash the dashboard

---

## 2. Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           DASHBOARD APP                                 │
│                    (Main App - textual.App)                            │
├─────────────────────────────────────────────────────────────────────────┤
│  on_mount()                                                            │
│    → start_timer(30s) → refresh_all()                                  │
│                                                                         │
│  refresh_all()                                                          │
│    → concurrent gather:                                                 │
│      ├── fetch_sessions()  →  AgentStatusPanel                         │
│      ├── fetch_projects()  →  ProjectHealthPanel                       │
│      ├── fetch_github()    →  GitHubActivityPanel                      │
│      └── fetch_blocked()   →  BlockedItemsPanel                        │
├─────────────────────────────────────────────────────────────────────────┤
│                              DATA LAYER                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │ OpenClawAPI  │  │  GitHubCLI   │  │ FileReader   │                  │
│  │  (sessions)  │  │    (gh)      │  │ (session-    │                  │
│  │              │  │              │  │   state)     │                  │
│  └──────────────┘  └──────────────┘  └──────────────┘                  │
├─────────────────────────────────────────────────────────────────────────┤
│                           CONFIG LAYER                                  │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                      config.py                                   │   │
│  │  • REFRESH_INTERVAL = 30                                        │   │
│  │  • SESSION_STATE_PATH = ...                                     │   │
│  │  • GITHUB_REPOS = [...]                                         │   │
│  │  • COLORS / STYLES                                              │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Data Flow

### 3.1 Data Flow Sequence

```
Timer Tick (30s)
      │
      ▼
┌─────────────────┐
│  refresh_all() │
│   (coroutine)   │
└────────┬────────┘
         │ concurrently launch:
         │
    ┌────┴────┬────────────┐
    ▼         ▼            ▼
┌───────┐ ┌───────┐   ┌───────┐
│Sessions│ │Projects│   │ GitHub│
│  API  │ │ File  │   │  CLI  │
└───┬───┘ └───┬───┘   └───┬───┘
    │         │           │
    ▼         ▼           ▼
┌─────────────────────────────┐
│    Data Models (dataclass)  │
│  • Agent                    │
│  • Project                  │
│  • GitHubEvent              │
│  • BlockedItem              │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│   Update Panel Widgets      │
│   (query_one + update)      │
└─────────────────────────────┘
```

### 3.2 Data Source Mapping

| Panel | Source | Method |
|-------|--------|--------|
| Agent Status | OpenClaw | `sessions_list` API (via subprocess) |
| Project Health | File | Read `SESSION-STATE.md` |
| GitHub Activity | CLI | `gh pr list`, `gh run list`, `gh issue list` |
| Blocked Items | File | Parse `SESSION-STATE.md` for blocked entries |

---

## 4. File Structure

```
martin-command-center/
├── design.md                  # This file
├── README.md
├── src/
│   ├── __init__.py
│   ├── app.py                 # Main Textual App class
│   ├── config.py              # Configuration constants
│   ├── models/
│   │   ├── __init__.py
│   │   ├── agent.py           # Agent dataclass
│   │   ├── project.py         # Project dataclass
│   │   ├── github.py          # GitHub event dataclass
│   │   └── blocked.py         # Blocked item dataclass
│   ├── data/
│   │   ├── __init__.py
│   │   ├── fetcher.py         # Main data fetcher orchestrator
│   │   ├── openclaw.py        # OpenClaw API client
│   │   ├── github.py         # GitHub CLI wrapper
│   │   └── session_state.py  # SESSION-STATE.md reader
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── widgets/
│   │   │   ├── __init__.py
│   │   │   ├── agent_panel.py    # Agent status widget
│   │   │   ├── project_panel.py  # Project health widget
│   │   │   ├── github_panel.py   # GitHub activity widget
│   │   │   ├── blocked_panel.py  # Blocked items widget
│   │   │   └── status_bar.py     # Bottom status bar
│   │   └── composer.py        # Panel layout composition
│   └── styles/
│       └── theme.py           # Color/theme definitions
├── tests/
│   ├── __init__.py
│   ├── test_data.py           # Data fetching tests
│   └── test_ui.py             # UI component tests
├── requirements.txt
└── run.py                     # Entry point
```

---

## 5. Key Class Definitions

### 5.1 Main Application

```python
# src/app.py
from textual.app import App
from textual import work

class CommandCenterApp(App):
    """Main dashboard application."""
    
    CSS = """
    /* Inline CSS or import from theme */
    """
    
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.data_fetcher = DataFetcher(self.config)
    
    # ─────────────────────────────────────────────
    # Lifecycle
    # ─────────────────────────────────────────────
    
    def compose(self) -> ComposeResult:
        """Create all panels and widgets."""
        yield from LayoutComposer.compose()
    
    def on_mount(self) -> None:
        """Start timer and initial data fetch."""
        self.set_interval(self.config.REFRESH_INTERVAL, self.refresh_all)
        self.refresh_all()  # Initial fetch
    
    # ─────────────────────────────────────────────
    # Data Refresh
    # ─────────────────────────────────────────────
    
    @work(exclusive=True, thread=True)
    async def refresh_all(self) -> None:
        """Fetch all data and update UI."""
        data = await self.data_fetcher.fetch_all()
        self.update_panels(data)
        self.update_timestamp()
    
    def update_panels(self, data: DashboardData) -> None:
        """Push data to individual panels."""
        self.query_one("#agent-panel", AgentPanel).update(data.agents)
        self.query_one("#project-panel", ProjectPanel).update(data.projects)
        self.query_one("#github-panel", GitHubPanel).update(data.github)
        self.query_one("#blocked-panel", BlockedPanel).update(data.blocked)
    
    def update_timestamp(self) -> None:
        """Update last-refreshed timestamp in status bar."""
        self.query_one("#status-bar", StatusBar).update_timestamp()
```

### 5.2 Configuration

```python
# src/config.py
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Config:
    """Dashboard configuration."""
    
    # Refresh
    REFRESH_INTERVAL: int = 30  # seconds
    
    # Paths
    SESSION_STATE_PATH: Path = Path(
        "~/.openclaw/workspace-architect/SESSION-STATE.md"
    ).expanduser()
    
    # GitHub
    GITHUB_REPOS: list[str] = []  # Optional: filter by repo
    
    # Display
    MAX_AGENTS_DISPLAY: int = 10
    MAX_EVENTS_DISPLAY: int = 15
    MAX_BLOCKED_DISPLAY: int = 10
    
    # Colors (Textual color names)
    COLOR_SUCCESS: str = "green"
    COLOR_WARNING: str = "yellow"
    COLOR_ERROR: str = "red"
    COLOR_MUTED: str = "dim"
```

### 5.3 Data Models

```python
# src/models/agent.py
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Agent:
    """Represents an active agent."""
    session_key: str
    agent_type: str      # "architect", "coder", "researcher", etc.
    status: str          # "active", "idle", "waiting"
    started_at: datetime
    last_activity: datetime
    
    @property
    def is_active(self) -> bool:
        return self.status == "active"


# src/models/project.py
@dataclass
class Project:
    """Represents a tracked project."""
    name: str
    health: float        # 0.0 - 1.0
    status: str          # "healthy", "warning", "blocked"
    blocked_count: int = 0
    last_update: datetime | None = None


# src/models/github.py
from datacaclass import dataclass

@dataclass
class GitHubEvent:
    """Represents a GitHub activity event."""
    type: str            # "pr", "run", "issue"
    title: str
    status: str          # "open", "closed", "success", "failure"
    repo: str
    timestamp: str


# src/models/blocked.py
@dataclass
class BlockedItem:
    """Represents a blocked task."""
    id: str
    description: str
    blocked_by: str      # Reason or dependency
    blocked_at: str      # Human-readable timestamp
```

### 5.4 Data Fetcher

```python
# src/data/fetcher.py
import asyncio
from dataclasses import dataclass

@dataclass
class DashboardData:
    """Container for all dashboard data."""
    agents: list[Agent]
    projects: list[Project]
    github: list[GitHubEvent]
    blocked: list[BlockedItem]

class DataFetcher:
    """Orchestrates data fetching from all sources."""
    
    def __init__(self, config: Config):
        self.config = config
        self.openclaw = OpenClawClient()
        self.github = GitHubClient(config)
        self.session_state = SessionStateReader(config)
    
    async def fetch_all(self) -> DashboardData:
        """Fetch all data sources concurrently."""
        agents, projects, github, blocked = await asyncio.gather(
            self.openclaw.get_active_sessions(),
            self.session_state.get_projects(),
            self.github.get_recent_activity(),
            self.session_state.get_blocked_items(),
            return_exceptions=True  # Don't fail all on one error
        )
        
        # Handle any exceptions gracefully
        agents = agents if not isinstance(agents, Exception) else []
        projects = projects if not isinstance(projects, Exception) else []
        github = github if not isinstance(github, Exception) else []
        blocked = blocked if not isinstance(agents, Exception) else []
        
        return DashboardData(agents, projects, github, blocked)
```

### 5.5 Data Sources

```python
# src/data/openclaw.py
import subprocess
import json
from typing import list

class OpenClawClient:
    """Client for OpenClaw API (sessions_list)."""
    
    async def get_active_sessions(self) -> list[Agent]:
        """Get active sessions via OpenClaw CLI."""
        result = await asyncio.create_subprocess_exec(
            "openclaw", "sessions", "list",
            "--json",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await result.communicate()
        
        # Parse JSON output into Agent objects
        data = json.loads(stdout.decode())
        return [Agent(**item) for item in data.get("sessions", [])]


# src/data/github.py
import subprocess
import json

class GitHubClient:
    """Wrapper for GitHub CLI (gh)."""
    
    def __init__(self, config: Config):
        self.repos = config.GITHUB_REPOS
    
    async def get_recent_activity(self) -> list[GitHubEvent]:
        """Fetch recent PRs, runs, and issues."""
        # Run gh commands and parse output
        prs = await self._get_prs()
        runs = await self._get_runs()
        issues = await self._get_issues()
        
        return sorted(prs + runs + issues, key=lambda x: x.timestamp)[:15]


# src/data/session_state.py
import re
from pathlib import Path

class SessionStateReader:
    """Reader for SESSION-STATE.md file."""
    
    def __init__(self, config: Config):
        self.path = config.SESSION_STATE_PATH
    
    async def get_projects(self) -> list[Project]:
        """Parse projects from SESSION-STATE.md."""
        content = await self._read_file()
        # Parse project health section
        # Return list of Project objects
        pass
    
    async def get_blocked_items(self) -> list[BlockedItem]:
        """Parse blocked items from SESSION-STATE.md."""
        content = await self._read_file()
        # Parse blocked section
        # Return list of BlockedItem objects
        pass
    
    async def _read_file(self) -> str:
        """Read file contents."""
        # Async file read
        pass
```

### 5.6 UI Panels

```python
# src/ui/widgets/agent_panel.py
from textual.widgets import Static
from textual.reactive import reactive

class AgentPanel(Static):
    """Panel showing active agent status."""
    
    BORDER_TITLE = "🤖 Agents"
    agents = reactive(list[Agent](), layout=False)
    
    def __init__(self, agent_id: str = "agent-panel"):
        super().__init__(id=agent_id)
    
    def watch_agents(self, agents: list[Agent]) -> None:
        """React to agent data changes."""
        self.update(self._render(agents))
    
    def _render(self, agents: list[Agent]) -> str:
        if not agents:
            return "[dim]No active agents[/dim]"
        
        lines = []
        for agent in agents[:10]:
            status_icon = "●" if agent.is_active else "○"
            color = "green" if agent.is_active else "dim"
            lines.append(f"[{color}]{status_icon}[/{color}] {agent.agent_type}")
        
        return "\n".join(lines)


# src/ui/widgets/status_bar.py
class StatusBar(Static):
    """Bottom status bar with timestamp."""
    
    def __init__(self):
        super().__init__(id="status-bar")
        self.last_update = None
    
    def update_timestamp(self) -> None:
        from datetime import datetime
        self.last_update = datetime.now().strftime("%H:%M:%S")
        self.update(f"Last updated: {self.last_update} | Refresh: 30s | ● Connected")
```

### 5.7 Layout Composer

```python
# src/ui/composer.py
from textual.containers import Horizontal, Vertical
from textual.widgets import Static

class LayoutComposer:
    """Composes the dashboard layout."""
    
    @staticmethod
    def compose():
        """Yield all dashboard panels."""
        yield Horizontal(
            Vertical(
                Static("Agent Panel Placeholder", id="agent-panel"),
                id="left-col"
            ),
            Vertical(
                Static("Project Panel Placeholder", id="project-panel"),
                Static("Blocked Panel Placeholder", id="blocked-panel"),
                id="center-col"
            ),
            Vertical(
                Static("GitHub Panel Placeholder", id="github-panel"),
                id="right-col"
            ),
            id="main-grid"
        )
        yield Static("Status Bar Placeholder", id="status-bar")
```

---

## 6. Implementation Roadmap

### Phase 1: Foundation (Build First)
**Goal:** Get a running app with basic structure

1. **Setup project structure**
   - Create `src/` directories
   - Create `requirements.txt` with `textual`, `pytest`
   - Create `run.py` entry point

2. **Create Config**
   - Define all configuration constants in `config.py`
   - Add path configuration for SESSION-STATE.md

3. **Create Data Models**
   - `models/agent.py` - Agent dataclass
   - `models/project.py` - Project dataclass
   - `models/github.py` - GitHubEvent dataclass
   - `models/blocked.py` - BlockedItem dataclass

4. **Create Basic App Shell**
   - `app.py` - Minimal Textual app with timer
   - Basic layout in `composer.py`
   - CSS styling

**Deliverable:** Running app showing placeholder panels, ticking timer

---

### Phase 2: Data Layer (Build Second)
**Goal:** Connect to all data sources

5. **Implement OpenClaw Client**
   - `data/openclaw.py` - sessions_list wrapper
   - Test with actual CLI call

6. **Implement GitHub Client**
   - `data/github.py` - gh CLI wrapper for PRs/runs/issues
   - Test with actual CLI calls

7. **Implement Session State Reader**
   - `data/session_state.py` - Read/parse SESSION-STATE.md
   - Extract projects and blocked items

8. **Create Data Fetcher**
   - `data/fetcher.py` - Orchestrator with `asyncio.gather`
   - Add error handling for each source

**Deliverable:** Console command that prints all data sources

---

### Phase 3: UI Panels (Build Third)
**Goal:** Render actual data in panels

9. **Create Agent Panel**
   - `widgets/agent_panel.py` - List active agents
   - Color-coded status indicators

10. **Create Project Panel**
    - `widgets/project_panel.py` - Show project health
    - Health bars or color indicators

11. **Create GitHub Panel**
    - `widgets/github_panel.py` - Recent PRs, runs, issues
    - Status icons (✓, ✗, open)

12. **Create Blocked Panel**
    - `widgets/blocked_panel.py` - List blocked items
    - Reason/dep display

13. **Create Status Bar**
    - `widgets/status_bar.py` - Timestamp, connection status

**Deliverable:** Fully functional dashboard with live data

---

### Phase 4: Polish (Build Fourth)
**Goal:** Production-ready refinements

14. **Styling & Theme**
    - `styles/theme.py` - Consistent colors
    - CSS refinements for readability

15. **Error Handling**
    - Panel-level error states (show "Failed to load" gracefully)
    - Retry logic for transient failures

16. **Testing**
    - `tests/test_data.py` - Data fetching tests
    - `tests/test_ui.py` - UI component tests

17. **Run Script**
    - `run.py` - Proper entry point with args

**Deliverable:** Production-ready dashboard

---

## 7. Key Implementation Notes

### Async Strategy
- Use `asyncio.create_subprocess_exec` for CLI commands (non-blocking)
- Use Textual's `@work` decorator for background data fetching
- `exclusive=True` prevents concurrent refreshes
- `return_exceptions=True` in `asyncio.gather` ensures one failure doesn't crash all

### Configuration
- All paths configurable via `Config` dataclass
- `SESSION-STATE.md` path follows OpenClaw workspace structure
- GitHub repos optional (empty list = all repos)

### Error Handling
- Individual data source failures → show empty/graceful state for that panel
- CLI not found → show "Install gh" message in GitHub panel
- File not found → show "No session state" in project/blocked panels

### CSS Layout
```
#main-grid {
    layout: horizontal;
    height: 100%;
}
#left-col { width: 25%; }
#center-col { width: 40%; }
#right-col { width: 35%; }
```

---

## 8. Acceptance Criteria

- [ ] App runs without errors
- [ ] All 4 panels render data
- [ ] 30-second auto-refresh works
- [ ] Individual panel failures don't crash app
- [ ] Status bar shows last update time
- [ ] Clean, readable terminal UI
- [ ] Configuration is externalized

---

**Done.**
