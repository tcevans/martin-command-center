#!/usr/bin/env python3
"""
Martin's Command Center - Terminal Dashboard

A real-time dashboard for monitoring agents, projects, and GitHub activity.
"""

import sys
import asyncio
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

import sys
from pathlib import Path

# Add src to path so we can import our modules
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from app import CommandCenterApp

def main():
    """Main entry point."""
    try:
        app = CommandCenterApp()
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()