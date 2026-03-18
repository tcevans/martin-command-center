#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test the dashboard rendering without running the full TUI.
"""

import sys
import io
from pathlib import Path
import asyncio

# Set UTF-8 encoding for stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add src to path so we can import our modules
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from config import Config
from data.fetcher import DataFetcher

async def test_rendering():
    """Test dashboard rendering."""
    print("🎨 Testing dashboard rendering...")
    print()
    
    config = Config()
    fetcher = DataFetcher(config)
    
    # Fetch data
    print("📊 Fetching data...")
    data = await fetcher.fetch_all()
    
    print(f"✅ Data fetched:")
    print(f"  - Agents: {len(data.agents)}")
    print(f"  - Projects: {len(data.projects)}")
    print(f"  - GitHub events: {len(data.github)}")
    print(f"  - Blocked items: {len(data.blocked)}")
    print()
    
    # Render each section
    print("🖼️  Rendered Sections:")
    print("=" * 60)
    
    # Agents section
    print("\n[🤖 AGENTS SECTION]")
    if data.agents:
        for i, agent in enumerate(data.agents[:config.MAX_AGENTS_DISPLAY]):
            status_icon = "●" if agent.is_active else "○"
            color = "green" if agent.is_active else "dim"
            age = agent.age_minutes
            print(f"{status_icon} {agent.agent_type} ({age}m)")
    else:
        print("No active agents")
    
    # Projects section
    print("\n[📊 PROJECTS SECTION]")
    if data.projects:
        for project in data.projects[:5]:
            health_bar = "█" * int(project.health * 10) + "░" * (10 - int(project.health * 10))
            print(f"[{health_bar}] {project.name[:20]} {project.health_percentage}%")

            # Format build status
            build_icon = "✅" if project.build_status == "passing" else "❌" if project.build_status == "failing" else "❓"

            # Additional metrics
            metrics = []
            metrics.append(f"Build: {build_icon} {project.build_status}")
            if project.test_coverage != "unknown":
                metrics.append(f"Coverage: {project.test_coverage}")
            if project.deployment_status != "unknown":
                metrics.append(f"Deploy: {project.deployment_status}")

            print("  " + " | ".join(metrics))
            print("")
    else:
        print("No project data")
    
    # GitHub section
    print("\n[🐙 GITHUB SECTION]")
    if data.github:
        for event in data.github[:config.MAX_EVENTS_DISPLAY]:
            icon = event.status_icon
            color = event.status_color
            age = event.age_hours
            print(f"{icon} {event.display_title} ({age}h)")
    else:
        print("No GitHub activity")
    
    # Blocked items section
    print("\n[🚧 BLOCKED SECTION]")
    if data.blocked:
        for item in data.blocked[:config.MAX_BLOCKED_DISPLAY]:
            icon = item.priority_icon
            days = item.age_days
            print(f"{icon} {item.display_description} ({days}d)")
    else:
        print("No blocked items")
    
    print("\n" + "=" * 60)
    print("✅ Rendering test completed!")
    print("This is what the dashboard would display in the terminal UI.")

if __name__ == "__main__":
    asyncio.run(test_rendering())