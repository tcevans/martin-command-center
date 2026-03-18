import pytest
from unittest.mock import patch, AsyncMock
from datetime import datetime
from textual.widgets import Static
from src.app import CommandCenterApp
from src.data.fetcher import DashboardData
from src.models.agent import Agent
from src.models.project import Project
from src.models.github import GitHubEvent
from src.models.blocked import BlockedItem

@pytest.fixture
def mock_dashboard_data():
    return DashboardData(
        agents=[
            Agent(
                session_key="key",
                agent_type="coder",
                status="active",
                started_at=datetime.now(),
                last_activity=datetime.now()
            )
        ],
        projects=[
            Project(
                name="Test Project",
                health=0.9,
                status="healthy"
            )
        ],
        github=[
            GitHubEvent(
                type="pr",
                title="Test PR",
                status="open",
                repo="test/repo",
                timestamp=datetime.now()
            )
        ],
        blocked=[
            BlockedItem(
                id="1",
                description="Test Blocker",
                blocked_by="Dependency",
                blocked_at=datetime.now()
            )
        ]
    )

@pytest.mark.asyncio
async def test_app_mount_and_update(mock_dashboard_data):
    app = CommandCenterApp()

    async with app.run_test() as pilot:
        # Wait for any background tasks (like refresh_all) to settle
        await pilot.pause(0.1)

        # We can skip the internal App.refresh_all background worker for tests
        # and just call update_panels directly to verify rendering logic works.
        app.update_panels(mock_dashboard_data)
        await pilot.pause(0.1)

        # The panels should be present
        agent_panel = app.query_one("#agent-panel", Static)
        project_panel = app.query_one("#project-panel", Static)
        blocked_panel = app.query_one("#blocked-panel", Static)
        github_panel = app.query_one("#github-panel", Static)

        # The loading class should be removed
        assert not agent_panel.has_class("loading")
        assert not project_panel.has_class("loading")
        assert not blocked_panel.has_class("loading")
        assert not github_panel.has_class("loading")

        # Panel contents should reflect the mocked data
        agent_text = str(agent_panel.render())
        assert "coder" in agent_text

        project_text = str(project_panel.render())
        assert "Test Project" in project_text

        blocked_text = str(blocked_panel.render())
        assert "Test Blocker" in blocked_text

        github_text = str(github_panel.render())
        assert "Test PR" in github_text
