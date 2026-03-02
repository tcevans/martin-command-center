#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Martin's Command Center - Quick Demo

Run this to see a quick demo of the terminal dashboard.
"""

import sys
import io
from pathlib import Path

# Set UTF-8 encoding for stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add src to path so we can import our modules
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from app import CommandCenterApp

def main():
    """Run the dashboard."""
    print("🚀 Starting Martin's Command Center...")
    print("Press Ctrl+C to exit")
    print()
    
    try:
        app = CommandCenterApp()
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error running dashboard: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())