import pytest
from datetime import datetime, timedelta
from unittest.mock import patch
from src.models.project import Project

@pytest.fixture
def mock_project_time():
    with patch("src.models.project.datetime") as mock_dt:
        mock_dt.now.return_value = datetime(2025, 1, 1, 12, 0, 0)
        yield mock_dt

def test_project_health_percentage():
    project = Project(name="Test", health=0.85, status="healthy")
    assert project.health_percentage == 85

    project_low = Project(name="Test", health=0.2, status="blocked")
    assert project_low.health_percentage == 20

def test_project_health_color():
    project_green = Project(name="Test", health=0.8, status="healthy")
    assert project_green.health_color == "green"

    project_yellow = Project(name="Test", health=0.5, status="warning")
    assert project_yellow.health_color == "yellow"

    project_red = Project(name="Test", health=0.49, status="blocked")
    assert project_red.health_color == "red"

def test_project_age_hours(mock_project_time):
    # 2 hours ago
    project = Project(
        name="Test",
        health=0.8,
        status="healthy",
        last_update=datetime(2025, 1, 1, 10, 0, 0)
    )
    assert project.age_hours == 2

def test_project_age_hours_none(mock_project_time):
    project = Project(
        name="Test",
        health=0.8,
        status="healthy",
        last_update=None
    )
    assert project.age_hours == -1
