#!/usr/bin/env python3
"""Basic usage examples for ScanHero."""

import asyncio
import json
from scanhero import PortScanner, ScanConfig
from scanhero.formatters import get_formatter


async def basic_scan():
    """Basic port scanning example."""
    print("=== Basic Port Scan ===")
    
    # Create scanner with default configuration
    scanner = PortScanner()
    
    # Scan common ports on localhost
    result = await scanner.scan("127.0.0.1", [80, 443, 22, 21, 25])
    
    # Print basic information
    print(f"Target: {result.target}")
    print(f"Scan Duration: {result.scan_duration:.2f}s")
    print(f"Open Ports: {result.open_count}")
    print(f"Closed Ports: {result.closed_count}")
    print(f"Filtered Ports: {result.filtered_count}")
    
    # Print open ports
    if result.open_ports:
        print("\nOpen Ports:")
        for port_result in result.open_ports:
            print(f"  Port {port_result.port}: {port_result.status.value}")
            if port_result.service:
                print(f"    Service: {port_result.service.name}")
                if port_result.service.version:
                    print(f"    Version: {port_result.service.version}")


async def custom_config_scan():
    """Port scanning with custom configuration."""
    print("\n=== Custom Configuration Scan ===")
    
    # Create custom configuration
    config = ScanConfig(
        timeout=5.0,           # Longer timeout
        max_concurrent=50,     # Fewer concurrent connections
        retry_count=2,         # More retries
        service_detection=True, # Enable service detection
        banner_grab=True,      # Enable banner grabbing
        scan_delay=0.1        # Small delay between scans
    )
    
    scanner = PortScanner(config)
    
    # Scan a range of ports
    result = await scanner.scan("127.0.0.1", "1-100")
    
    print(f"Scanned {result.total_ports} ports")
    print(f"Found {result.open_count} open ports")
    
    # Show services detected
    services = result.get_services()
    if services:
        print("\nDetected Services:")
        for service in services:
            print(f"  {service.name} (confidence: {service.confidence:.1%})")


async def output_formats():
    """Demonstrate different output formats."""
    print("\n=== Output Formats ===")
    
    scanner = PortScanner()
    result = await scanner.scan("127.0.0.1", [80, 443, 22])
    
    # Console format
    console_formatter = get_formatter("console", show_closed=True)
    console_output = console_formatter.format(result)
    print("Console Format:")
    print(console_output)
    
    # JSON format
    json_formatter = get_formatter("json")
    json_output = json_formatter.format(result)
    print("\nJSON Format:")
    print(json_output)
    
    # CSV format
    csv_formatter = get_formatter("csv")
    csv_output = csv_formatter.format(result)
    print("\nCSV Format:")
    print(csv_output)


async def error_handling():
    """Demonstrate error handling."""
    print("\n=== Error Handling ===")
    
    scanner = PortScanner()
    
    try:
        # This will raise an InvalidTargetError
        result = await scanner.scan("", [80])
    except Exception as e:
        print(f"Error: {e}")
        print(f"Error Code: {getattr(e, 'error_code', 'N/A')}")
    
    try:
        # This will raise an InvalidTargetError for invalid ports
        result = await scanner.scan("127.0.0.1", "invalid")
    except Exception as e:
        print(f"Error: {e}")
        print(f"Error Code: {getattr(e, 'error_code', 'N/A')}")


async def service_detection():
    """Demonstrate service detection capabilities."""
    print("\n=== Service Detection ===")
    
    scanner = PortScanner()
    
    # Scan with service detection
    result = await scanner.scan("127.0.0.1", [80, 443, 22, 21, 25], service_detection=True)
    
    print("Service Detection Results:")
    for port_result in result.open_ports:
        if port_result.service:
            service = port_result.service
            print(f"Port {port_result.port}:")
            print(f"  Service: {service.name}")
            print(f"  Type: {service.service_type.value}")
            print(f"  Version: {service.version or 'Unknown'}")
            print(f"  Confidence: {service.confidence:.1%}")
            if service.banner:
                print(f"  Banner: {service.banner[:50]}...")
            print()


async def main():
    """Run all examples."""
    print("ScanHero Usage Examples")
    print("=" * 50)
    
    await basic_scan()
    await custom_config_scan()
    await output_formats()
    await error_handling()
    await service_detection()
    
    print("\nExamples completed!")


if __name__ == "__main__":
    asyncio.run(main())
