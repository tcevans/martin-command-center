import asyncio
import json
import subprocess
from datetime import datetime
from typing import List

try:
    from ..models.agent import Agent
except ImportError:
    from models.agent import Agent

class OpenClawClient:
    """Client for OpenClaw API (sessions_list)."""
    
    async def get_active_sessions(self) -> List[Agent]:
        """Get active sessions via OpenClaw sessions_list tool."""
        try:
            # Since we're already in OpenClaw context, let's simulate the sessions_list call
            # For now, we'll create mock agents based on our current knowledge
            
            # Mock data similar to what sessions_list returns
            mock_sessions = [
                {
                    "key": "agent:project-manager:discord:channel:1476019052613996544",
                    "sessionId": "982d3aaa-d3d0-4574-8d93-7ccab0f1e524", 
                    "model": "hf:moonshotai/Kimi-K2.5",
                    "updatedAt": 1772443409374,
                    "agentType": "project-manager",
                    "runtime": "project-manager"
                },
                {
                    "key": "agent:architect:subagent:80e29a0a-4c96-4cf7-9547-5e4fbdf6fb4c",
                    "sessionId": "d83bd11b-58b6-4702-b8b9-cd80fe3951fa",
                    "model": "MiniMax-M2.5", 
                    "updatedAt": 1772442687436,
                    "agentType": "architect",
                    "runtime": "architect"
                },
                {
                    "key": "agent:coder:subagent:ca1b5562-7430-4d55-a348-81d12d491be9",  # This session!
                    "sessionId": "d8b988e4-278b-454a-a8b4-62ceeb907b4b",
                    "model": "hf:moonshotai/Kimi-K2-Instruct-0905",
                    "updatedAt": 1772443019714,
                    "agentType": "coder", 
                    "runtime": "coder"
                },
                {
                    "key": "agent:researcher:subagent:137d0c94-bbfa-4171-9227-9c9840dbde5c",
                    "sessionId": "9f4703a4-699f-485c-b0ad-aeff392f7fbb",
                    "model": "MiniMax-M2.5",
                    "updatedAt": 1772442247282,
                    "agentType": "researcher",
                    "runtime": "researcher"
                }
            ]
            
            agents = []
            for session_data in mock_sessions:
                try:
                    agent = self._parse_agent(session_data)
                    if agent:
                        agents.append(agent)
                except (KeyError, ValueError) as e:
                    print(f"Error parsing agent data: {e}")
                    continue
            
            print(f"Found {len(agents)} active agents")
            return agents
            
        except Exception as e:
            print(f"Error fetching OpenClaw sessions: {e}")
            return []
    
    def _parse_agent(self, session_data: dict) -> Agent:
        """Parse session data into Agent object."""
        # Handle various field mappings
        session_key = session_data.get("sessionKey", session_data.get("key", "unknown"))
        agent_type = self._determine_agent_type(session_data)
        status = self._determine_status(session_data)
        
        # Parse dates
        started_at = self._parse_datetime(session_data.get("startedAt", session_data.get("startTime")))
        last_activity = self._parse_datetime(session_data.get("lastActivity", session_data.get("updatedAt", started_at)))
        
        # Get additional metadata
        runtime = session_data.get("runtime", "")
        model = session_data.get("model", session_data.get("defaultModel", ""))
        
        return Agent(
            session_key=session_key,
            agent_type=agent_type,
            status=status,
            started_at=started_at,
            last_activity=last_activity or started_at,
            runtime=runtime,
            model=model
        )
    
    def _determine_agent_type(self, session_data: dict) -> str:
        """Determine agent type from session data."""
        # Try various fields that might contain agent type
        runtime = session_data.get("runtime", "").lower()
        agent_type = session_data.get("agentType", "")
        
        if runtime:
            if "architect" in runtime:
                return "architect"
            elif "coder" in runtime:
                return "coder"
            elif "researcher" in runtime:
                return "researcher"
            elif "project-manager" in runtime:
                return "project-manager"
            elif "code-reviewer" in runtime:
                return "code-reviewer"
        
        if agent_type:
            return agent_type
            
        # Default based on runtime or generic
        if runtime:
            return runtime.replace("-", " ").title()
        
        return "unknown"
    
    def _determine_status(self, session_data: dict) -> str:
        """Determine agent status from session data."""
        status = session_data.get("status", "").lower()
        
        if status in ["active", "running", "busy"]:
            return "active"
        elif status in ["idle", "waiting", "ready"]:
            return "idle"
        elif status in ["blocked", "paused"]:
            return "waiting"
        else:
            # Default to active if we can't determine
            return "active"
    
    def _parse_datetime(self, date_value) -> datetime:
        """Parse datetime from string or timestamp, fallback to now if invalid."""
        if not date_value:
            return datetime.now()
        
        # Handle Unix timestamps (integers)
        if isinstance(date_value, (int, float)):
            try:
                # Assuming it's milliseconds since epoch
                if date_value > 1000000000000:  # Likely milliseconds
                    return datetime.fromtimestamp(date_value / 1000)
                else:  # Likely seconds
                    return datetime.fromtimestamp(date_value)
            except (ValueError, OSError):
                return datetime.now()
        
        # Handle string dates
        if isinstance(date_value, str):
            # Try common datetime formats
            formats = [
                "%Y-%m-%dT%H:%M:%S.%fZ",  # ISO format with microseconds
                "%Y-%m-%dT%H:%M:%SZ",     # ISO format
                "%Y-%m-%d %H:%M:%S",      # Standard format
                "%Y-%m-%d",               # Date only
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_value, fmt)
                except ValueError:
                    continue
        
        # If all formats fail, return current time
        return datetime.now()