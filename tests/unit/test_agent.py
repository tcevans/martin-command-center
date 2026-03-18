import pytest
from datetime import datetime, timedelta
from unittest.mock import patch
from src.models.agent import Agent

@pytest.fixture
def mock_agent_time():
    with patch("src.models.agent.datetime") as mock_dt:
        mock_dt.now.return_value = datetime(2025, 1, 1, 12, 0, 0)
        yield mock_dt

def test_agent_is_active():
    agent_active = Agent(
        session_key="test-key",
        agent_type="coder",
        status="active",
        started_at=datetime(2025, 1, 1, 11, 0, 0),
        last_activity=datetime(2025, 1, 1, 11, 30, 0)
    )
    assert agent_active.is_active is True

    agent_idle = Agent(
        session_key="test-key",
        agent_type="coder",
        status="idle",
        started_at=datetime(2025, 1, 1, 11, 0, 0),
        last_activity=datetime(2025, 1, 1, 11, 30, 0)
    )
    assert agent_idle.is_active is False

def test_agent_age_minutes(mock_agent_time):
    # 60 minutes ago
    agent = Agent(
        session_key="test-key",
        agent_type="coder",
        status="active",
        started_at=datetime(2025, 1, 1, 11, 0, 0),
        last_activity=datetime(2025, 1, 1, 11, 30, 0)
    )
    assert agent.age_minutes == 60

def test_agent_last_activity_minutes(mock_agent_time):
    # 30 minutes ago
    agent = Agent(
        session_key="test-key",
        agent_type="coder",
        status="active",
        started_at=datetime(2025, 1, 1, 11, 0, 0),
        last_activity=datetime(2025, 1, 1, 11, 30, 0)
    )
    assert agent.last_activity_minutes == 30

def test_agent_last_activity_minutes_none(mock_agent_time):
    agent = Agent(
        session_key="test-key",
        agent_type="coder",
        status="active",
        started_at=datetime(2025, 1, 1, 11, 0, 0),
        last_activity=None
    )
    assert agent.last_activity_minutes == 0
