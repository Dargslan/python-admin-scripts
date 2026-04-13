"""
dargslan-sysinfo — Linux System Information Tool

Get comprehensive system information: CPU, memory, disk, network,
uptime, and process monitoring.

Homepage: https://dargslan.com
Free Cheat Sheets: https://dargslan.com/cheat-sheets
Linux & DevOps Books: https://dargslan.com/books
"""

__version__ = "1.0.0"
__author__ = "Dargslan"
__url__ = "https://dargslan.com"

from dargslan_sysinfo.sysinfo import SystemInfo

__all__ = ["SystemInfo"]
