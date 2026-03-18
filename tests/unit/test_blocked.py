import pytest
from datetime import datetime, timedelta
from unittest.mock import patch
from src.models.blocked import BlockedItem

@pytest.fixture
def mock_blocked_time():
    with patch("src.models.blocked.datetime") as mock_dt:
        mock_dt.now.return_value = datetime(2025, 1, 5, 12, 0, 0)
        yield mock_dt

def test_blocked_item_age_days(mock_blocked_time):
    # 4 days ago
    item = BlockedItem(
        id="1",
        description="Test",
        blocked_by="Dep",
        blocked_at=datetime(2025, 1, 1, 12, 0, 0)
    )
    assert item.age_days == 4

def test_blocked_item_priority_color():
    item_critical = BlockedItem(id="1", description="Test", blocked_by="Dep", blocked_at=datetime.now(), priority="critical")
    assert item_critical.priority_color == "red"

    item_high = BlockedItem(id="1", description="Test", blocked_by="Dep", blocked_at=datetime.now(), priority="high")
    assert item_high.priority_color == "yellow"

    item_medium = BlockedItem(id="1", description="Test", blocked_by="Dep", blocked_at=datetime.now(), priority="medium")
    assert item_medium.priority_color == "blue"

    item_low = BlockedItem(id="1", description="Test", blocked_by="Dep", blocked_at=datetime.now(), priority="low")
    assert item_low.priority_color == "green"

    item_unknown = BlockedItem(id="1", description="Test", blocked_by="Dep", blocked_at=datetime.now(), priority="unknown")
    assert item_unknown.priority_color == "white"

def test_blocked_item_priority_icon():
    item_critical = BlockedItem(id="1", description="Test", blocked_by="Dep", blocked_at=datetime.now(), priority="critical")
    assert item_critical.priority_icon == "🔴"

    item_unknown = BlockedItem(id="1", description="Test", blocked_by="Dep", blocked_at=datetime.now(), priority="unknown")
    assert item_unknown.priority_icon == "⚪"

def test_blocked_item_display_description():
    short_desc = "Short description"
    item_short = BlockedItem(id="1", description=short_desc, blocked_by="Dep", blocked_at=datetime.now())
    assert item_short.display_description == short_desc

    long_desc = "This is a very long description that exceeds the sixty character limit"
    item_long = BlockedItem(id="1", description=long_desc, blocked_by="Dep", blocked_at=datetime.now())
    assert item_long.display_description == "This is a very long description that exceeds the sixty ch..."
    assert len(item_long.display_description) == 60
