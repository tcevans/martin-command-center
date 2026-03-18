import pytest
import asyncio
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
import json
from src.data.github import GitHubClient
from src.config import Config

@pytest.fixture
def config():
    c = Config()
    c.GITHUB_REPOS = ["test/repo"]
    return c

@pytest.fixture
def github_client(config):
    return GitHubClient(config)

@pytest.mark.asyncio
async def test_run_gh_command(github_client):
    # Mock create_subprocess_exec
    async def mock_communicate():
        return (b'mock output', b'')

    process_mock = MagicMock()
    process_mock.communicate = mock_communicate
    process_mock.returncode = 0

    with patch('asyncio.create_subprocess_exec', return_value=process_mock) as mock_exec:
        output = await github_client._run_gh_command(["test"])
        assert output == "mock output"
        mock_exec.assert_called_once_with('gh', 'test', stdout=-1, stderr=-1)

@pytest.mark.asyncio
async def test_run_gh_command_error(github_client):
    async def mock_communicate():
        return (b'', b'mock error')

    process_mock = MagicMock()
    process_mock.communicate = mock_communicate
    process_mock.returncode = 1

    with patch('asyncio.create_subprocess_exec', return_value=process_mock) as mock_exec:
        output = await github_client._run_gh_command(["test"])
        assert output == ""
        mock_exec.assert_called_once_with('gh', 'test', stdout=-1, stderr=-1)

@pytest.mark.asyncio
async def test_get_recent_activity(github_client):
    mock_prs = json.dumps([{
        "title": "PR 1",
        "state": "OPEN",
        "createdAt": "2024-01-01T12:00:00Z",
        "headRepositoryOwner": {"login": "test-repo"},
        "url": "http://pr1",
        "author": {"login": "user1"},
        "number": 1
    }])
    mock_runs = json.dumps([{
        "displayTitle": "Run 1",
        "status": "success",
        "createdAt": "2024-01-01T13:00:00Z",
        "headBranch": "main",
        "url": "http://run1"
    }])
    mock_issues = json.dumps([{
        "title": "Issue 1",
        "state": "CLOSED",
        "createdAt": "2024-01-01T14:00:00Z",
        "author": {"login": "user2"},
        "url": "http://issue1",
        "number": 2
    }])

    async def mock_run_gh_command(args):
        if args[0] == "pr":
            return mock_prs
        elif args[0] == "run":
            return mock_runs
        elif args[0] == "issue":
            return mock_issues
        return ""

    with patch.object(github_client, "_run_gh_command", side_effect=mock_run_gh_command):
        events = await github_client.get_recent_activity()

        assert len(events) == 3

        # Newest first sorting check (Issue at 14:00, Run at 13:00, PR at 12:00)
        assert events[0].type == "issue"
        assert events[0].title == "Issue 1"
        assert events[0].repo == "test/repo" # from config

        assert events[1].type == "run"
        assert events[1].title == "Run 1"
        assert events[1].repo == "main" # headBranch

        assert events[2].type == "pr"
        assert events[2].title == "PR 1"
        assert events[2].repo == "test-repo"
