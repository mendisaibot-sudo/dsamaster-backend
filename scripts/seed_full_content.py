#!/usr/bin/env python3
"""
DSAMaster Seed Script - Full Content
Wrapper around load_full_content.py to seed the database with all content.

Usage:
    python scripts/seed_full_content.py
"""
import sys
from pathlib import Path

# Delegate to load_full_content.py
loader = Path(__file__).parent / "load_full_content.py"
exec(compile(open(loader, "rb").read(), str(loader), "exec"))
