from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Project:
    """Represents a tracked project."""
    name: str
    health: float        # 0.0 - 1.0
    status: str          # "healthy", "warning", "blocked", "unknown"
    blocked_count: int = 0
    last_update: Optional[datetime] = None
    build_status: str = "unknown"
    test_coverage: str = "unknown"
    deployment_status: str = "unknown"
    
    @property
    def health_percentage(self) -> int:
        """Health as percentage (0-100)."""
        return int(self.health * 100)
    
    @property
    def health_color(self) -> str:
        """Color based on health score."""
        if self.health >= 0.8:
            return "green"
        elif self.health >= 0.5:
            return "yellow"
        else:
            return "red"
    
    @property
    def age_hours(self) -> int:
        """Hours since last update."""
        if self.last_update:
            age = datetime.now() - self.last_update
            return int(age.total_seconds() / 3600)
        return -1