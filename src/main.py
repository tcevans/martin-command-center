#!/usr/bin/env python3
"""Entry point for Martin's Command Center dashboard."""

from src.app import CommandCenterApp

def main():
    app = CommandCenterApp()
    app.run()

if __name__ == "__main__":
    main()
