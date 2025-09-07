"""Command-line interface for ScanHero."""

import argparse
import asyncio
import logging
import sys
from typing import List, Optional
from .scanner import PortScanner
from .models import ScanConfig
from .formatters import get_formatter
from .exceptions import ScanHeroError


def setup_logging(verbose: bool = False) -> None:
    """Set up logging configuration.
    
    Args:
        verbose: Whether to enable verbose logging.
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def parse_ports(ports_str: str) -> List[int]:
    """Parse ports string into list of integers.
    
    Args:
        ports_str: Ports specification string.
        
    Returns:
        List of port numbers.
    """
    ports = []
    for part in ports_str.split(','):
        part = part.strip()
        if '-' in part:
            start, end = map(int, part.split('-'))
            ports.extend(range(start, end + 1))
        else:
            ports.append(int(part))
    return ports


def create_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser.
    
    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        prog='scanhero',
        description='A modern, lightweight port scanner for cybersecurity contexts',
        epilog='Examples:\n'
               '  scanhero scan 192.168.1.1 --ports 80,443,22\n'
               '  scanhero scan example.com --ports 1-1000 --format json\n'
               '  scanhero scan 10.0.0.1 --ports 80 --no-service-detection',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Scan target for open ports')
    
    # Required arguments
    scan_parser.add_argument(
        'target',
        help='Target host or IP address to scan'
    )
    
    scan_parser.add_argument(
        '--ports', '-p',
        default='1-1000',
        help='Ports to scan (default: 1-1000). Can be comma-separated or ranges (e.g., 80,443,8080 or 1-1000)'
    )
    
    # Output options
    scan_parser.add_argument(
        '--format', '-f',
        choices=['console', 'json', 'csv'],
        default='console',
        help='Output format (default: console)'
    )
    
    scan_parser.add_argument(
        '--output', '-o',
        help='Output file path (default: stdout)'
    )
    
    # Scan options
    scan_parser.add_argument(
        '--timeout', '-t',
        type=float,
        default=3.0,
        help='Connection timeout in seconds (default: 3.0)'
    )
    
    scan_parser.add_argument(
        '--max-concurrent', '-c',
        type=int,
        default=100,
        help='Maximum concurrent connections (default: 100)'
    )
    
    scan_parser.add_argument(
        '--retry-count', '-r',
        type=int,
        default=1,
        help='Number of retries for failed connections (default: 1)'
    )
    
    scan_parser.add_argument(
        '--no-service-detection',
        action='store_true',
        help='Disable service detection'
    )
    
    scan_parser.add_argument(
        '--no-banner-grab',
        action='store_true',
        help='Disable banner grabbing'
    )
    
    scan_parser.add_argument(
        '--scan-delay',
        type=float,
        default=0.0,
        help='Delay between scans in seconds (default: 0.0)'
    )
    
    # Display options
    scan_parser.add_argument(
        '--show-closed',
        action='store_true',
        help='Show closed ports in console output'
    )
    
    scan_parser.add_argument(
        '--show-filtered',
        action='store_true',
        help='Show filtered ports in console output'
    )
    
    # General options
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    return parser


async def run_scan(args: argparse.Namespace) -> int:
    """Run port scan with given arguments.
    
    Args:
        args: Parsed command-line arguments.
        
    Returns:
        Exit code (0 for success, 1 for error).
    """
    try:
        # Parse ports
        ports = parse_ports(args.ports)
        
        # Create scan configuration
        config = ScanConfig(
            timeout=args.timeout,
            max_concurrent=args.max_concurrent,
            retry_count=args.retry_count,
            service_detection=not args.no_service_detection,
            banner_grab=not args.no_banner_grab,
            scan_delay=args.scan_delay
        )
        
        # Create scanner
        scanner = PortScanner(config)
        
        # Perform scan
        print(f"Scanning {args.target} on ports {args.ports}...", file=sys.stderr)
        result = await scanner.scan(args.target, ports)
        
        # Format output
        formatter_kwargs = {}
        if args.format == 'console':
            formatter_kwargs.update({
                'show_closed': args.show_closed,
                'show_filtered': args.show_filtered
            })
        
        formatter = get_formatter(args.format, **formatter_kwargs)
        output = formatter.format(result)
        
        # Write output
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"Results saved to {args.output}", file=sys.stderr)
        else:
            print(output)
        
        # Print summary to stderr
        print(f"\nScan completed in {result.scan_duration:.2f}s", file=sys.stderr)
        print(f"Found {result.open_count} open ports out of {result.total_ports} scanned", file=sys.stderr)
        
        return 0
        
    except ScanHeroError as e:
        print(f"Error: {e.message}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nScan interrupted by user", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def main() -> int:
    """Main entry point for CLI.
    
    Returns:
        Exit code (0 for success, 1 for error).
    """
    parser = create_parser()
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.verbose)
    
    # Handle no command
    if not args.command:
        parser.print_help()
        return 1
    
    # Run command
    if args.command == 'scan':
        return asyncio.run(run_scan(args))
    
    return 1


if __name__ == '__main__':
    sys.exit(main())
