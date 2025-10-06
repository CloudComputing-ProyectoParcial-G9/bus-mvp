#!/usr/bin/env python3
"""
Standalone script to seed the passengers database
Can be run manually with: python seed.py
"""

import sys
import os

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.seed_data import seed_passengers

if __name__ == "__main__":
    print("=" * 60)
    print("MS-PASSENGERS Database Seeding Script")
    print("=" * 60)
    seed_passengers()
    print("=" * 60)
    print("Done!")
