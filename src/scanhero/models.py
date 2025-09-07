"""Data models for ScanHero package."""

from dataclasses import dataclass
from typing import Dict, List, Optional, Union
from enum import Enum


class PortStatus(Enum):
    """Enumeration for port status."""
    OPEN = "open"
    CLOSED = "closed"
    FILTERED = "filtered"
    UNKNOWN = "unknown"


class ServiceType(Enum):
    """Enumeration for service types."""
    HTTP = "http"
    HTTPS = "https"
    SSH = "ssh"
    FTP = "ftp"
    SMTP = "smtp"
    DNS = "dns"
    TELNET = "telnet"
    POP3 = "pop3"
    IMAP = "imap"
    SNMP = "snmp"
    LDAP = "ldap"
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    REDIS = "redis"
    MONGODB = "mongodb"
    ELASTICSEARCH = "elasticsearch"
    UNKNOWN = "unknown"


@dataclass
class ServiceInfo:
    """Information about a detected service.
    
    Attributes:
        service_type: Type of service detected.
        name: Human-readable name of the service.
        version: Version of the service if detected.
        banner: Raw banner information from the service.
        confidence: Confidence level of the detection (0.0 to 1.0).
    """
    service_type: ServiceType
    name: str
    version: Optional[str] = None
    banner: Optional[str] = None
    confidence: float = 1.0


@dataclass
class PortResult:
    """Result of scanning a single port.
    
    Attributes:
        port: Port number that was scanned.
        status: Status of the port (open, closed, filtered, unknown).
        service: Service information if detected.
        response_time: Response time in milliseconds.
        error: Error message if scanning failed.
    """
    port: int
    status: PortStatus
    service: Optional[ServiceInfo] = None
    response_time: Optional[float] = None
    error: Optional[str] = None


@dataclass
class ScanResult:
    """Complete result of a port scan operation.
    
    Attributes:
        target: Target host or IP address that was scanned.
        ports_scanned: List of ports that were scanned.
        open_ports: List of open ports found.
        closed_ports: List of closed ports found.
        filtered_ports: List of filtered ports found.
        scan_duration: Total time taken for the scan in seconds.
        timestamp: Timestamp when the scan was performed.
        errors: List of errors encountered during scanning.
    """
    target: str
    ports_scanned: List[int]
    open_ports: List[PortResult]
    closed_ports: List[PortResult]
    filtered_ports: List[PortResult]
    scan_duration: float
    timestamp: str
    errors: List[str]

    @property
    def total_ports(self) -> int:
        """Total number of ports scanned."""
        return len(self.ports_scanned)

    @property
    def open_count(self) -> int:
        """Number of open ports found."""
        return len(self.open_ports)

    @property
    def closed_count(self) -> int:
        """Number of closed ports found."""
        return len(self.closed_ports)

    @property
    def filtered_count(self) -> int:
        """Number of filtered ports found."""
        return len(self.filtered_ports)

    def get_port_result(self, port: int) -> Optional[PortResult]:
        """Get result for a specific port.
        
        Args:
            port: Port number to look up.
            
        Returns:
            PortResult for the specified port, or None if not found.
        """
        all_results = self.open_ports + self.closed_ports + self.filtered_ports
        for result in all_results:
            if result.port == port:
                return result
        return None

    def get_services(self) -> List[ServiceInfo]:
        """Get all detected services.
        
        Returns:
            List of ServiceInfo objects for detected services.
        """
        services = []
        for port_result in self.open_ports:
            if port_result.service:
                services.append(port_result.service)
        return services


@dataclass
class ScanConfig:
    """Configuration for port scanning.
    
    Attributes:
        timeout: Connection timeout in seconds.
        max_concurrent: Maximum number of concurrent connections.
        retry_count: Number of retries for failed connections.
        service_detection: Whether to perform service detection.
        banner_grab: Whether to attempt banner grabbing.
        scan_delay: Delay between scans in seconds.
    """
    timeout: float = 3.0
    max_concurrent: int = 100
    retry_count: int = 1
    service_detection: bool = True
    banner_grab: bool = True
    scan_delay: float = 0.0
