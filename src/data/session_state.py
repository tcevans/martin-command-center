import re
import asyncio
from datetime import datetime
from pathlib import Path
from typing import List

try:
    from ..models.project import Project
    from ..models.blocked import BlockedItem
    from ..config import Config
except ImportError:
    from models.project import Project
    from models.blocked import BlockedItem
    from config import Config

class SessionStateReader:
    """Reader for SESSION-STATE.md file."""
    
    def __init__(self, config: Config):
        self.config = config
        self.file_path = config.SESSION_STATE_PATH
    
    async def get_projects(self) -> List[Project]:
        """Parse projects from SESSION-STATE.md."""
        try:
            content = await self._read_file()
            if not content:
                return []
            
            projects = []
            
            # Look for project sections
            # Common patterns: "## Projects", "## Current Projects", etc.
            project_section = self._find_section(content, ["projects", "current projects", "active projects"])
            if project_section:
                projects.extend(self._parse_projects(project_section))
            
            # If no specific project section found, try to extract from general content
            if not projects:
                projects.extend(self._extract_projects_from_content(content))
            
            # If still no projects, create a default one based on overall file health
            if not projects:
                projects.append(self._create_default_project(content))
            
            return projects
            
        except Exception as e:
            print(f"Error reading projects from session state: {e}")
            return []
    
    async def get_blocked_items(self) -> List[BlockedItem]:
        """Parse blocked items from SESSION-STATE.md."""
        try:
            content = await self._read_file()
            if not content:
                return []
            
            blocked_items = []
            
            # Look for blocked items sections
            blocked_section = self._find_section(content, ["blocked", "blockers", "stuck items", "impediments"])
            if blocked_section:
                blocked_items.extend(self._parse_blocked_items(blocked_section))
            
            # Also look for TODO items with "[ ]" or "BLOCKED" indicators
            blocked_items.extend(self._extract_blocked_from_todos(content))
            
            return blocked_items
            
        except Exception as e:
            print(f"Error reading blocked items from session state: {e}")
            return []
    
    async def _read_file(self) -> str:
        """Read file contents asynchronously."""
        try:
            # Use asyncio.to_thread for file I/O in async context
            content = await asyncio.to_thread(self._read_file_sync)
            return content
        except FileNotFoundError:
            print(f"Session state file not found: {self.file_path}")
            return ""
        except Exception as e:
            print(f"Error reading session state file: {e}")
            return ""
    
    def _read_file_sync(self) -> str:
        """Synchronous file reading."""
        if not self.file_path.exists():
            return ""
        
        return self.file_path.read_text(encoding='utf-8')
    
    def _find_section(self, content: str, section_names: List[str]) -> str:
        """Find a section by name."""
        content_lower = content.lower()
        
        for section_name in section_names:
            # Look for markdown headers
            pattern = rf"^#+\s*{re.escape(section_name)}\s*$"
            match = re.search(pattern, content_lower, re.MULTILINE)
            if match:
                # Extract content from this header to the next header or end
                start_pos = match.end()
                
                # Find next header
                next_header = re.search(r"^#+\s", content[start_pos:], re.MULTILINE)
                if next_header:
                    end_pos = start_pos + next_header.start()
                    return content[start_pos:end_pos].strip()
                else:
                    return content[start_pos:].strip()
        
        return ""
    
    def _parse_projects(self, section_content: str) -> List[Project]:
        """Parse projects from a section."""
        projects = []
        lines = section_content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for project patterns: "- Project Name: Health Score" or similar
            project_match = re.search(r'^[-*+]\s*([^:]+?):\s*(.+)', line)
            if project_match:
                name = project_match.group(1).strip()
                health_info = project_match.group(2).strip()
                
                # Try to extract health score
                health = self._parse_health_score(health_info)
                status = self._determine_status(health_info)
                
                projects.append(Project(
                    name=name,
                    health=health,
                    status=status,
                    last_update=datetime.now()  # Assume current time
                ))
        
        return projects
    
    def _extract_projects_from_content(self, content: str) -> List[Project]:
        """Extract project-like items from general content."""
        projects = []
        
        # Look for bold text that might be project names
        bold_pattern = r'\*\*([^*]+)\*\*'
        bold_matches = re.findall(bold_pattern, content)
        
        for match in bold_matches[:3]:  # Limit to first 3
            if len(match.strip()) > 3 and len(match.strip()) < 30:
                projects.append(Project(
                    name=match.strip(),
                    health=0.7,  # Default health
                    status="unknown",
                    last_update=datetime.now()
                ))
        
        return projects
    
    def _create_default_project(self, content: str) -> Project:
        """Create a default project based on file health."""
        # Estimate "health" based on file characteristics
        lines = content.split('\n')
        health = 0.7  # Default health
        
        if len(lines) > 100:
            health = min(0.9, health + 0.1)
        
        if content.lower().count('completed') > 5:
            health = min(1.0, health + 0.1)
        
        if content.lower().count('blocked') > 3:
            health = max(0.3, health - 0.2)
        
        # Count various status indicators
        if content.lower().count('todo') > 10:
            health = max(0.4, health - 0.1)
        
        if content.lower().count('error') > 0:
            health = max(0.2, health - 0.1)
        
        return Project(
            name="Default Workspace",
            health=health,
            status="healthy" if health > 0.7 else "warning" if health > 0.4 else "blocked",
            last_update=datetime.now()
        )
    
    def _parse_blocked_items(self, section_content: str) -> List[BlockedItem]:
        """Parse blocked items from a section."""
        blocked_items = []
        lines = section_content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for blocked item patterns
            if re.search(r'\b(blocked|blocked by|depends on|waiting for)\b', line, re.IGNORECASE):
                # Extract description and reason
                description = self._extract_description(line)
                blocked_by = self._extract_blocked_reason(line)
                
                # Determine priority
                priority = self._determine_priority(line)
                
                blocked_items.append(BlockedItem(
                    id=f"blocked_{len(blocked_items) + 1}",
                    description=description,
                    blocked_by=blocked_by,
                    blocked_at=datetime.now(),  # Assume current time
                    priority=priority
                ))
        
        return blocked_items
    
    def _extract_blocked_from_todos(self, content: str) -> List[BlockedItem]:
        """Extract blocked items from TODO lists."""
        blocked_items = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            # Look for TODO items with [ ] or BLOCKED indicators
            if re.search(r'^(\s*[-*+]\s*)?\[\s*\]', line) and re.search(r'\b(blocked|waiting|depends)\b', line, re.IGNORECASE):
                description = re.sub(r'^\s*[-*+]\s*\[\s*\]\s*', '', line)
                description = re.sub(r'\b(blocked|waiting|depends)\s*:\s*', '', description, flags=re.IGNORECASE)
                
                blocked_by = "Unknown dependency"
                if "depends on" in line.lower():
                    blocked_by = re.search(r'depends on\s+(.+)', line, re.IGNORECASE)
                    blocked_by = blocked_by.group(1) if blocked_by else "Unknown dependency"
                elif "waiting for" in line.lower():
                    blocked_by = re.search(r'waiting for\s+(.+)', line, re.IGNORECASE)
                    blocked_by = blocked_by.group(1) if blocked_by else "Unknown dependency"
                
                priority = self._determine_priority(line)
                
                blocked_items.append(BlockedItem(
                    id=f"todo_{i}",
                    description=description.strip(),
                    blocked_by=blocked_by,
                    blocked_at=datetime.now(),
                    priority=priority
                ))
        
        return blocked_items
    
    def _parse_health_score(self, health_info: str) -> float:
        """Parse health score from text."""
        # Try to find percentage
        percent_match = re.search(r'(\d+)%', health_info)
        if percent_match:
            return int(percent_match.group(1)) / 100
        
        # Try to find fraction (e.g., "8/10")
        fraction_match = re.search(r'(\d+)/(\d+)', health_info)
        if fraction_match:
            numerator = int(fraction_match.group(1))
            denominator = int(fraction_match.group(2))
            if denominator > 0:
                return min(1.0, numerator / denominator)
        
        # Try to find decimal (e.g., "0.8")
        decimal_match = re.search(r'(\d*\.\d+)', health_info)
        if decimal_match:
            return min(1.0, float(decimal_match.group(1)))
        
        # Keyword-based scoring
        health_info_lower = health_info.lower()
        if "excellent" in health_info_lower or "great" in health_info_lower:
            return 0.9
        elif "good" in health_info_lower:
            return 0.8
        elif "okay" in health_info_lower or "fair" in health_info_lower:
            return 0.6
        elif "poor" in health_info_lower or "bad" in health_info_lower:
            return 0.3
        else:
            return 0.7  # Default
    
    def _determine_status(self, health_info: str) -> str:
        """Determine status from health info."""
        health_info_lower = health_info.lower()
        
        if re.search(r'\b(blocked|stuck|broken)\b', health_info_lower):
            return "blocked"
        elif re.search(r'\b(warning|issue|problem)\b', health_info_lower):
            return "warning"
        elif re.search(r'\b(healthy|good|excellent)\b', health_info_lower):
            return "healthy"
        else:
            return "unknown"
    
    def _determine_priority(self, text: str) -> str:
        """Determine priority from text."""
        text_lower = text.lower()
        
        if re.search(r'\b(critical|urgent|high priority|p0)\b', text_lower):
            return "critical"
        elif re.search(r'\b(high|important|p1)\b', text_lower):
            return "high"
        elif re.search(r'\b(low)\b', text_lower):
            return "low"
        else:
            return "medium"