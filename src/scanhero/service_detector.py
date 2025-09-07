"""Service detection module for ScanHero."""

import asyncio
import socket
from typing import Dict, Optional, Tuple
from .models import ServiceInfo, ServiceType
from .exceptions import ServiceDetectionError


class ServiceDetector:
    """Service detector for identifying services running on open ports."""
    
    # Common port mappings
    PORT_SERVICES: Dict[int, ServiceType] = {
        21: ServiceType.FTP,
        22: ServiceType.SSH,
        23: ServiceType.TELNET,
        25: ServiceType.SMTP,
        53: ServiceType.DNS,
        80: ServiceType.HTTP,
        110: ServiceType.POP3,
        143: ServiceType.IMAP,
        443: ServiceType.HTTPS,
        993: ServiceType.IMAP,
        995: ServiceType.POP3,
        3306: ServiceType.MYSQL,
        5432: ServiceType.POSTGRESQL,
        6379: ServiceType.REDIS,
        27017: ServiceType.MONGODB,
        9200: ServiceType.ELASTICSEARCH,
        389: ServiceType.LDAP,
        161: ServiceType.SNMP,
    }
    
    # Service names mapping
    SERVICE_NAMES: Dict[ServiceType, str] = {
        ServiceType.HTTP: "HTTP",
        ServiceType.HTTPS: "HTTPS",
        ServiceType.SSH: "SSH",
        ServiceType.FTP: "FTP",
        ServiceType.SMTP: "SMTP",
        ServiceType.DNS: "DNS",
        ServiceType.TELNET: "Telnet",
        ServiceType.POP3: "POP3",
        ServiceType.IMAP: "IMAP",
        ServiceType.SNMP: "SNMP",
        ServiceType.LDAP: "LDAP",
        ServiceType.MYSQL: "MySQL",
        ServiceType.POSTGRESQL: "PostgreSQL",
        ServiceType.REDIS: "Redis",
        ServiceType.MONGODB: "MongoDB",
        ServiceType.ELASTICSEARCH: "Elasticsearch",
        ServiceType.UNKNOWN: "Unknown",
    }
    
    def __init__(self, timeout: float = 3.0) -> None:
        """Initialize service detector.
        
        Args:
            timeout: Connection timeout for service detection.
        """
        self.timeout = timeout
    
    async def detect_service(self, host: str, port: int) -> Optional[ServiceInfo]:
        """Detect service running on a specific port.
        
        Args:
            host: Target host or IP address.
            port: Port number to check.
            
        Returns:
            ServiceInfo if service is detected, None otherwise.
            
        Raises:
            ServiceDetectionError: If service detection fails.
        """
        try:
            # First, try to identify service by port number
            service_type = self.PORT_SERVICES.get(port, ServiceType.UNKNOWN)
            
            # If it's a known service port, try banner grabbing
            if service_type != ServiceType.UNKNOWN:
                banner = await self._grab_banner(host, port)
                version = self._extract_version(banner, service_type)
                
                return ServiceInfo(
                    service_type=service_type,
                    name=self.SERVICE_NAMES[service_type],
                    version=version,
                    banner=banner,
                    confidence=0.9 if banner else 0.7
                )
            
            # For unknown ports, try to grab any banner
            banner = await self._grab_banner(host, port)
            if banner:
                # Try to identify service from banner
                service_type = self._identify_from_banner(banner)
                return ServiceInfo(
                    service_type=service_type,
                    name=self.SERVICE_NAMES[service_type],
                    banner=banner,
                    confidence=0.6
                )
            
            return None
            
        except Exception as e:
            raise ServiceDetectionError(f"Service detection failed for {host}:{port}: {str(e)}")
    
    async def _grab_banner(self, host: str, port: int) -> Optional[str]:
        """Grab banner from a service.
        
        Args:
            host: Target host or IP address.
            port: Port number to connect to.
            
        Returns:
            Banner string if successful, None otherwise.
        """
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port),
                timeout=self.timeout
            )
            
            # Send a simple probe for some services
            probe_data = self._get_probe_data(port)
            if probe_data:
                writer.write(probe_data.encode())
                await writer.drain()
            
            # Try to read response
            try:
                banner = await asyncio.wait_for(
                    reader.read(1024),
                    timeout=self.timeout
                )
                banner_str = banner.decode('utf-8', errors='ignore').strip()
                return banner_str if banner_str else None
            except asyncio.TimeoutError:
                return None
            finally:
                writer.close()
                await writer.wait_closed()
                
        except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
            return None
    
    def _get_probe_data(self, port: int) -> Optional[str]:
        """Get probe data to send for specific services.
        
        Args:
            port: Port number.
            
        Returns:
            Probe data string or None.
        """
        probes = {
            21: "QUIT\r\n",  # FTP
            25: "QUIT\r\n",  # SMTP
            110: "QUIT\r\n",  # POP3
            143: "A1 LOGOUT\r\n",  # IMAP
            993: "A1 LOGOUT\r\n",  # IMAPS
            995: "QUIT\r\n",  # POP3S
            161: "\x30\x0c\x02\x01\x00\x04\x06public\xa0\x05\x02\x03\x00\x00\x00",  # SNMP
        }
        return probes.get(port)
    
    def _extract_version(self, banner: Optional[str], service_type: ServiceType) -> Optional[str]:
        """Extract version information from banner.
        
        Args:
            banner: Banner string from service.
            service_type: Type of service.
            
        Returns:
            Version string if found, None otherwise.
        """
        if not banner:
            return None
        
        banner_lower = banner.lower()
        
        # Common version patterns
        version_patterns = [
            r'version\s+([0-9]+\.[0-9]+(?:\.[0-9]+)?)',
            r'v([0-9]+\.[0-9]+(?:\.[0-9]+)?)',
            r'([0-9]+\.[0-9]+(?:\.[0-9]+)?)',
        ]
        
        import re
        for pattern in version_patterns:
            match = re.search(pattern, banner_lower)
            if match:
                return match.group(1)
        
        return None
    
    def _identify_from_banner(self, banner: str) -> ServiceType:
        """Identify service type from banner.
        
        Args:
            banner: Banner string from service.
            
        Returns:
            Identified service type.
        """
        banner_lower = banner.lower()
        
        # Service identification patterns
        patterns = {
            ServiceType.HTTP: ['http', 'apache', 'nginx', 'iis'],
            ServiceType.HTTPS: ['https', 'ssl', 'tls'],
            ServiceType.SSH: ['ssh', 'openssh'],
            ServiceType.FTP: ['ftp', 'vsftpd', 'proftpd'],
            ServiceType.SMTP: ['smtp', 'postfix', 'sendmail'],
            ServiceType.DNS: ['dns', 'bind'],
            ServiceType.MYSQL: ['mysql'],
            ServiceType.POSTGRESQL: ['postgresql', 'postgres'],
            ServiceType.REDIS: ['redis'],
            ServiceType.MONGODB: ['mongodb'],
            ServiceType.ELASTICSEARCH: ['elasticsearch'],
        }
        
        for service_type, keywords in patterns.items():
            if any(keyword in banner_lower for keyword in keywords):
                return service_type
        
        return ServiceType.UNKNOWN
