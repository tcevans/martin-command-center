import asyncio
import json
import subprocess
from datetime import datetime, timedelta
from typing import List

try:
    from models.github import GitHubEvent
    from config import Config
except ImportError:
    from ..models.github import GitHubEvent
    from ..config import Config

class GitHubClient:
    """Wrapper for GitHub CLI (gh)."""
    
    def __init__(self, config: Config):
        self.config = config
    
    async def _run_gh_command(self, args: List[str]) -> str:
        """Run a GitHub CLI command and return the output."""
        try:
            cmd = ["gh"] + args
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            
            if result.returncode != 0:
                print(f"GitHub CLI error: {stderr.decode()}")
                return ""
                
            return stdout.decode()
            
        except Exception as e:
            print(f"Failed to run GitHub command: {e}")
            return ""
        
    async def get_recent_activity(self) -> List[GitHubEvent]:
        """Fetch recent GitHub activity."""
        try:
            events = []
            
            # Fetch PRs
            prs_result = await self._run_gh_command([
                "pr", "list", 
                "--limit", "5", 
                "--state", "all",
                "--json", "number,title,state,createdAt,author,headRepositoryOwner,headRefName,url"
            ])
            
            if prs_result:
                prs = json.loads(prs_result)
                for pr in prs:
                    events.append(GitHubEvent(
                        type="pr",
                        title=pr.get("title", "Unknown"),
                        status=pr.get("state", "unknown"),
                        repo=pr.get("headRepositoryOwner", {}).get("login", "unknown"),
                        timestamp=datetime.fromisoformat(pr.get("createdAt", "2026-01-01T00:00:00Z").replace("Z", "+00:00")),
                        url=pr.get("url", ""),
                        author=pr.get("author", {}).get("login", "unknown"),
                        number=pr.get("number", 0)
                    ))
            
            # Fetch workflow runs
            runs_result = await self._run_gh_command([
                "run", "list", 
                "--limit", "5",
                "--json", "databaseId,displayTitle,status,createdAt,headBranch,url,name"
            ])
            
            if runs_result:
                runs = json.loads(runs_result)
                for run in runs:
                    events.append(GitHubEvent(
                        type="run",
                        title=run.get("displayTitle") or run.get("name", "Unknown"),
                        status=run.get("status", "unknown"),
                        repo=run.get("headBranch", "unknown"),
                        timestamp=datetime.fromisoformat(run.get("createdAt", "2026-01-01T00:00:00Z").replace("Z", "+00:00")),
                        url=run.get("url", ""),
                        author=""
                    ))
            
            # Fetch issues
            issues_result = await self._run_gh_command([
                "issue", "list", 
                "--limit", "5", 
                "--state", "all",
                "--json", "number,title,state,createdAt,author,url"
            ])
            
            if issues_result:
                issues = json.loads(issues_result)
                for issue in issues:
                    # Use the config's GitHub repos as the repo name, or "unknown" if not set
                    repo_name = self.config.GITHUB_REPOS[0] if self.config.GITHUB_REPOS else "unknown"
                    events.append(GitHubEvent(
                        type="issue",
                        title=issue.get("title", "Unknown"),
                        status=issue.get("state", "unknown"),
                        repo=repo_name,
                        timestamp=datetime.fromisoformat(issue.get("createdAt", "2026-01-01T00:00:00Z").replace("Z", "+00:00")),
                        url=issue.get("url", ""),
                        author=issue.get("author", {}).get("login", "unknown"),
                        number=issue.get("number", 0)
                    ))
            
            # Sort by timestamp, newest first
            events.sort(key=lambda x: x.timestamp, reverse=True)
            return events
            
        except Exception as e:
            print(f"Error fetching GitHub activity: {e}")
            return []