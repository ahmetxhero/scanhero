"""Tests for output formatters."""

import pytest
import json
from datetime import datetime
from scanhero.formatters import ConsoleFormatter, JSONFormatter, CSVFormatter, get_formatter
from scanhero.models import ScanResult, PortResult, PortStatus, ServiceInfo, ServiceType


class TestFormatters:
    """Test cases for output formatters."""
    
    @pytest.fixture
    def sample_result(self):
        """Create a sample ScanResult for testing."""
        service = ServiceInfo(
            service_type=ServiceType.HTTP,
            name="HTTP",
            version="2.4.41",
            banner="Apache/2.4.41 (Ubuntu)",
            confidence=0.9
        )
        
        open_port = PortResult(
            port=80,
            status=PortStatus.OPEN,
            service=service,
            response_time=15.5
        )
        
        closed_port = PortResult(
            port=443,
            status=PortStatus.CLOSED,
            response_time=5.2
        )
        
        return ScanResult(
            target="127.0.0.1",
            ports_scanned=[80, 443],
            open_ports=[open_port],
            closed_ports=[closed_port],
            filtered_ports=[],
            scan_duration=2.5,
            timestamp=datetime.now().isoformat(),
            errors=[]
        )
    
    def test_console_formatter_init(self):
        """Test ConsoleFormatter initialization."""
        formatter = ConsoleFormatter(show_closed=True, show_filtered=True)
        assert formatter.show_closed is True
        assert formatter.show_filtered is True
    
    def test_console_formatter_format(self, sample_result):
        """Test ConsoleFormatter format method."""
        formatter = ConsoleFormatter()
        output = formatter.format(sample_result)
        
        assert "ScanHero Port Scanner Results" in output
        assert "127.0.0.1" in output
        assert "Scan Summary" in output
        assert "Open Ports" in output
        assert "Detected Services" in output
    
    def test_console_formatter_with_closed(self, sample_result):
        """Test ConsoleFormatter with closed ports shown."""
        formatter = ConsoleFormatter(show_closed=True)
        output = formatter.format(sample_result)
        
        assert "Closed Ports" in output
    
    def test_json_formatter_format(self, sample_result):
        """Test JSONFormatter format method."""
        formatter = JSONFormatter()
        output = formatter.format(sample_result)
        
        # Parse JSON to verify structure
        data = json.loads(output)
        
        assert data["target"] == "127.0.0.1"
        assert data["scan_duration"] == 2.5
        assert "summary" in data
        assert "ports" in data
        assert "services" in data
        assert "errors" in data
        
        # Check summary
        summary = data["summary"]
        assert summary["total_ports"] == 2
        assert summary["open_ports"] == 1
        assert summary["closed_ports"] == 1
        assert summary["filtered_ports"] == 0
        
        # Check ports
        assert len(data["ports"]["open"]) == 1
        assert len(data["ports"]["closed"]) == 1
        assert len(data["ports"]["filtered"]) == 0
        
        # Check open port details
        open_port = data["ports"]["open"][0]
        assert open_port["port"] == 80
        assert open_port["status"] == "open"
        assert open_port["response_time"] == 15.5
        assert "service" in open_port
        
        # Check service details
        service = open_port["service"]
        assert service["type"] == "http"
        assert service["name"] == "HTTP"
        assert service["version"] == "2.4.41"
        assert service["banner"] == "Apache/2.4.41 (Ubuntu)"
        assert service["confidence"] == 0.9
    
    def test_csv_formatter_format(self, sample_result):
        """Test CSVFormatter format method."""
        formatter = CSVFormatter()
        output = formatter.format(sample_result)
        
        lines = output.strip().split('\n')
        assert len(lines) == 3  # Header + 2 data rows
        
        # Check header
        header = lines[0]
        expected_columns = [
            "Target", "Port", "Status", "Service", "Version",
            "Response Time (ms)", "Confidence", "Banner", "Error"
        ]
        for column in expected_columns:
            assert column in header
        
        # Check data rows
        open_row = lines[1]
        assert "127.0.0.1" in open_row
        assert "80" in open_row
        assert "open" in open_row
        assert "HTTP" in open_row
        assert "2.4.41" in open_row
        
        closed_row = lines[2]
        assert "127.0.0.1" in closed_row
        assert "443" in closed_row
        assert "closed" in closed_row
    
    def test_get_formatter_console(self):
        """Test get_formatter with console type."""
        formatter = get_formatter("console", show_closed=True)
        assert isinstance(formatter, ConsoleFormatter)
        assert formatter.show_closed is True
    
    def test_get_formatter_json(self):
        """Test get_formatter with json type."""
        formatter = get_formatter("json")
        assert isinstance(formatter, JSONFormatter)
    
    def test_get_formatter_csv(self):
        """Test get_formatter with csv type."""
        formatter = get_formatter("csv")
        assert isinstance(formatter, CSVFormatter)
    
    def test_get_formatter_invalid(self):
        """Test get_formatter with invalid type."""
        with pytest.raises(ValueError):
            get_formatter("invalid")
    
    def test_json_formatter_with_errors(self, sample_result):
        """Test JSONFormatter with errors."""
        sample_result.errors = ["Connection timeout", "Invalid target"]
        
        formatter = JSONFormatter()
        output = formatter.format(sample_result)
        
        data = json.loads(output)
        assert data["errors"] == ["Connection timeout", "Invalid target"]
    
    def test_csv_formatter_with_errors(self, sample_result):
        """Test CSVFormatter with errors."""
        error_port = PortResult(
            port=9999,
            status=PortStatus.UNKNOWN,
            error="Connection timeout"
        )
        sample_result.filtered_ports = [error_port]
        
        formatter = CSVFormatter()
        output = formatter.format(sample_result)
        
        lines = output.strip().split('\n')
        assert len(lines) == 4  # Header + 3 data rows
        
        # Check error row
        error_row = lines[3]
        assert "9999" in error_row
        assert "unknown" in error_row
        assert "Connection timeout" in error_row
