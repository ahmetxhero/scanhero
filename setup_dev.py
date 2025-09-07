#!/usr/bin/env python3
"""Development setup script for ScanHero."""

import subprocess
import sys
import os


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed:")
        print(f"  Error: {e.stderr}")
        return False


def main():
    """Set up development environment."""
    print("ScanHero Development Setup")
    print("=" * 40)
    
    # Check Python version
    if sys.version_info < (3, 10):
        print("✗ Python 3.10+ is required")
        sys.exit(1)
    
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Install package in development mode
    if not run_command("pip install -e .", "Installing package in development mode"):
        sys.exit(1)
    
    # Install development dependencies
    if not run_command("pip install -e \"[dev]\"", "Installing development dependencies"):
        sys.exit(1)
    
    # Install pre-commit hooks
    if not run_command("pre-commit install", "Installing pre-commit hooks"):
        print("Warning: Pre-commit installation failed, continuing...")
    
    # Run basic tests
    if not run_command("python test_installation.py", "Running installation tests"):
        sys.exit(1)
    
    print("\n🎉 Development environment setup complete!")
    print("\nAvailable commands:")
    print("  make help          - Show all available commands")
    print("  make test          - Run tests")
    print("  make lint          - Run linting")
    print("  make format        - Format code")
    print("  make test-install  - Test installation")
    print("  make cli-test      - Test CLI functionality")
    print("\nExamples:")
    print("  python examples/basic_usage.py")
    print("  python examples/advanced_usage.py")
    print("  scanhero scan 127.0.0.1 --ports 80,443,22")


if __name__ == "__main__":
    main()
