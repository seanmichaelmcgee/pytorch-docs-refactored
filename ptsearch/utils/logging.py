"""
Logging utilities for PyTorch Documentation Search Tool.
Provides consistent structured logging with context tracking.
"""

import json
import logging
import sys
import time
import uuid
from typing import Dict, Any, Optional

class StructuredLogger:
    """Logger that provides structured, consistent logging with context."""
    
    def __init__(self, name: str, level: int = logging.INFO):
        """Initialize logger with name and level."""
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Add console handler if none exists
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stderr)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        # Request context
        self.context: Dict[str, Any] = {}
    
    def set_context(self, **kwargs):
        """Set context values to include in all log messages."""
        self.context.update(kwargs)
    
    def _format_message(self, message: str, extra: Optional[Dict[str, Any]] = None) -> str:
        """Format message with context and extra data."""
        log_data = {**self.context}
        
        if extra:
            log_data.update(extra)
        
        if log_data:
            return f"{message} {json.dumps(log_data)}"
        return message
    
    def debug(self, message: str, **kwargs):
        """Log debug message with context."""
        self.logger.debug(self._format_message(message, kwargs))
    
    def info(self, message: str, **kwargs):
        """Log info message with context."""
        self.logger.info(self._format_message(message, kwargs))
    
    def warning(self, message: str, **kwargs):
        """Log warning message with context."""
        self.logger.warning(self._format_message(message, kwargs))
    
    def error(self, message: str, **kwargs):
        """Log error message with context."""
        self.logger.error(self._format_message(message, kwargs))
    
    def critical(self, message: str, **kwargs):
        """Log critical message with context."""
        self.logger.critical(self._format_message(message, kwargs))
    
    def exception(self, message: str, **kwargs):
        """Log exception message with context and traceback."""
        self.logger.exception(self._format_message(message, kwargs))
    
    def request_context(self, request_id: Optional[str] = None):
        """Create a new request context with unique ID."""
        req_id = request_id or str(uuid.uuid4())
        self.set_context(request_id=req_id, timestamp=time.time())
        return req_id

# Create main application logger
logger = StructuredLogger("ptsearch")