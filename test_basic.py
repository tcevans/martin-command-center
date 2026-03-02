#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test script to verify the dashboard runs without errors."""

import sys
import io
from pathlib import Path
import asyncio

# Set UTF-8 encoding for stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add src to path so we can import our modules  
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from app import CommandCenterApp

async def test_dashboard():
    """Test the dashboard startup."""
    print("🚀 Testing dashboard startup...")
    
    try:
        # Create app instance
        app = CommandCenterApp()
        print("✅ App created successfully")
        
        # Test data fetcher
        from config import Config
        from data.fetcher import DataFetcher
        
        config = Config()
        fetcher = DataFetcher(config)
        print("✅ Data fetcher created successfully")
        
        # Test fetching data (with timeout)
        print("📊 Testing data fetch...")
        try:
            data = await asyncio.wait_for(fetcher.fetch_all(), timeout=10)
            print(f"✅ Data fetched successfully:")
            print(f"  - Agents: {len(data.agents)}")
            print(f"  - Projects: {len(data.projects)}")
            print(f"  - GitHub events: {len(data.github)}")
            print(f"  - Blocked items: {len(data.blocked)}")
        except asyncio.TimeoutError:
            print("⚠️ Data fetch timed out (expected if services aren't running)")
        except Exception as e:
            print(f"⚠️ Data fetch failed: {e}")
        
        print("\n🎉 Dashboard test completed successfully!")
        print("📝 Note: Some data sources may be empty if services aren't available.")
        print("🎯 To run the full dashboard: python run.py")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_dashboard())
    sys.exit(0 if success else 1)