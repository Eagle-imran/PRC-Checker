#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "playwright>=1.44",
#     "jinja2>=3.1",
#     "pydantic>=2.0",
# ]
# ///
"""
MahaBhulekh PR Card fetcher — Root Wrapper Script.
"""
import sys

from prc_checker.cli import main

if __name__ == "__main__":
    sys.exit(main())
