"""
dargslan-log-parser — Linux Log File Parser & Analyzer

Parse syslog, auth.log, nginx, and Apache logs with pattern matching.

Homepage: https://dargslan.com
Free Cheat Sheets: https://dargslan.com/cheat-sheets
"""

__version__ = "1.0.0"
__author__ = "Dargslan"
__url__ = "https://dargslan.com"

from dargslan_log_parser.parser import LogParser

__all__ = ["LogParser"]
