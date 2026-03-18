import pytest
import asyncio
from unittest.mock import patch, MagicMock
from src.data.fetcher import DataFetcher
from src.config import Config

@pytest.fixture
def config():
    return Config()

@pytest.fixture
def fetcher(config):
    return DataFetcher(config)

@pytest.mark.asyncio
async def test_fetch_all_success(fetcher):
    # Mock return values for all sources
    with patch.object(fetcher.openclaw, 'get_active_sessions', return_value=['agent1']), \
         patch.object(fetcher.session_state, 'get_projects', return_value=['project1']), \
         patch.object(fetcher.github, 'get_recent_activity', return_value=['event1']), \
         patch.object(fetcher.session_state, 'get_blocked_items', return_value=['blocked1']):

        data = await fetcher.fetch_all()

        assert data.agents == ['agent1']
        assert data.projects == ['project1']
        assert data.github == ['event1']
        assert data.blocked == ['blocked1']

@pytest.mark.asyncio
async def test_fetch_all_partial_failure(fetcher):
    # Mock one source to raise an exception
    with patch.object(fetcher.openclaw, 'get_active_sessions', return_value=['agent1']), \
         patch.object(fetcher.session_state, 'get_projects', side_effect=Exception("DB Error")), \
         patch.object(fetcher.github, 'get_recent_activity', return_value=['event1']), \
         patch.object(fetcher.session_state, 'get_blocked_items', return_value=['blocked1']):

        data = await fetcher.fetch_all()

        assert data.agents == ['agent1']
        assert data.projects == []  # The failed one should be empty list
        assert data.github == ['event1']
        assert data.blocked == ['blocked1']

@pytest.mark.asyncio
async def test_fetch_individual_success(fetcher):
    with patch.object(fetcher.openclaw, 'get_active_sessions', return_value=['a']), \
         patch.object(fetcher.session_state, 'get_projects', return_value=['p']), \
         patch.object(fetcher.github, 'get_recent_activity', return_value=['g']), \
         patch.object(fetcher.session_state, 'get_blocked_items', return_value=['b']):

        assert await fetcher.fetch_agents() == ['a']
        assert await fetcher.fetch_projects() == ['p']
        assert await fetcher.fetch_github() == ['g']
        assert await fetcher.fetch_blocked() == ['b']

@pytest.mark.asyncio
async def test_fetch_individual_failure(fetcher):
    with patch.object(fetcher.openclaw, 'get_active_sessions', side_effect=Exception("E")), \
         patch.object(fetcher.session_state, 'get_projects', side_effect=Exception("E")), \
         patch.object(fetcher.github, 'get_recent_activity', side_effect=Exception("E")), \
         patch.object(fetcher.session_state, 'get_blocked_items', side_effect=Exception("E")):

        assert await fetcher.fetch_agents() == []
        assert await fetcher.fetch_projects() == []
        assert await fetcher.fetch_github() == []
        assert await fetcher.fetch_blocked() == []
