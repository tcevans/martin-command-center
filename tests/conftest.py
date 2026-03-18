import pytest
from datetime import datetime, timedelta

@pytest.fixture
def mock_now():
    return datetime(2025, 1, 1, 12, 0, 0)
