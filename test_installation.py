#!/usr/bin/env python3
"""Test script to verify ScanHero installation and basic functionality."""

import asyncio
import sys
from scanhero import PortScanner, ScanConfig
from scanhero.formatters import get_formatter


async def test_basic_functionality():
    """Test basic ScanHero functionality."""
    print("Testing ScanHero basic functionality...")
    
    try:
        # Test scanner creation
        config = ScanConfig(timeout=1.0, max_concurrent=10)
        scanner = PortScanner(config)
        print("✓ Scanner created successfully")
        
        # Test port parsing
        ports = scanner._parse_ports([80, 443, 22])
        assert ports == [80, 443, 22]
        print("✓ Port parsing works")
        
        # Test target validation
        target = scanner._validate_target("127.0.0.1")
        assert target == "127.0.0.1"
        print("✓ Target validation works")
        
        # Test formatters
        console_formatter = get_formatter("console")
        json_formatter = get_formatter("json")
        csv_formatter = get_formatter("csv")
        print("✓ Formatters created successfully")
        
        print("\nAll basic tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False


async def test_scan_functionality():
    """Test actual scanning functionality."""
    print("\nTesting scan functionality...")
    
    try:
        scanner = PortScanner()
        
        # Test scanning localhost (should work on most systems)
        result = await scanner.scan("127.0.0.1", [80, 443, 22])
        
        print(f"✓ Scan completed successfully")
        print(f"  Target: {result.target}")
        print(f"  Duration: {result.scan_duration:.2f}s")
        print(f"  Open ports: {result.open_count}")
        print(f"  Closed ports: {result.closed_count}")
        print(f"  Filtered ports: {result.filtered_count}")
        
        # Test formatters
        console_output = get_formatter("console").format(result)
        json_output = get_formatter("json").format(result)
        csv_output = get_formatter("csv").format(result)
        
        assert len(console_output) > 0
        assert len(json_output) > 0
        assert len(csv_output) > 0
        print("✓ All formatters work correctly")
        
        return True
        
    except Exception as e:
        print(f"✗ Scan test failed: {e}")
        return False


def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from scanhero import PortScanner, ScanResult, ServiceInfo
        from scanhero.exceptions import ScanHeroError, InvalidTargetError
        from scanhero.models import PortStatus, ServiceType
        from scanhero.service_detector import ServiceDetector
        from scanhero.formatters import ConsoleFormatter, JSONFormatter, CSVFormatter
        from scanhero.cli import main as cli_main
        
        print("✓ All imports successful")
        return True
        
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("ScanHero Installation Test")
    print("=" * 40)
    
    # Test imports
    if not test_imports():
        sys.exit(1)
    
    # Test basic functionality
    if not await test_basic_functionality():
        sys.exit(1)
    
    # Test scan functionality
    if not await test_scan_functionality():
        sys.exit(1)
    
    print("\n🎉 All tests passed! ScanHero is working correctly.")
    print("\nYou can now use ScanHero:")
    print("  - Command line: scanhero scan 127.0.0.1 --ports 80,443")
    print("  - Python API: from scanhero import PortScanner")


if __name__ == "__main__":
    asyncio.run(main())
