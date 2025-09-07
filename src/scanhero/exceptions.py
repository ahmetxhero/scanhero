"""Custom exceptions for ScanHero package."""


class ScanHeroError(Exception):
    """Base exception class for all ScanHero errors."""
    
    def __init__(self, message: str, error_code: str = "SCAN_ERROR") -> None:
        """Initialize ScanHero error.
        
        Args:
            message: Error message describing what went wrong.
            error_code: Unique error code for programmatic handling.
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class ScanTimeoutError(ScanHeroError):
    """Raised when a scan operation times out."""
    
    def __init__(self, message: str = "Scan operation timed out") -> None:
        """Initialize scan timeout error.
        
        Args:
            message: Error message describing the timeout.
        """
        super().__init__(message, "SCAN_TIMEOUT")


class InvalidTargetError(ScanHeroError):
    """Raised when an invalid target is provided for scanning."""
    
    def __init__(self, message: str = "Invalid target provided") -> None:
        """Initialize invalid target error.
        
        Args:
            message: Error message describing the invalid target.
        """
        super().__init__(message, "INVALID_TARGET")


class ServiceDetectionError(ScanHeroError):
    """Raised when service detection fails."""
    
    def __init__(self, message: str = "Service detection failed") -> None:
        """Initialize service detection error.
        
        Args:
            message: Error message describing the detection failure.
        """
        super().__init__(message, "SERVICE_DETECTION_ERROR")


class ConfigurationError(ScanHeroError):
    """Raised when there's a configuration error."""
    
    def __init__(self, message: str = "Configuration error") -> None:
        """Initialize configuration error.
        
        Args:
            message: Error message describing the configuration issue.
        """
        super().__init__(message, "CONFIGURATION_ERROR")
