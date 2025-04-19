"""
Error handling utilities for PyTorch Documentation Search Tool.
Defines custom exceptions and error formatting.
"""

from typing import Dict, Any, Optional, List, Union

class PTSearchError(Exception):
    """Base exception for all PyTorch Documentation Search Tool errors."""
    
    def __init__(self, message: str, code: int = 500, details: Optional[Dict[str, Any]] = None):
        """Initialize error with message, code and details."""
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for JSON serialization."""
        result = {
            "error": self.message,
            "code": self.code
        }
        if self.details:
            result["details"] = self.details
        return result


class ConfigError(PTSearchError):
    """Error raised for configuration issues."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Initialize config error."""
        super().__init__(message, 500, details)


class APIError(PTSearchError):
    """Error raised for API-related issues (e.g., OpenAI API)."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Initialize API error."""
        super().__init__(message, 502, details)


class DatabaseError(PTSearchError):
    """Error raised for database-related issues."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Initialize database error."""
        super().__init__(message, 500, details)


class SearchError(PTSearchError):
    """Error raised for search-related issues."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Initialize search error."""
        super().__init__(message, 400, details)


class TransportError(PTSearchError):
    """Error raised for transport-related issues."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Initialize transport error."""
        super().__init__(message, 500, details)


class ProtocolError(PTSearchError):
    """Error raised for MCP protocol-related issues."""
    
    def __init__(self, message: str, code: int = -32600, details: Optional[Dict[str, Any]] = None):
        """Initialize protocol error with JSON-RPC error code."""
        super().__init__(message, code, details)


def format_error(error: Union[PTSearchError, Exception]) -> Dict[str, Any]:
    """Format any error for JSON response."""
    if isinstance(error, PTSearchError):
        return error.to_dict()
    
    return {
        "error": str(error),
        "code": 500
    }