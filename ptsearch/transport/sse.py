"""
Server-Sent Events (SSE) transport implementation for PyTorch Documentation Search Tool.
Provides an HTTP server for MCP using Flask and SSE.
"""

import json
import time
from typing import Dict, Any, Optional, Iterator

from flask import Flask, Response, request, jsonify, stream_with_context, g
from flask_cors import CORS

from ptsearch.utils import logger
from ptsearch.utils.error import TransportError, format_error
from ptsearch.protocol import MCPProtocolHandler, get_tool_descriptor
from ptsearch.transport.base import BaseTransport


class SSETransport(BaseTransport):
    """SSE transport implementation for MCP."""
    
    def __init__(self, protocol_handler: MCPProtocolHandler, host: str = "0.0.0.0", port: int = 5000):
        """Initialize SSE transport with host and port."""
        super().__init__(protocol_handler)
        self.host = host
        self.port = port
        self.flask_app = self._create_flask_app()
        self._running = False
    
    def _create_flask_app(self) -> Flask:
        """Create and configure Flask app."""
        app = Flask("ptsearch_sse")
        CORS(app)  # Enable CORS for all routes
        
        # Request ID tracking
        @app.before_request
        def tag_request():
            g.request_id = logger.request_context()
            logger.info(f"{request.method} {request.path}")
        
        # SSE events endpoint for tool registration
        @app.route("/events")
        def events():
            def stream() -> Iterator[str]:
                tool_descriptor = get_tool_descriptor()
                
                # Add endpoint info for SSE transport
                if "endpoint" not in tool_descriptor:
                    tool_descriptor["endpoint"] = {
                        "path": "/tools/call",
                        "method": "POST"
                    }
                
                payload = json.dumps([tool_descriptor])
                for tag in ("tool_list", "tools"):
                    logger.debug(f"Sending event: {tag}")
                    yield f"event: {tag}\ndata: {payload}\n\n"
                
                # Keep-alive loop
                n = 0
                while True:
                    n += 1
                    time.sleep(15)
                    yield f": ka-{n}\n\n"
            
            return Response(
                stream_with_context(stream()),
                mimetype="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "X-Accel-Buffering": "no",
                    "Connection": "keep-alive",
                },
            )
        
        # Call handling endpoint
        @app.route("/tools/call", methods=["POST"])
        def tools_call():
            try:
                body = request.get_json(force=True)
                # Convert to MCP protocol message format for the handler
                message = {
                    "jsonrpc": "2.0",
                    "id": "http-call",
                    "method": "call_tool",
                    "params": {
                        "tool": body.get("tool"),
                        "args": body.get("args", {})
                    }
                }
                
                # Use the protocol handler to process the message
                response_str = self.protocol_handler.process_message(json.dumps(message))
                response = json.loads(response_str)
                
                if "error" in response:
                    return jsonify({"error": response["error"]["message"]}), 400
                
                return jsonify(response["result"]["result"])
            except Exception as e:
                logger.exception(f"Error handling call: {e}")
                error_dict = format_error(e)
                return jsonify({"error": error_dict["error"]}), error_dict.get("code", 500)
        
        # List tools endpoint
        @app.route("/tools/list", methods=["GET"])
        def tools_list():
            tool_descriptor = get_tool_descriptor()
            # Add endpoint info for SSE transport
            if "endpoint" not in tool_descriptor:
                tool_descriptor["endpoint"] = {
                    "path": "/tools/call",
                    "method": "POST"
                }
            return jsonify([tool_descriptor])
        
        # Health check endpoint
        @app.route("/health", methods=["GET"])
        def health():
            return "ok", 200
        
        # Direct search endpoint
        @app.route("/search", methods=["POST"])
        def search():
            try:
                data = request.get_json(force=True)
                
                # Convert to MCP protocol message format for the handler
                message = {
                    "jsonrpc": "2.0",
                    "id": "http-search",
                    "method": "call_tool",
                    "params": {
                        "tool": get_tool_descriptor()["name"],
                        "args": data
                    }
                }
                
                # Use the protocol handler to process the message
                response_str = self.protocol_handler.process_message(json.dumps(message))
                response = json.loads(response_str)
                
                if "error" in response:
                    return jsonify({"error": response["error"]["message"]}), 400
                
                return jsonify(response["result"]["result"])
            except Exception as e:
                logger.exception(f"Error handling search: {e}")
                error_dict = format_error(e)
                return jsonify({"error": error_dict["error"]}), error_dict.get("code", 500)
        
        return app
    
    def start(self):
        """Start the Flask server."""
        logger.info(f"Starting SSE transport on {self.host}:{self.port}")
        self._running = True
        
        tool_name = get_tool_descriptor()["name"]
        logger.info(f"Tool registration command:")
        logger.info(f"claude mcp add --transport sse {tool_name} http://{self.host}:{self.port}/events")
        
        try:
            self.flask_app.run(host=self.host, port=self.port, threaded=True)
        except Exception as e:
            logger.exception(f"Error in SSE transport: {e}")
            self._running = False
            raise TransportError(f"SSE transport error: {e}")
        finally:
            self._running = False
            logger.info("SSE transport stopped")
    
    def stop(self):
        """Stop the transport."""
        logger.info("Stopping SSE transport")
        self._running = False
        # Flask doesn't have a clean shutdown mechanism from inside
        # This would normally be handled via signals from outside
    
    @property
    def is_running(self) -> bool:
        """Check if the transport is running."""
        return self._running