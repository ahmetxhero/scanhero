"""Core port scanner implementation for ScanHero."""

import asyncio
import socket
import time
from datetime import datetime
from typing import List, Optional, Set, Union
from .models import PortResult, PortStatus, ScanResult, ScanConfig
from .service_detector import ServiceDetector
from .exceptions import InvalidTargetError, ScanTimeoutError


class PortScanner:
    """Asynchronous port scanner with service detection capabilities."""
    
    def __init__(self, config: Optional[ScanConfig] = None) -> None:
        """Initialize port scanner.
        
        Args:
            config: Scanner configuration. If None, uses default config.
        """
        self.config = config or ScanConfig()
        self.service_detector = ServiceDetector(timeout=self.config.timeout)
        self._semaphore = asyncio.Semaphore(self.config.max_concurrent)
    
    async def scan(
        self,
        target: str,
        ports: Union[int, List[int], str],
        service_detection: Optional[bool] = None
    ) -> ScanResult:
        """Scan target host for open ports.
        
        Args:
            target: Target host or IP address to scan.
            ports: Port(s) to scan. Can be int, list of ints, or range string (e.g., "1-1000").
            service_detection: Whether to perform service detection. Overrides config.
            
        Returns:
            ScanResult containing scan results.
            
        Raises:
            InvalidTargetError: If target is invalid.
            ScanTimeoutError: If scan times out.
        """
        start_time = time.time()
        timestamp = datetime.now().isoformat()
        
        # Validate and parse target
        target = self._validate_target(target)
        
        # Parse ports
        port_list = self._parse_ports(ports)
        
        # Determine service detection setting
        detect_services = service_detection if service_detection is not None else self.config.service_detection
        
        # Perform scan
        try:
            results = await self._scan_ports(target, port_list, detect_services)
        except asyncio.TimeoutError as e:
            raise ScanTimeoutError(f"Scan timed out after {self.config.timeout} seconds") from e
        
        scan_duration = time.time() - start_time
        
        # Organize results
        open_ports = [r for r in results if r.status == PortStatus.OPEN]
        closed_ports = [r for r in results if r.status == PortStatus.CLOSED]
        filtered_ports = [r for r in results if r.status == PortStatus.FILTERED]
        
        # Collect errors
        errors = [r.error for r in results if r.error]
        
        return ScanResult(
            target=target,
            ports_scanned=port_list,
            open_ports=open_ports,
            closed_ports=closed_ports,
            filtered_ports=filtered_ports,
            scan_duration=scan_duration,
            timestamp=timestamp,
            errors=errors
        )
    
    async def _scan_ports(
        self,
        target: str,
        ports: List[int],
        detect_services: bool
    ) -> List[PortResult]:
        """Scan multiple ports concurrently.
        
        Args:
            target: Target host or IP address.
            ports: List of ports to scan.
            detect_services: Whether to perform service detection.
            
        Returns:
            List of PortResult objects.
        """
        tasks = []
        for port in ports:
            task = self._scan_single_port(target, port, detect_services)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(PortResult(
                    port=ports[i],
                    status=PortStatus.UNKNOWN,
                    error=str(result)
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _scan_single_port(
        self,
        target: str,
        port: int,
        detect_services: bool
    ) -> PortResult:
        """Scan a single port.
        
        Args:
            target: Target host or IP address.
            port: Port number to scan.
            detect_services: Whether to perform service detection.
            
        Returns:
            PortResult for the scanned port.
        """
        async with self._semaphore:
            start_time = time.time()
            
            try:
                # Attempt connection
                status = await self._check_port_status(target, port)
                
                response_time = (time.time() - start_time) * 1000  # Convert to ms
                
                # Perform service detection if port is open
                service = None
                if status == PortStatus.OPEN and detect_services:
                    try:
                        service = await self.service_detector.detect_service(target, port)
                    except Exception:
                        # Service detection failed, but port is still open
                        pass
                
                return PortResult(
                    port=port,
                    status=status,
                    service=service,
                    response_time=response_time
                )
                
            except Exception as e:
                return PortResult(
                    port=port,
                    status=PortStatus.UNKNOWN,
                    error=str(e)
                )
    
    async def _check_port_status(self, target: str, port: int) -> PortStatus:
        """Check if a port is open, closed, or filtered.
        
        Args:
            target: Target host or IP address.
            port: Port number to check.
            
        Returns:
            PortStatus indicating port state.
        """
        for attempt in range(self.config.retry_count + 1):
            try:
                # Create connection
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(target, port),
                    timeout=self.config.timeout
                )
                
                # Connection successful - port is open
                writer.close()
                await writer.wait_closed()
                return PortStatus.OPEN
                
            except asyncio.TimeoutError:
                # Timeout - port might be filtered
                return PortStatus.FILTERED
                
            except ConnectionRefusedError:
                # Connection refused - port is closed
                return PortStatus.CLOSED
                
            except OSError as e:
                if e.errno == 113:  # No route to host
                    return PortStatus.FILTERED
                elif e.errno == 111:  # Connection refused
                    return PortStatus.CLOSED
                else:
                    # Other network error
                    if attempt == self.config.retry_count:
                        return PortStatus.UNKNOWN
                    await asyncio.sleep(0.1)  # Brief delay before retry
        
        return PortStatus.UNKNOWN
    
    def _validate_target(self, target: str) -> str:
        """Validate target host or IP address.
        
        Args:
            target: Target to validate.
            
        Returns:
            Validated target string.
            
        Raises:
            InvalidTargetError: If target is invalid.
        """
        if not target or not isinstance(target, str):
            raise InvalidTargetError("Target must be a non-empty string")
        
        target = target.strip()
        if not target:
            raise InvalidTargetError("Target cannot be empty")
        
        # Basic validation - could be enhanced with more sophisticated checks
        if len(target) > 255:
            raise InvalidTargetError("Target hostname too long")
        
        return target
    
    def _parse_ports(self, ports: Union[int, List[int], str]) -> List[int]:
        """Parse ports input into a list of integers.
        
        Args:
            ports: Port specification (int, list, or range string).
            
        Returns:
            List of port numbers.
            
        Raises:
            InvalidTargetError: If ports specification is invalid.
        """
        if isinstance(ports, int):
            return [ports]
        
        if isinstance(ports, list):
            if not all(isinstance(p, int) and 1 <= p <= 65535 for p in ports):
                raise InvalidTargetError("All ports must be integers between 1 and 65535")
            return ports
        
        if isinstance(ports, str):
            return self._parse_port_range(ports)
        
        raise InvalidTargetError("Ports must be int, list of ints, or range string")
    
    def _parse_port_range(self, port_range: str) -> List[int]:
        """Parse port range string (e.g., "1-1000", "80,443,8080").
        
        Args:
            port_range: Port range string.
            
        Returns:
            List of port numbers.
            
        Raises:
            InvalidTargetError: If port range is invalid.
        """
        ports: Set[int] = set()
        
        for part in port_range.split(','):
            part = part.strip()
            
            if '-' in part:
                # Range format (e.g., "1-1000")
                try:
                    start, end = part.split('-', 1)
                    start_port = int(start.strip())
                    end_port = int(end.strip())
                    
                    if not (1 <= start_port <= 65535 and 1 <= end_port <= 65535):
                        raise InvalidTargetError("Port numbers must be between 1 and 65535")
                    
                    if start_port > end_port:
                        raise InvalidTargetError("Start port cannot be greater than end port")
                    
                    ports.update(range(start_port, end_port + 1))
                    
                except ValueError:
                    raise InvalidTargetError(f"Invalid port range format: {part}")
            else:
                # Single port
                try:
                    port = int(part)
                    if not (1 <= port <= 65535):
                        raise InvalidTargetError("Port numbers must be between 1 and 65535")
                    ports.add(port)
                except ValueError:
                    raise InvalidTargetError(f"Invalid port number: {part}")
        
        return sorted(list(ports))
