"""Tests for the ServiceDetector class."""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from scanhero.service_detector import ServiceDetector
from scanhero.models import ServiceType, ServiceInfo
from scanhero.exceptions import ServiceDetectionError


class TestServiceDetector:
    """Test cases for ServiceDetector class."""
    
    @pytest.fixture
    def detector(self):
        """Create a ServiceDetector instance for testing."""
        return ServiceDetector(timeout=1.0)
    
    def test_init(self):
        """Test ServiceDetector initialization."""
        detector = ServiceDetector(timeout=2.0)
        assert detector.timeout == 2.0
    
    def test_port_services_mapping(self, detector):
        """Test port to service mapping."""
        assert detector.PORT_SERVICES[80] == ServiceType.HTTP
        assert detector.PORT_SERVICES[443] == ServiceType.HTTPS
        assert detector.PORT_SERVICES[22] == ServiceType.SSH
        assert detector.PORT_SERVICES[21] == ServiceType.FTP
    
    def test_service_names_mapping(self, detector):
        """Test service type to name mapping."""
        assert detector.SERVICE_NAMES[ServiceType.HTTP] == "HTTP"
        assert detector.SERVICE_NAMES[ServiceType.SSH] == "SSH"
        assert detector.SERVICE_NAMES[ServiceType.UNKNOWN] == "Unknown"
    
    @pytest.mark.asyncio
    async def test_detect_service_known_port(self, detector):
        """Test service detection for known port."""
        with patch.object(detector, '_grab_banner') as mock_banner:
            mock_banner.return_value = "HTTP/1.1 200 OK"
            
            result = await detector.detect_service("127.0.0.1", 80)
            
            assert result is not None
            assert result.service_type == ServiceType.HTTP
            assert result.name == "HTTP"
            assert result.banner == "HTTP/1.1 200 OK"
            assert result.confidence == 0.9
    
    @pytest.mark.asyncio
    async def test_detect_service_unknown_port(self, detector):
        """Test service detection for unknown port."""
        with patch.object(detector, '_grab_banner') as mock_banner:
            mock_banner.return_value = None
            
            result = await detector.detect_service("127.0.0.1", 9999)
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_detect_service_with_banner(self, detector):
        """Test service detection with banner for unknown port."""
        with patch.object(detector, '_grab_banner') as mock_banner:
            mock_banner.return_value = "SSH-2.0-OpenSSH_8.0"
            
            result = await detector.detect_service("127.0.0.1", 9999)
            
            assert result is not None
            assert result.service_type == ServiceType.SSH
            assert result.name == "SSH"
            assert result.banner == "SSH-2.0-OpenSSH_8.0"
            assert result.confidence == 0.6
    
    @pytest.mark.asyncio
    async def test_detect_service_error(self, detector):
        """Test service detection error handling."""
        with patch.object(detector, '_grab_banner') as mock_banner:
            mock_banner.side_effect = Exception("Connection failed")
            
            with pytest.raises(ServiceDetectionError):
                await detector.detect_service("127.0.0.1", 80)
    
    @pytest.mark.asyncio
    async def test_grab_banner_success(self, detector):
        """Test successful banner grabbing."""
        with patch('asyncio.open_connection') as mock_conn:
            mock_reader = AsyncMock()
            mock_writer = AsyncMock()
            mock_reader.read.return_value = b"HTTP/1.1 200 OK\r\n"
            mock_conn.return_value = (mock_reader, mock_writer)
            
            banner = await detector._grab_banner("127.0.0.1", 80)
            
            assert banner == "HTTP/1.1 200 OK"
            mock_writer.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_grab_banner_timeout(self, detector):
        """Test banner grabbing timeout."""
        with patch('asyncio.open_connection') as mock_conn:
            mock_conn.side_effect = asyncio.TimeoutError()
            
            banner = await detector._grab_banner("127.0.0.1", 80)
            
            assert banner is None
    
    @pytest.mark.asyncio
    async def test_grab_banner_connection_refused(self, detector):
        """Test banner grabbing with connection refused."""
        with patch('asyncio.open_connection') as mock_conn:
            mock_conn.side_effect = ConnectionRefusedError()
            
            banner = await detector._grab_banner("127.0.0.1", 80)
            
            assert banner is None
    
    def test_get_probe_data(self, detector):
        """Test probe data generation."""
        assert detector._get_probe_data(21) == "QUIT\r\n"  # FTP
        assert detector._get_probe_data(25) == "QUIT\r\n"  # SMTP
        assert detector._get_probe_data(80) is None  # HTTP (no probe)
        assert detector._get_probe_data(9999) is None  # Unknown port
    
    def test_extract_version(self, detector):
        """Test version extraction from banner."""
        # Test with version in banner
        banner = "Apache/2.4.41 (Ubuntu)"
        version = detector._extract_version(banner, ServiceType.HTTP)
        assert version == "2.4.41"
        
        # Test with HTTP version (should extract HTTP version)
        banner = "HTTP/1.1 200 OK"
        version = detector._extract_version(banner, ServiceType.HTTP)
        assert version == "1.1"
        
        # Test with no version
        banner = "Server response without version"
        version = detector._extract_version(banner, ServiceType.HTTP)
        assert version is None
        
        # Test with None banner
        version = detector._extract_version(None, ServiceType.HTTP)
        assert version is None
    
    def test_identify_from_banner(self, detector):
        """Test service identification from banner."""
        # Test HTTP identification
        banner = "HTTP/1.1 200 OK Server: Apache/2.4.41"
        service_type = detector._identify_from_banner(banner)
        assert service_type == ServiceType.HTTP
        
        # Test SSH identification
        banner = "SSH-2.0-OpenSSH_8.0"
        service_type = detector._identify_from_banner(banner)
        assert service_type == ServiceType.SSH
        
        # Test unknown service
        banner = "Some unknown service response"
        service_type = detector._identify_from_banner(banner)
        assert service_type == ServiceType.UNKNOWN
