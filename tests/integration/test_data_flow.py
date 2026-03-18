import pytest
from unittest.mock import patch, AsyncMock
from datetime import datetime
from src.data.fetcher import DataFetcher
from src.config import Config
from src.models.agent import Agent
from src.models.project import Project
from src.models.github import GitHubEvent
from src.models.blocked import BlockedItem

@pytest.fixture
def mock_config():
    return Config()

@pytest.mark.asyncio
async def test_data_fetcher_integration(mock_config):
    fetcher = DataFetcher(mock_config)

    mock_agent = Agent(
        session_key="key",
        agent_type="coder",
        status="active",
        started_at=datetime.now(),
        last_activity=datetime.now()
    )

    mock_project = Project(
        name="Test Project",
        health=0.9,
        status="healthy"
    )

    mock_github = GitHubEvent(
        type="pr",
        title="Test PR",
        status="open",
        repo="test/repo",
        timestamp=datetime.now()
    )

    mock_blocked = BlockedItem(
        id="1",
        description="Test Blocker",
        blocked_by="Dependency",
        blocked_at=datetime.now()
    )

    with patch('src.data.openclaw.OpenClawClient.get_active_sessions', new_callable=AsyncMock) as mock_get_sessions, \
         patch('src.data.github.GitHubClient.get_recent_activity', new_callable=AsyncMock) as mock_get_github, \
         patch('src.data.session_state.SessionStateReader.get_projects', new_callable=AsyncMock) as mock_get_projects, \
         patch('src.data.session_state.SessionStateReader.get_blocked_items', new_callable=AsyncMock) as mock_get_blocked:

        mock_get_sessions.return_value = [mock_agent]
        mock_get_github.return_value = [mock_github]
        mock_get_projects.return_value = [mock_project]
        mock_get_blocked.return_value = [mock_blocked]

        data = await fetcher.fetch_all()

        # Verify the data was correctly aggregated
        assert len(data.agents) == 1
        assert data.agents[0] == mock_agent

        assert len(data.projects) == 1
        assert data.projects[0] == mock_project

        assert len(data.github) == 1
        assert data.github[0] == mock_github

        assert len(data.blocked) == 1
        assert data.blocked[0] == mock_blocked
