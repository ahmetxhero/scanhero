"""Output formatters for ScanHero results."""

import csv
import json
from io import StringIO
from typing import Any, Dict, List, Optional
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.panel import Panel
from rich import box
from .models import ScanResult, PortResult, PortStatus, ServiceType


class BaseFormatter:
    """Base class for output formatters."""
    
    def format(self, result: ScanResult) -> str:
        """Format scan result.
        
        Args:
            result: ScanResult to format.
            
        Returns:
            Formatted string.
        """
        raise NotImplementedError


class ConsoleFormatter(BaseFormatter):
    """Rich console formatter with colored output."""
    
    def __init__(self, show_closed: bool = False, show_filtered: bool = False) -> None:
        """Initialize console formatter.
        
        Args:
            show_closed: Whether to show closed ports.
            show_filtered: Whether to show filtered ports.
        """
        self.console = Console()
        self.show_closed = show_closed
        self.show_filtered = show_filtered
    
    def format(self, result: ScanResult) -> str:
        """Format scan result for console output.
        
        Args:
            result: ScanResult to format.
            
        Returns:
            Formatted string.
        """
        output = StringIO()
        console = Console(file=output, width=120)
        
        # Header
        console.print(Panel.fit(
            f"[bold blue]ScanHero Port Scanner Results[/bold blue]\n"
            f"Target: [bold]{result.target}[/bold]\n"
            f"Scan Duration: [bold]{result.scan_duration:.2f}s[/bold]\n"
            f"Timestamp: [bold]{result.timestamp}[/bold]",
            border_style="blue"
        ))
        
        # Summary
        summary_table = Table(title="Scan Summary", box=box.ROUNDED)
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Count", style="magenta", justify="right")
        
        summary_table.add_row("Total Ports Scanned", str(result.total_ports))
        summary_table.add_row("Open Ports", str(result.open_count), style="green")
        summary_table.add_row("Closed Ports", str(result.closed_count), style="red")
        summary_table.add_row("Filtered Ports", str(result.filtered_count), style="yellow")
        
        console.print(summary_table)
        console.print()
        
        # Open ports table
        if result.open_ports:
            self._create_ports_table(console, result.open_ports, "Open Ports", "green")
        
        # Closed ports table (if requested)
        if self.show_closed and result.closed_ports:
            self._create_ports_table(console, result.closed_ports, "Closed Ports", "red")
        
        # Filtered ports table (if requested)
        if self.show_filtered and result.filtered_ports:
            self._create_ports_table(console, result.filtered_ports, "Filtered Ports", "yellow")
        
        # Services summary
        services = result.get_services()
        if services:
            self._create_services_table(console, services)
        
        # Errors
        if result.errors:
            self._create_errors_section(console, result.errors)
        
        return output.getvalue()
    
    def _create_ports_table(
        self,
        console: Console,
        ports: List[PortResult],
        title: str,
        style: str
    ) -> None:
        """Create a table for port results.
        
        Args:
            console: Rich console instance.
            ports: List of port results.
            title: Table title.
            style: Style for the table.
        """
        table = Table(title=title, box=box.ROUNDED)
        table.add_column("Port", style="cyan", justify="right")
        table.add_column("Status", style=style)
        table.add_column("Service", style="white")
        table.add_column("Version", style="dim")
        table.add_column("Response Time", style="dim", justify="right")
        
        for port_result in sorted(ports, key=lambda x: x.port):
            status_text = Text(port_result.status.value.title(), style=style)
            
            service_name = "Unknown"
            version = ""
            if port_result.service:
                service_name = port_result.service.name
                if port_result.service.version:
                    version = port_result.service.version
            
            response_time = ""
            if port_result.response_time is not None:
                response_time = f"{port_result.response_time:.1f}ms"
            
            table.add_row(
                str(port_result.port),
                status_text,
                service_name,
                version,
                response_time
            )
        
        console.print(table)
        console.print()
    
    def _create_services_table(self, console: Console, services: List[Any]) -> None:
        """Create a table for detected services.
        
        Args:
            console: Rich console instance.
            services: List of service info objects.
        """
        table = Table(title="Detected Services", box=box.ROUNDED)
        table.add_column("Service", style="cyan")
        table.add_column("Version", style="dim")
        table.add_column("Confidence", style="dim", justify="right")
        table.add_column("Banner", style="dim")
        
        for service in services:
            confidence = f"{service.confidence:.1%}"
            banner = service.banner[:50] + "..." if service.banner and len(service.banner) > 50 else service.banner or ""
            
            table.add_row(
                service.name,
                service.version or "Unknown",
                confidence,
                banner
            )
        
        console.print(table)
        console.print()
    
    def _create_errors_section(self, console: Console, errors: List[str]) -> None:
        """Create errors section.
        
        Args:
            console: Rich console instance.
            errors: List of error messages.
        """
        error_text = "\n".join(f"• {error}" for error in errors)
        console.print(Panel(
            error_text,
            title="[red]Errors[/red]",
            border_style="red"
        ))


class JSONFormatter(BaseFormatter):
    """JSON formatter for machine-readable output."""
    
    def format(self, result: ScanResult) -> str:
        """Format scan result as JSON.
        
        Args:
            result: ScanResult to format.
            
        Returns:
            JSON string.
        """
        data = {
            "target": result.target,
            "scan_duration": result.scan_duration,
            "timestamp": result.timestamp,
            "summary": {
                "total_ports": result.total_ports,
                "open_ports": result.open_count,
                "closed_ports": result.closed_count,
                "filtered_ports": result.filtered_count
            },
            "ports": {
                "open": [self._port_to_dict(p) for p in result.open_ports],
                "closed": [self._port_to_dict(p) for p in result.closed_ports],
                "filtered": [self._port_to_dict(p) for p in result.filtered_ports]
            },
            "services": [self._service_to_dict(s) for s in result.get_services()],
            "errors": result.errors
        }
        
        return json.dumps(data, indent=2, default=str)
    
    def _port_to_dict(self, port_result: PortResult) -> Dict[str, Any]:
        """Convert PortResult to dictionary.
        
        Args:
            port_result: PortResult to convert.
            
        Returns:
            Dictionary representation.
        """
        data = {
            "port": port_result.port,
            "status": port_result.status.value,
            "response_time": port_result.response_time,
            "error": port_result.error
        }
        
        if port_result.service:
            data["service"] = self._service_to_dict(port_result.service)
        
        return data
    
    def _service_to_dict(self, service: Any) -> Dict[str, Any]:
        """Convert ServiceInfo to dictionary.
        
        Args:
            service: ServiceInfo to convert.
            
        Returns:
            Dictionary representation.
        """
        return {
            "type": service.service_type.value,
            "name": service.name,
            "version": service.version,
            "banner": service.banner,
            "confidence": service.confidence
        }


class CSVFormatter(BaseFormatter):
    """CSV formatter for spreadsheet compatibility."""
    
    def format(self, result: ScanResult) -> str:
        """Format scan result as CSV.
        
        Args:
            result: ScanResult to format.
            
        Returns:
            CSV string.
        """
        output = StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            "Target", "Port", "Status", "Service", "Version", 
            "Response Time (ms)", "Confidence", "Banner", "Error"
        ])
        
        # All port results
        all_ports = result.open_ports + result.closed_ports + result.filtered_ports
        
        for port_result in sorted(all_ports, key=lambda x: x.port):
            service_name = ""
            version = ""
            confidence = ""
            banner = ""
            
            if port_result.service:
                service_name = port_result.service.name
                version = port_result.service.version or ""
                confidence = f"{port_result.service.confidence:.2f}"
                banner = port_result.service.banner or ""
            
            response_time = ""
            if port_result.response_time is not None:
                response_time = f"{port_result.response_time:.1f}"
            
            writer.writerow([
                result.target,
                port_result.port,
                port_result.status.value,
                service_name,
                version,
                response_time,
                confidence,
                banner,
                port_result.error or ""
            ])
        
        return output.getvalue()


def get_formatter(format_type: str, **kwargs) -> BaseFormatter:
    """Get formatter by type.
    
    Args:
        format_type: Type of formatter ('console', 'json', 'csv').
        **kwargs: Additional arguments for formatter.
        
    Returns:
        Formatter instance.
        
    Raises:
        ValueError: If format type is not supported.
    """
    formatters = {
        "console": ConsoleFormatter,
        "json": JSONFormatter,
        "csv": CSVFormatter
    }
    
    if format_type not in formatters:
        raise ValueError(f"Unsupported format type: {format_type}")
    
    return formatters[format_type](**kwargs)
