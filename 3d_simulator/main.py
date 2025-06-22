#!/usr/bin/env python3
"""
Main entry point for the 3D Language Simulator.
"""

import sys
import os

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.game_engine import GameEngine


def main():
    """Main function."""
    try:
        engine = GameEngine()
        engine.run()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
