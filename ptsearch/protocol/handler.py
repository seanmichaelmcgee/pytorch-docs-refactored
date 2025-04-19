"""
MCP protocol handler for PyTorch Documentation Search Tool.
Processes MCP messages and dispatches to appropriate handlers.
"""

import json
from typing import Dict, Any, Optional, Callable, List, Union

from ptsearch.utils import logger
from ptsearch.utils.error import ProtocolError, format_error
from ptsearch.protocol.descriptor import get_tool_descriptor

# Define handler type for protocol methods
HandlerType = Callable[[Dict[str, Any]], Dict[str, Any]]

class MCPProtocolHandler:
    """Handler for MCP protocol messages."""
    
    def __init__(self, search_handler: HandlerType):
        """Initialize with search handler function."""
        self.search_handler = search_handler
        self.tool_descriptor = get_tool_descriptor()
        self.handlers: Dict[str, HandlerType] = {
            "initialize": self._handle_initialize,
            "list_tools": self._handle_list_tools,
            "call_tool": self._handle_call_tool
        }
    
    def process_message(self, message: str) -> str:
        """Process an MCP message and return the response."""
        try:
            # Parse the message
            data = json.loads(message)
            
            # Get the method and message ID
            method = data.get("method", "")
            message_id = data.get("id")
            
            # Log the received message
            logger.info(f"Received MCP message", method=method, id=message_id)
            
            # Handle the message
            if method in self.handlers:
                result = self.handlers[method](data)
                return self._format_response(message_id, result)
            else:
                error = ProtocolError(f"Unknown method: {method}", -32601)
                return self._format_error(message_id, error)
                
        except json.JSONDecodeError:
            logger.error("Invalid JSON message")
            error = ProtocolError("Invalid JSON", -32700)
            return self._format_error(None, error)
        except Exception as e:
            logger.exception(f"Error processing message: {e}")
            return self._format_error(data.get("id") if 'data' in locals() else None, e)
    
    def _handle_initialize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialize request."""
        return {"capabilities": ["tools"]}
    
    def _handle_list_tools(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle list_tools request."""
        return {"tools": [self.tool_descriptor]}
    
    def _handle_call_tool(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle call_tool request."""
        params = data.get("params", {})
        tool_name = params.get("tool")
        args = params.get("args", {})
        
        if tool_name != self.tool_descriptor["name"]:
            raise ProtocolError(f"Unknown tool: {tool_name}", -32602)
        
        # Execute search through handler
        result = self.search_handler(args)
        return {"result": result}
    
    def _format_response(self, id: Optional[str], result: Dict[str, Any]) -> str:
        """Format a successful response."""
        response = {
            "jsonrpc": "2.0",
            "id": id,
            "result": result
        }
        return json.dumps(response)
    
    def _format_error(self, id: Optional[str], error: Union[ProtocolError, Exception]) -> str:
        """Format an error response."""
        error_dict = format_error(error)
        
        response = {
            "jsonrpc": "2.0",
            "id": id,
            "error": {
                "code": error_dict.get("code", -32000),
                "message": error_dict.get("error", "Unknown error")
            }
        }
        
        if "details" in error_dict:
            response["error"]["data"] = error_dict["details"]
            
        return json.dumps(response)