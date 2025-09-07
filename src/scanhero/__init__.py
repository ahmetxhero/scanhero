"""ScanHero: A modern, lightweight, and modular Python package for port and service scanning.

This package provides fast asynchronous port scanning capabilities with service detection,
multiple output formats, and both CLI and Python API interfaces.
"""

__version__ = "1.0.0"
__author__ = "Ahmet Hero"
__email__ = "ahmet@example.com"

from .scanner import PortScanner, ScanResult
from .models import ServiceInfo, ScanConfig
from .cli import main as cli_main
from .exceptions import ScanHeroError, ScanTimeoutError, InvalidTargetError

__all__ = [
    "PortScanner",
    "ScanResult", 
    "ServiceInfo",
    "ScanConfig",
    "cli_main",
    "ScanHeroError",
    "ScanTimeoutError",
    "InvalidTargetError",
]
