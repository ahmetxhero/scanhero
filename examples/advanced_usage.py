#!/usr/bin/env python3
"""Advanced usage examples for ScanHero."""

import asyncio
import json
import time
from typing import List
from scanhero import PortScanner, ScanConfig, ScanResult
from scanhero.models import PortResult, ServiceInfo, ServiceType


class ScanAnalyzer:
    """Advanced scan result analyzer."""
    
    def __init__(self, result: ScanResult):
        """Initialize analyzer with scan result.
        
        Args:
            result: ScanResult to analyze.
        """
        self.result = result
    
    def get_vulnerable_services(self) -> List[PortResult]:
        """Identify potentially vulnerable services.
        
        Returns:
            List of port results with potentially vulnerable services.
        """
        vulnerable = []
        
        for port_result in self.result.open_ports:
            if not port_result.service:
                continue
            
            service = port_result.service
            
            # Check for known vulnerable services/versions
            if self._is_vulnerable_service(service):
                vulnerable.append(port_result)
        
        return vulnerable
    
    def _is_vulnerable_service(self, service: ServiceInfo) -> bool:
        """Check if service is potentially vulnerable.
        
        Args:
            service: ServiceInfo to check.
            
        Returns:
            True if service is potentially vulnerable.
        """
        # Simple vulnerability checks (in real implementation, use CVE database)
        vulnerable_patterns = [
            ("Apache", "2.2"),  # Old Apache versions
            ("nginx", "1.0"),   # Old nginx versions
            ("OpenSSH", "6.0"), # Old SSH versions
            ("vsftpd", "2.3"),  # Old FTP versions
        ]
        
        if not service.version:
            return False
        
        for name, version in vulnerable_patterns:
            if name.lower() in service.name.lower() and version in service.version:
                return True
        
        return False
    
    def get_network_services(self) -> List[PortResult]:
        """Get network infrastructure services.
        
        Returns:
            List of port results for network services.
        """
        network_services = []
        
        for port_result in self.result.open_ports:
            if not port_result.service:
                continue
            
            service_type = port_result.service.service_type
            
            if service_type in [ServiceType.DNS, ServiceType.SNMP, ServiceType.LDAP]:
                network_services.append(port_result)
        
        return network_services
    
    def get_web_services(self) -> List[PortResult]:
        """Get web services.
        
        Returns:
            List of port results for web services.
        """
        web_services = []
        
        for port_result in self.result.open_ports:
            if not port_result.service:
                continue
            
            service_type = port_result.service.service_type
            
            if service_type in [ServiceType.HTTP, ServiceType.HTTPS]:
                web_services.append(port_result)
        
        return web_services
    
    def generate_report(self) -> dict:
        """Generate comprehensive scan report.
        
        Returns:
            Dictionary containing scan analysis.
        """
        report = {
            "scan_info": {
                "target": self.result.target,
                "scan_duration": self.result.scan_duration,
                "timestamp": self.result.timestamp,
                "total_ports": self.result.total_ports
            },
            "summary": {
                "open_ports": self.result.open_count,
                "closed_ports": self.result.closed_count,
                "filtered_ports": self.result.filtered_count,
                "services_detected": len(self.result.get_services())
            },
            "analysis": {
                "vulnerable_services": len(self.get_vulnerable_services()),
                "network_services": len(self.get_network_services()),
                "web_services": len(self.get_web_services())
            },
            "recommendations": self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate security recommendations.
        
        Returns:
            List of security recommendations.
        """
        recommendations = []
        
        # Check for common security issues
        if self.result.open_count > 10:
            recommendations.append("High number of open ports detected. Consider closing unnecessary services.")
        
        vulnerable_services = self.get_vulnerable_services()
        if vulnerable_services:
            recommendations.append(f"Found {len(vulnerable_services)} potentially vulnerable services. Update immediately.")
        
        web_services = self.get_web_services()
        if web_services:
            recommendations.append("Web services detected. Ensure proper security configurations.")
        
        if not any(port_result.service and port_result.service.service_type == ServiceType.HTTPS 
                  for port_result in self.result.open_ports):
            recommendations.append("No HTTPS services detected. Consider implementing SSL/TLS.")
        
        return recommendations


class BatchScanner:
    """Batch scanner for multiple targets."""
    
    def __init__(self, config: ScanConfig):
        """Initialize batch scanner.
        
        Args:
            config: Scanner configuration.
        """
        self.config = config
        self.scanner = PortScanner(config)
    
    async def scan_targets(self, targets: List[str], ports: List[int]) -> List[ScanResult]:
        """Scan multiple targets concurrently.
        
        Args:
            targets: List of target hosts/IPs.
            ports: List of ports to scan.
            
        Returns:
            List of ScanResult objects.
        """
        tasks = []
        for target in targets:
            task = self.scanner.scan(target, ports)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Error scanning {targets[i]}: {result}")
                continue
            processed_results.append(result)
        
        return processed_results
    
    def compare_results(self, results: List[ScanResult]) -> dict:
        """Compare scan results across targets.
        
        Args:
            results: List of ScanResult objects.
            
        Returns:
            Comparison analysis.
        """
        comparison = {
            "targets": [r.target for r in results],
            "common_open_ports": self._find_common_ports(results, "open"),
            "unique_ports": self._find_unique_ports(results),
            "service_analysis": self._analyze_services(results)
        }
        
        return comparison
    
    def _find_common_ports(self, results: List[ScanResult], port_type: str) -> List[int]:
        """Find common ports across targets.
        
        Args:
            results: List of ScanResult objects.
            port_type: Type of ports to analyze ('open', 'closed', 'filtered').
            
        Returns:
            List of common port numbers.
        """
        port_sets = []
        for result in results:
            if port_type == "open":
                ports = [p.port for p in result.open_ports]
            elif port_type == "closed":
                ports = [p.port for p in result.closed_ports]
            else:
                ports = [p.port for p in result.filtered_ports]
            port_sets.append(set(ports))
        
        if not port_sets:
            return []
        
        common_ports = port_sets[0]
        for port_set in port_sets[1:]:
            common_ports = common_ports.intersection(port_set)
        
        return sorted(list(common_ports))
    
    def _find_unique_ports(self, results: List[ScanResult]) -> dict:
        """Find unique ports per target.
        
        Args:
            results: List of ScanResult objects.
            
        Returns:
            Dictionary mapping targets to their unique ports.
        """
        unique_ports = {}
        
        for result in results:
            target_ports = set(p.port for p in result.open_ports)
            other_ports = set()
            
            for other_result in results:
                if other_result.target != result.target:
                    other_ports.update(p.port for p in other_result.open_ports)
            
            unique_ports[result.target] = sorted(list(target_ports - other_ports))
        
        return unique_ports
    
    def _analyze_services(self, results: List[ScanResult]) -> dict:
        """Analyze services across targets.
        
        Args:
            results: List of ScanResult objects.
            
        Returns:
            Service analysis.
        """
        service_counts = {}
        all_services = set()
        
        for result in results:
            services = result.get_services()
            for service in services:
                service_name = service.name
                all_services.add(service_name)
                service_counts[service_name] = service_counts.get(service_name, 0) + 1
        
        return {
            "total_unique_services": len(all_services),
            "service_frequency": service_counts,
            "most_common_services": sorted(service_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        }


async def advanced_scan_analysis():
    """Demonstrate advanced scan analysis."""
    print("=== Advanced Scan Analysis ===")
    
    scanner = PortScanner()
    result = await scanner.scan("127.0.0.1", "1-1000")
    
    analyzer = ScanAnalyzer(result)
    report = analyzer.generate_report()
    
    print("Scan Report:")
    print(json.dumps(report, indent=2))
    
    # Show vulnerable services
    vulnerable = analyzer.get_vulnerable_services()
    if vulnerable:
        print(f"\nPotentially Vulnerable Services ({len(vulnerable)}):")
        for port_result in vulnerable:
            service = port_result.service
            print(f"  Port {port_result.port}: {service.name} {service.version}")


async def batch_scanning():
    """Demonstrate batch scanning."""
    print("\n=== Batch Scanning ===")
    
    config = ScanConfig(max_concurrent=50)
    batch_scanner = BatchScanner(config)
    
    # Scan multiple targets
    targets = ["127.0.0.1", "localhost"]
    ports = [80, 443, 22, 21, 25, 53]
    
    print(f"Scanning {len(targets)} targets on {len(ports)} ports...")
    start_time = time.time()
    
    results = await batch_scanner.scan_targets(targets, ports)
    
    scan_time = time.time() - start_time
    print(f"Batch scan completed in {scan_time:.2f}s")
    
    # Compare results
    comparison = batch_scanner.compare_results(results)
    print("\nComparison Results:")
    print(json.dumps(comparison, indent=2))


async def performance_testing():
    """Demonstrate performance testing capabilities."""
    print("\n=== Performance Testing ===")
    
    # Test different configurations
    configs = [
        ScanConfig(max_concurrent=10, timeout=1.0),
        ScanConfig(max_concurrent=50, timeout=2.0),
        ScanConfig(max_concurrent=100, timeout=3.0),
    ]
    
    ports = list(range(1, 101))  # Scan ports 1-100
    
    for i, config in enumerate(configs):
        print(f"\nConfiguration {i+1}: max_concurrent={config.max_concurrent}, timeout={config.timeout}")
        
        scanner = PortScanner(config)
        start_time = time.time()
        
        result = await scanner.scan("127.0.0.1", ports)
        
        scan_time = time.time() - start_time
        print(f"  Scan time: {scan_time:.2f}s")
        print(f"  Open ports: {result.open_count}")
        print(f"  Closed ports: {result.closed_count}")
        print(f"  Filtered ports: {result.filtered_count}")


async def main():
    """Run advanced examples."""
    print("ScanHero Advanced Usage Examples")
    print("=" * 50)
    
    await advanced_scan_analysis()
    await batch_scanning()
    await performance_testing()
    
    print("\nAdvanced examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
