from dataclasses import dataclass
from datetime import datetime

@dataclass
class Agent:
    """Represents an active agent."""
    session_key: str
    agent_type: str      # "architect", "coder", "researcher", etc.
    status: str          # "active", "idle", "waiting"
    started_at: datetime
    last_activity: datetime
    runtime: str = ""
    model: str = ""
    
    @property
    def is_active(self) -> bool:
        return self.status == "active"
    
    @property
    def age_minutes(self) -> int:
        """Age in minutes since start."""
        age = datetime.now() - self.started_at
        return int(age.total_seconds() / 60)
    
    @property
    def last_activity_minutes(self) -> int:
        """Minutes since last activity."""
        if self.last_activity:
            inactive = datetime.now() - self.last_activity
            return int(inactive.total_seconds() / 60)
        return 0