"""
Base transport implementation for PyTorch Documentation Search Tool.
Defines the interface for transport mechanisms.
"""

import abc
from typing import Dict, Any, Callable

from ptsearch.utils import logger
from ptsearch.protocol import MCPProtocolHandler


class BaseTransport(abc.ABC):
    """Base class for all transport mechanisms."""
    
    def __init__(self, protocol_handler: MCPProtocolHandler):
        """Initialize with protocol handler."""
        self.protocol_handler = protocol_handler
        logger.info(f"Initialized {self.__class__.__name__}")
    
    @abc.abstractmethod
    def start(self):
        """Start the transport."""
        pass
    
    @abc.abstractmethod
    def stop(self):
        """Stop the transport."""
        pass
    
    @property
    @abc.abstractmethod
    def is_running(self) -> bool:
        """Check if the transport is running."""
        pass