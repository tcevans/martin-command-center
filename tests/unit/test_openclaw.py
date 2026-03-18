import pytest
import asyncio
from datetime import datetime
from unittest.mock import patch
from src.data.openclaw import OpenClawClient

@pytest.fixture
def openclaw_client():
    return OpenClawClient()

def test_parse_agent_basic(openclaw_client):
    data = {
        "key": "test-key",
        "agentType": "coder",
        "status": "active",
        "startedAt": 1704067200, # 2024-01-01 00:00:00
        "updatedAt": 1704067200,
        "runtime": "coder",
        "model": "test-model"
    }

    with patch("src.data.openclaw.datetime") as mock_dt:
        mock_now = datetime(2025, 1, 1, 12, 0, 0)
        mock_dt.now.return_value = mock_now
        mock_dt.fromtimestamp = datetime.fromtimestamp
        mock_dt.strptime = datetime.strptime

        agent = openclaw_client._parse_agent(data)
        assert agent.session_key == "test-key"
        assert agent.agent_type == "coder"
        assert agent.status == "active"
        assert agent.started_at == datetime.fromtimestamp(1704067200)
        assert agent.last_activity == datetime.fromtimestamp(1704067200)
        assert agent.runtime == "coder"
        assert agent.model == "test-model"

def test_determine_agent_type(openclaw_client):
    # Tests based on runtime string checking
    assert openclaw_client._determine_agent_type({"runtime": "architect-runtime"}) == "architect"
    assert openclaw_client._determine_agent_type({"runtime": "project-manager"}) == "project-manager"

    # Tests based on agentType
    assert openclaw_client._determine_agent_type({"agentType": "researcher"}) == "researcher"

    # Tests fallback to title case
    assert openclaw_client._determine_agent_type({"runtime": "some-other"}) == "Some Other"

def test_determine_status(openclaw_client):
    assert openclaw_client._determine_status({"status": "running"}) == "active"
    assert openclaw_client._determine_status({"status": "idle"}) == "idle"
    assert openclaw_client._determine_status({"status": "paused"}) == "waiting"
    assert openclaw_client._determine_status({"status": "unknown"}) == "active" # fallback

def test_parse_datetime_seconds(openclaw_client):
    # Timestamp in seconds: 1704067200 -> 2024-01-01 00:00:00 UTC
    dt = openclaw_client._parse_datetime(1704067200)
    assert dt == datetime.fromtimestamp(1704067200)

def test_parse_datetime_milliseconds(openclaw_client):
    # Timestamp in milliseconds: > 1,000,000,000,000
    # 1704067200000 -> 2024-01-01 00:00:00 UTC
    dt = openclaw_client._parse_datetime(1704067200000)
    assert dt == datetime.fromtimestamp(1704067200)

def test_parse_datetime_string(openclaw_client):
    dt = openclaw_client._parse_datetime("2024-01-01T12:00:00Z")
    assert dt == datetime(2024, 1, 1, 12, 0, 0)

def test_parse_datetime_invalid(openclaw_client):
    with patch("src.data.openclaw.datetime") as mock_dt:
        mock_now = datetime(2025, 1, 1, 12, 0, 0)
        mock_dt.now.return_value = mock_now
        # We need to let strptime fail with ValueError to trigger the fallback
        mock_dt.strptime.side_effect = ValueError("invalid format")

        # Test None
        assert openclaw_client._parse_datetime(None) == mock_now

        # Test unparseable string
        assert openclaw_client._parse_datetime("invalid-date-string") == mock_now

@pytest.mark.asyncio
async def test_get_active_sessions(openclaw_client):
    agents = await openclaw_client.get_active_sessions()
    assert len(agents) == 4

    # Verify the specific "coder" agent parsed from the mock data
    coder = next(a for a in agents if a.agent_type == "coder")
    assert coder.session_key == "agent:coder:subagent:ca1b5562-7430-4d55-a348-81d12d491be9"
    assert coder.status == "active"
    assert coder.model == "hf:moonshotai/Kimi-K2-Instruct-0905"
