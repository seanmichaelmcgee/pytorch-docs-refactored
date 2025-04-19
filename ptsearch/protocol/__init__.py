"""
Protocol handling for PyTorch Documentation Search Tool.
"""

from ptsearch.protocol.descriptor import get_tool_descriptor
from ptsearch.protocol.handler import MCPProtocolHandler

__all__ = ["get_tool_descriptor", "MCPProtocolHandler"]