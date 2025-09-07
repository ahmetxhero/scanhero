"""Tests for the PortScanner class."""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from scanhero.scanner import PortScanner
from scanhero.models import ScanConfig, PortStatus, ServiceType
from scanhero.exceptions import InvalidTargetError, ScanTimeoutError


class TestPortScanner:
    """Test cases for PortScanner class."""
    
    @pytest.fixture
    def scanner(self):
        """Create a PortScanner instance for testing."""
        config = ScanConfig(timeout=1.0, max_concurrent=10)
        return PortScanner(config)
    
    @pytest.fixture
    def mock_service_detector(self):
        """Create a mock service detector."""
        return AsyncMock()
    
    def test_init(self):
        """Test PortScanner initialization."""
        config = ScanConfig(timeout=2.0)
        scanner = PortScanner(config)
        assert scanner.config == config
        assert scanner.config.timeout == 2.0
    
    def test_init_default_config(self):
        """Test PortScanner initialization with default config."""
        scanner = PortScanner()
        assert isinstance(scanner.config, ScanConfig)
        assert scanner.config.timeout == 3.0
    
    def test_validate_target_valid(self, scanner):
        """Test target validation with valid targets."""
        valid_targets = ["192.168.1.1", "example.com", "localhost"]
        for target in valid_targets:
            result = scanner._validate_target(target)
            assert result == target
    
    def test_validate_target_invalid(self, scanner):
        """Test target validation with invalid targets."""
        invalid_targets = ["", "   ", None, "a" * 256]
        for target in invalid_targets:
            with pytest.raises(InvalidTargetError):
                scanner._validate_target(target)
    
    def test_parse_ports_int(self, scanner):
        """Test port parsing with integer input."""
        result = scanner._parse_ports(80)
        assert result == [80]
    
    def test_parse_ports_list(self, scanner):
        """Test port parsing with list input."""
        result = scanner._parse_ports([80, 443, 22])
        assert result == [80, 443, 22]
    
    def test_parse_ports_range(self, scanner):
        """Test port parsing with range string."""
        result = scanner._parse_ports("80-82")
        assert result == [80, 81, 82]
    
    def test_parse_ports_mixed(self, scanner):
        """Test port parsing with mixed format."""
        result = scanner._parse_ports("80,443,8080-8082")
        assert result == [80, 443, 8080, 8081, 8082]
    
    def test_parse_ports_invalid(self, scanner):
        """Test port parsing with invalid input."""
        with pytest.raises(InvalidTargetError):
            scanner._parse_ports("invalid")
        
        with pytest.raises(InvalidTargetError):
            scanner._parse_ports([80, 0])  # Port 0 is invalid
        
        with pytest.raises(InvalidTargetError):
            scanner._parse_ports([80, 65536])  # Port 65536 is invalid
    
    @pytest.mark.asyncio
    async def test_check_port_status_open(self, scanner):
        """Test port status check for open port."""
        with patch('asyncio.open_connection') as mock_conn:
            mock_reader = AsyncMock()
            mock_writer = AsyncMock()
            mock_conn.return_value = (mock_reader, mock_writer)
            
            status = await scanner._check_port_status("127.0.0.1", 80)
            assert status == PortStatus.OPEN
    
    @pytest.mark.asyncio
    async def test_check_port_status_closed(self, scanner):
        """Test port status check for closed port."""
        with patch('asyncio.open_connection') as mock_conn:
            mock_conn.side_effect = ConnectionRefusedError()
            
            status = await scanner._check_port_status("127.0.0.1", 80)
            assert status == PortStatus.CLOSED
    
    @pytest.mark.asyncio
    async def test_check_port_status_filtered(self, scanner):
        """Test port status check for filtered port."""
        with patch('asyncio.open_connection') as mock_conn:
            mock_conn.side_effect = asyncio.TimeoutError()
            
            status = await scanner._check_port_status("127.0.0.1", 80)
            assert status == PortStatus.FILTERED
    
    @pytest.mark.asyncio
    async def test_scan_single_port_open(self, scanner):
        """Test scanning a single open port."""
        with patch.object(scanner, '_check_port_status') as mock_check:
            mock_check.return_value = PortStatus.OPEN
            
            result = await scanner._scan_single_port("127.0.0.1", 80, False)
            
            assert result.port == 80
            assert result.status == PortStatus.OPEN
            assert result.response_time is not None
            assert result.service is None
    
    @pytest.mark.asyncio
    async def test_scan_single_port_with_service(self, scanner):
        """Test scanning a single port with service detection."""
        with patch.object(scanner, '_check_port_status') as mock_check:
            with patch.object(scanner.service_detector, 'detect_service') as mock_detect:
                mock_check.return_value = PortStatus.OPEN
                mock_service = MagicMock()
                mock_service.name = "HTTP"
                mock_detect.return_value = mock_service
                
                result = await scanner._scan_single_port("127.0.0.1", 80, True)
                
                assert result.port == 80
                assert result.status == PortStatus.OPEN
                assert result.service == mock_service
    
    @pytest.mark.asyncio
    async def test_scan_single_port_error(self, scanner):
        """Test scanning a single port with error."""
        with patch.object(scanner, '_check_port_status') as mock_check:
            mock_check.side_effect = Exception("Test error")
            
            result = await scanner._scan_single_port("127.0.0.1", 80, False)
            
            assert result.port == 80
            assert result.status == PortStatus.UNKNOWN
            assert result.error == "Test error"
    
    @pytest.mark.asyncio
    async def test_scan_ports_concurrent(self, scanner):
        """Test scanning multiple ports concurrently."""
        with patch.object(scanner, '_scan_single_port') as mock_scan:
            mock_results = [
                MagicMock(port=80, status=PortStatus.OPEN),
                MagicMock(port=443, status=PortStatus.CLOSED),
                MagicMock(port=22, status=PortStatus.OPEN)
            ]
            mock_scan.side_effect = mock_results
            
            results = await scanner._scan_ports("127.0.0.1", [80, 443, 22], False)
            
            assert len(results) == 3
            assert mock_scan.call_count == 3
    
    @pytest.mark.asyncio
    async def test_scan_complete(self, scanner):
        """Test complete scan functionality."""
        with patch.object(scanner, '_scan_ports') as mock_scan_ports:
            mock_port_results = [
                MagicMock(port=80, status=PortStatus.OPEN),
                MagicMock(port=443, status=PortStatus.CLOSED)
            ]
            mock_scan_ports.return_value = mock_port_results
            
            result = await scanner.scan("127.0.0.1", [80, 443])
            
            assert result.target == "127.0.0.1"
            assert result.ports_scanned == [80, 443]
            assert len(result.open_ports) == 1
            assert len(result.closed_ports) == 1
            assert result.scan_duration > 0
            assert result.timestamp is not None
    
    @pytest.mark.asyncio
    async def test_scan_timeout_error(self, scanner):
        """Test scan timeout error handling."""
        with patch.object(scanner, '_scan_ports') as mock_scan_ports:
            mock_scan_ports.side_effect = asyncio.TimeoutError()
            
            with pytest.raises(ScanTimeoutError):
                await scanner.scan("127.0.0.1", [80])
    
    @pytest.mark.asyncio
    async def test_scan_invalid_target(self, scanner):
        """Test scan with invalid target."""
        with pytest.raises(InvalidTargetError):
            await scanner.scan("", [80])
    
    @pytest.mark.asyncio
    async def test_scan_invalid_ports(self, scanner):
        """Test scan with invalid ports."""
        with pytest.raises(InvalidTargetError):
            await scanner.scan("127.0.0.1", "invalid")
