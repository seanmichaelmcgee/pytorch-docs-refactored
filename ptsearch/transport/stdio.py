"""
STDIO transport implementation for PyTorch Documentation Search Tool.
Handles MCP protocol over standard input/output.
"""

import sys
import signal
from typing import Dict, Any, Optional

from ptsearch.utils import logger
from ptsearch.utils.error import TransportError
from ptsearch.protocol import MCPProtocolHandler
from ptsearch.transport.base import BaseTransport


class STDIOTransport(BaseTransport):
    """STDIO transport implementation for MCP."""
    
    def __init__(self, protocol_handler: MCPProtocolHandler):
        """Initialize STDIO transport."""
        super().__init__(protocol_handler)
        self._running = False
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown."""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, sig, frame):
        """Handle termination signals."""
        logger.info(f"Received signal {sig}, shutting down")
        self.stop()
    
    def start(self):
        """Start processing messages from stdin."""
        logger.info("Starting STDIO transport")
        self._running = True
        
        try:
            while self._running:
                # Read a line from stdin
                line = sys.stdin.readline()
                if not line:
                    logger.info("End of input, shutting down")
                    break
                
                # Process the line and write response to stdout
                response = self.protocol_handler.process_message(line.strip())
                sys.stdout.write(response + "\n")
                sys.stdout.flush()
                
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt, shutting down")
        except Exception as e:
            logger.exception(f"Error in STDIO transport: {e}")
            self._running = False
            raise TransportError(f"STDIO transport error: {e}")
        finally:
            self._running = False
            logger.info("STDIO transport stopped")
    
    def stop(self):
        """Stop the transport."""
        logger.info("Stopping STDIO transport")
        self._running = False
    
    @property
    def is_running(self) -> bool:
        """Check if the transport is running."""
        return self._running