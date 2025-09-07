# ScanHero

A modern, lightweight, and modular Python package for basic port and service scanning in cybersecurity contexts. ScanHero provides fast asynchronous port scanning capabilities with service detection, multiple output formats, and both CLI and Python API interfaces.

## Features

- **Fast Asynchronous Scanning**: Built on asyncio for high-performance concurrent port scanning
- **Service Detection**: Automatically detects common services (HTTP, HTTPS, SSH, FTP, SMTP, DNS, etc.)
- **Multiple Output Formats**: Console (with colors), JSON, and CSV output formats
- **Command-Line Interface**: Easy-to-use CLI with comprehensive options
- **Python API**: Clean, type-hinted API for integration into other projects
- **Modern Error Handling**: Comprehensive error handling with custom exceptions
- **Extensible Design**: Ready for future AI-powered features like anomaly detection

## Installation

### From PyPI (when published)

```bash
pip install scanhero
```

### From Source

```bash
git clone https://github.com/ahmetxhero/scanhero.git
cd scanhero
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/ahmetxhero/scanhero.git
cd scanhero
pip install -e ".[dev]"
```

## Quick Start

### Command Line Usage

```bash
# Basic scan
scanhero scan 192.168.1.1 --ports 80,443,22

# Scan port range
scanhero scan example.com --ports 1-1000

# JSON output
scanhero scan 10.0.0.1 --ports 80,443 --format json --output results.json

# Verbose output with service detection
scanhero scan target.com --ports 1-1000 --verbose --show-closed
```

### Python API Usage

```python
import asyncio
from scanhero import PortScanner, ScanConfig

async def main():
    # Create scanner with custom configuration
    config = ScanConfig(
        timeout=3.0,
        max_concurrent=100,
        service_detection=True
    )
    scanner = PortScanner(config)
    
    # Scan target
    result = await scanner.scan("192.168.1.1", [80, 443, 22])
    
    # Print results
    print(f"Scanned {result.target}")
    print(f"Found {result.open_count} open ports")
    print(f"Scan completed in {result.scan_duration:.2f}s")
    
    # Access individual port results
    for port_result in result.open_ports:
        print(f"Port {port_result.port}: {port_result.status.value}")
        if port_result.service:
            print(f"  Service: {port_result.service.name}")
            if port_result.service.version:
                print(f"  Version: {port_result.service.version}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Command Line Interface

### Scan Command

```bash
scanhero scan <target> [options]
```

#### Required Arguments

- `target`: Target host or IP address to scan

#### Optional Arguments

- `--ports, -p`: Ports to scan (default: 1-1000)
  - Single port: `80`
  - Multiple ports: `80,443,22`
  - Port range: `1-1000`
  - Mixed: `80,443,8080-8082`

- `--format, -f`: Output format (`console`, `json`, `csv`)
- `--output, -o`: Output file path (default: stdout)

#### Scan Options

- `--timeout, -t`: Connection timeout in seconds (default: 3.0)
- `--max-concurrent, -c`: Maximum concurrent connections (default: 100)
- `--retry-count, -r`: Number of retries for failed connections (default: 1)
- `--no-service-detection`: Disable service detection
- `--no-banner-grab`: Disable banner grabbing
- `--scan-delay`: Delay between scans in seconds (default: 0.0)

#### Display Options

- `--show-closed`: Show closed ports in console output
- `--show-filtered`: Show filtered ports in console output
- `--verbose, -v`: Enable verbose logging

## Python API Reference

### PortScanner

The main scanner class for performing port scans.

```python
from scanhero import PortScanner, ScanConfig

scanner = PortScanner(config=ScanConfig())
result = await scanner.scan(target, ports, service_detection=True)
```

#### Methods

- `scan(target, ports, service_detection=None)`: Perform port scan
  - `target`: Target host or IP address
  - `ports`: Port(s) to scan (int, list, or range string)
  - `service_detection`: Override service detection setting
  - Returns: `ScanResult` object

### ScanConfig

Configuration class for scanner behavior.

```python
config = ScanConfig(
    timeout=3.0,           # Connection timeout
    max_concurrent=100,    # Max concurrent connections
    retry_count=1,         # Retry attempts
    service_detection=True, # Enable service detection
    banner_grab=True,      # Enable banner grabbing
    scan_delay=0.0        # Delay between scans
)
```

### ScanResult

Result object containing scan information.

```python
result = await scanner.scan("192.168.1.1", [80, 443])

# Properties
result.target          # Target that was scanned
result.scan_duration  # Scan duration in seconds
result.timestamp     # Scan timestamp
result.total_ports   # Total ports scanned
result.open_count    # Number of open ports
result.closed_count  # Number of closed ports
result.filtered_count # Number of filtered ports

# Collections
result.open_ports     # List of open PortResult objects
result.closed_ports   # List of closed PortResult objects
result.filtered_ports # List of filtered PortResult objects
result.errors         # List of error messages

# Methods
result.get_port_result(port)  # Get result for specific port
result.get_services()         # Get all detected services
```

### PortResult

Individual port scan result.

```python
port_result = result.open_ports[0]

port_result.port          # Port number
port_result.status        # PortStatus enum (OPEN, CLOSED, FILTERED, UNKNOWN)
port_result.service       # ServiceInfo object (if detected)
port_result.response_time # Response time in milliseconds
port_result.error         # Error message (if any)
```

### ServiceInfo

Service detection information.

```python
service = port_result.service

service.service_type  # ServiceType enum
service.name          # Human-readable service name
service.version       # Service version (if detected)
service.banner        # Raw banner information
service.confidence    # Detection confidence (0.0 to 1.0)
```

## Output Formats

### Console Format

Rich, colored console output with tables and panels:

```
┌─ ScanHero Port Scanner Results ─┐
│ Target: 192.168.1.1            │
│ Scan Duration: 2.34s           │
│ Timestamp: 2024-01-15T10:30:00 │
└─────────────────────────────────┘

┌─ Scan Summary ─┐
│ Metric           │ Count │
├──────────────────┼───────┤
│ Total Ports      │   100 │
│ Open Ports       │     3 │
│ Closed Ports     │    95 │
│ Filtered Ports   │     2 │
└──────────────────┴───────┘
```

### JSON Format

Machine-readable JSON output:

```json
{
  "target": "192.168.1.1",
  "scan_duration": 2.34,
  "timestamp": "2024-01-15T10:30:00",
  "summary": {
    "total_ports": 100,
    "open_ports": 3,
    "closed_ports": 95,
    "filtered_ports": 2
  },
  "ports": {
    "open": [
      {
        "port": 80,
        "status": "open",
        "response_time": 15.5,
        "service": {
          "type": "http",
          "name": "HTTP",
          "version": "2.4.41",
          "banner": "Apache/2.4.41 (Ubuntu)",
          "confidence": 0.9
        }
      }
    ]
  }
}
```

### CSV Format

Spreadsheet-compatible CSV output:

```csv
Target,Port,Status,Service,Version,Response Time (ms),Confidence,Banner,Error
192.168.1.1,80,open,HTTP,2.4.41,15.5,0.90,Apache/2.4.41 (Ubuntu),
192.168.1.1,443,closed,,,,,,
```

## Supported Services

ScanHero can detect the following services:

- **Web Services**: HTTP, HTTPS
- **Remote Access**: SSH, Telnet
- **File Transfer**: FTP
- **Email**: SMTP, POP3, IMAP
- **Network Services**: DNS, SNMP, LDAP
- **Databases**: MySQL, PostgreSQL, Redis, MongoDB
- **Search**: Elasticsearch

## Error Handling

ScanHero provides comprehensive error handling with custom exceptions:

```python
from scanhero.exceptions import (
    ScanHeroError,
    ScanTimeoutError,
    InvalidTargetError,
    ServiceDetectionError,
    ConfigurationError
)

try:
    result = await scanner.scan("invalid-target", [80])
except InvalidTargetError as e:
    print(f"Invalid target: {e.message}")
except ScanTimeoutError as e:
    print(f"Scan timed out: {e.message}")
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=scanhero --cov-report=html

# Run specific test file
pytest tests/test_scanner.py
```

### Code Quality

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

### Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Roadmap

- [ ] AI-powered anomaly detection
- [ ] Adaptive scanning strategies
- [ ] Vulnerability assessment integration
- [ ] Network topology mapping
- [ ] Performance optimization
- [ ] Additional service detection
- [ ] Plugin system for custom detectors

## Support

- **Documentation**: [https://scanhero.readthedocs.io](https://scanhero.readthedocs.io)
- **Issues**: [GitHub Issues](https://github.com/ahmetxhero/scanhero/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ahmetxhero/scanhero/discussions)

## Acknowledgments

- Built with modern Python async/await patterns
- Inspired by nmap and other network scanning tools
- Designed for cybersecurity professionals and developers
