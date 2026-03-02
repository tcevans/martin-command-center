import asyncio
from dataclasses import dataclass
from typing import List

try:
    from ..models.agent import Agent
    from ..models.project import Project
    from ..models.github import GitHubEvent
    from ..models.blocked import BlockedItem
    from ..config import Config
    from .openclaw import OpenClawClient
    from .github import GitHubClient
    from .session_state import SessionStateReader
except ImportError:
    # Handle direct module execution
    from models.agent import Agent
    from models.project import Project
    from models.github import GitHubEvent
    from models.blocked import BlockedItem
    from config import Config
    from data.openclaw import OpenClawClient
    from data.github import GitHubClient
    from data.session_state import SessionStateReader

@dataclass
class DashboardData:
    """Container for all dashboard data."""
    agents: List[Agent]
    projects: List[Project]
    github: List[GitHubEvent]
    blocked: List[BlockedItem]

class DataFetcher:
    """Orchestrates data fetching from all sources."""
    
    def __init__(self, config: Config):
        self.config = config
        self.openclaw = OpenClawClient()
        self.github = GitHubClient(config)
        self.session_state = SessionStateReader(config)
    
    async def fetch_all(self) -> DashboardData:
        """Fetch all data sources concurrently."""
        # Use asyncio.gather to run all fetches concurrently
        results = await asyncio.gather(
            self.openclaw.get_active_sessions(),
            self.session_state.get_projects(),
            self.github.get_recent_activity(),
            self.session_state.get_blocked_items(),
            return_exceptions=True  # Don't fail all on one error
        )
        
        # Handle any exceptions gracefully
        agents = results[0] if not isinstance(results[0], Exception) else []
        projects = results[1] if not isinstance(results[1], Exception) else []
        github = results[2] if not isinstance(results[2], Exception) else []
        blocked = results[3] if not isinstance(results[3], Exception) else []
        
        # Log any errors for debugging
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                source_names = ["agents", "projects", "github", "blocked"]
                print(f"Error fetching {source_names[i]}: {result}")
        
        return DashboardData(agents, projects, github, blocked)
    
    async def fetch_agents(self) -> List[Agent]:
        """Fetch only agent data."""
        try:
            return await self.openclaw.get_active_sessions()
        except Exception as e:
            print(f"Error fetching agents: {e}")
            return []
    
    async def fetch_projects(self) -> List[Project]:
        """Fetch only project data."""
        try:
            return await self.session_state.get_projects()
        except Exception as e:
            print(f"Error fetching projects: {e}")
            return []
    
    async def fetch_github(self) -> List[GitHubEvent]:
        """Fetch only GitHub data."""
        try:
            return await self.github.get_recent_activity()
        except Exception as e:
            print(f"Error fetching GitHub data: {e}")
            return []
    
    async def fetch_blocked(self) -> List[BlockedItem]:
        """Fetch only blocked items."""
        try:
            return await self.session_state.get_blocked_items()
        except Exception as e:
            print(f"Error fetching blocked items: {e}")
            return []