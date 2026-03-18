import pytest
from datetime import datetime, timedelta
from unittest.mock import patch
from src.models.github import GitHubEvent

@pytest.fixture
def mock_github_time():
    with patch("src.models.github.datetime") as mock_dt:
        mock_dt.now.return_value = datetime(2025, 1, 1, 12, 0, 0)
        yield mock_dt

def test_github_event_status_icon():
    event_success = GitHubEvent(type="pr", title="Test", status="success", repo="test", timestamp=datetime.now())
    assert event_success.status_icon == "✓"

    event_failure = GitHubEvent(type="pr", title="Test", status="failure", repo="test", timestamp=datetime.now())
    assert event_failure.status_icon == "✗"

    event_pending = GitHubEvent(type="pr", title="Test", status="pending", repo="test", timestamp=datetime.now())
    assert event_pending.status_icon == "⏳"

    event_unknown = GitHubEvent(type="pr", title="Test", status="unknown", repo="test", timestamp=datetime.now())
    assert event_unknown.status_icon == "•"

def test_github_event_status_color():
    event_success = GitHubEvent(type="pr", title="Test", status="success", repo="test", timestamp=datetime.now())
    assert event_success.status_color == "green"

    event_failure = GitHubEvent(type="pr", title="Test", status="failure", repo="test", timestamp=datetime.now())
    assert event_failure.status_color == "red"

    event_unknown = GitHubEvent(type="pr", title="Test", status="unknown", repo="test", timestamp=datetime.now())
    assert event_unknown.status_color == "white"

def test_github_event_age_hours(mock_github_time):
    # 3 hours ago
    event = GitHubEvent(
        type="pr",
        title="Test",
        status="open",
        repo="test",
        timestamp=datetime(2025, 1, 1, 9, 0, 0)
    )
    assert event.age_hours == 3

def test_github_event_display_title():
    short_title = "This is a short title"
    event_short = GitHubEvent(type="pr", title=short_title, status="open", repo="test", timestamp=datetime.now())
    assert event_short.display_title == short_title

    long_title = "This is a very long title that exceeds the fifty character limit and should be truncated"
    event_long = GitHubEvent(type="pr", title=long_title, status="open", repo="test", timestamp=datetime.now())
    assert event_long.display_title == "This is a very long title that exceeds the fift..."
    assert len(event_long.display_title) == 50
