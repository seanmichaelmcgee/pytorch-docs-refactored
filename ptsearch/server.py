#!/usr/bin/env python3
"""
Unified MCP server implementation for PyTorch Documentation Search Tool.
Provides both STDIO and SSE transport support for Claude Code CLI integration.
"""

import os
import sys
import json
import logging
import time
import asyncio
from typing import Dict, Any, Optional, List, Union

from flask import Flask, Response, request, jsonify, stream_with_context, g, abort
from flask_cors import CORS

from ptsearch.utils import logger
from ptsearch.config import settings
from ptsearch.core import DatabaseManager, EmbeddingGenerator, SearchEngine
from ptsearch.protocol import MCPProtocolHandler, get_tool_descriptor
from ptsearch.transport import STDIOTransport, SSETransport

# Early API key validation
if not os.environ.get("OPENAI_API_KEY"):
    logger.error("OPENAI_API_KEY not found. Please set this key before running the server.")
    print("Error: OPENAI_API_KEY not found in environment variables.")
    print("Please set this key in your .env file or environment before running the server.")


def format_search_results(results: Dict[str, Any], query: str) -> str:
    """Format search results as text for CLI output."""
    result_text = f"Search results for: {query}\n\n"
    
    for i, res in enumerate(results.get("results", [])):
        result_text += f"--- Result {i+1} ({res.get('chunk_type', 'unknown')}) ---\n"
        result_text += f"Title: {res.get('title', 'Unknown')}\n"
        result_text += f"Source: {res.get('source', 'Unknown')}\n"
        result_text += f"Score: {res.get('score', 0):.4f}\n"
        result_text += f"Snippet: {res.get('snippet', '')}\n\n"
        
    return result_text


def search_handler(args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle search requests from the MCP protocol."""
    # Initialize search components
    db_manager = DatabaseManager()
    embedding_generator = EmbeddingGenerator()
    search_engine = SearchEngine(db_manager, embedding_generator)
    
    # Extract search parameters
    query = args.get("query", "")
    n = int(args.get("num_results", settings.max_results))
    filter_type = args.get("filter", "")
    
    # Handle empty string filter as None
    if filter_type == "":
        filter_type = None
    
    # Echo for testing
    if query == "echo:ping":
        return {"ok": True}
    
    # Execute search
    return search_engine.search(query, n, filter_type)


def create_flask_app() -> Flask:
    """Create and configure Flask app for SSE transport."""
    app = Flask("ptsearch_sse")
    CORS(app)  # Enable CORS for all routes
    seq = 0
    
    @app.before_request
    def tag_request():
        nonlocal seq
        g.cid = f"c{int(time.time())}-{seq}"
        seq += 1
        logger.info(f"[{g.cid}] {request.method} {request.path}")

    @app.after_request
    def log_response(resp):
        logger.info(f"[{g.cid}] → {resp.status}")
        return resp

    # SSE events endpoint for tool registration
    @app.route("/events")
    def events():
        cid = g.cid
        
        def stream():
            tool_descriptor = get_tool_descriptor()
            # Add endpoint info for SSE transport
            tool_descriptor["endpoint"] = {
                "path": "/tools/call",
                "method": "POST"
            }
            
            payload = json.dumps([tool_descriptor])
            for tag in ("tool_list", "tools"):
                logger.debug(f"[{cid}] send {tag}")
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

    # Call handling
    def handle_call(body):
        if body.get("tool") != settings.tool_name:
            abort(400, description=f"Unknown tool: {body.get('tool')}. Expected: {settings.tool_name}")
        
        args = body.get("args", {})
        return search_handler(args)

    # Register endpoints for various call paths
    for path in ("/tools/call", "/call", "/invoke", "/run"):
        app.add_url_rule(
            path,
            path,
            lambda path=path: jsonify(handle_call(request.get_json(force=True))),
            methods=["POST"],
        )

    # List tools
    @app.route("/tools/list")
    def list_tools():
        tool_descriptor = get_tool_descriptor()
        # Add endpoint info for SSE transport
        tool_descriptor["endpoint"] = {
            "path": "/tools/call",
            "method": "POST"
        }
        return jsonify([tool_descriptor])

    # Health check
    @app.route("/health")
    def health():
        return "ok", 200

    # Direct search endpoint
    @app.route("/search", methods=["POST"])
    def search():
        try:
            data = request.get_json(force=True)
            results = search_handler(data)
            return jsonify(results)
        except Exception as e:
            logger.exception(f"Error handling search: {e}")
            return jsonify({"error": str(e)}), 500

    return app


def run_stdio_server():
    """Run the MCP server using STDIO transport."""
    logger.info("Starting PyTorch Documentation Search MCP Server with STDIO transport")
    
    # Initialize protocol handler with search handler
    protocol_handler = MCPProtocolHandler(search_handler)
    
    # Initialize and start STDIO transport
    transport = STDIOTransport(protocol_handler)
    transport.start()


def run_sse_server(host: str = "0.0.0.0", port: int = 5000, debug: bool = False):
    """Run the MCP server using SSE transport with Flask."""
    logger.info(f"Starting PyTorch Documentation Search MCP Server with SSE transport on {host}:{port}")
    print(f"Run: claude mcp add --transport sse {settings.tool_name} http://{host}:{port}/events")
    
    app = create_flask_app()
    app.run(host=host, port=port, debug=debug, threaded=True)


def run_server(transport_type: str = "stdio", host: str = "0.0.0.0", port: int = 5000, debug: bool = False):
    """Run the MCP server with the specified transport."""
    # Validate settings
    errors = settings.validate()
    if errors:
        for key, error in errors.items():
            logger.error(f"Configuration error", field=key, error=error)
        sys.exit(1)
    
    # Log server startup
    logger.info("Starting PyTorch Documentation Search MCP Server",
               transport=transport_type,
               python_version=sys.version,
               current_dir=os.getcwd())
    
    # Start the appropriate transport
    if transport_type.lower() == "stdio":
        run_stdio_server()
    elif transport_type.lower() == "sse":
        run_sse_server(host, port, debug)
    else:
        logger.error(f"Unknown transport type: {transport_type}")
        sys.exit(1)


def main():
    """Command-line entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="PyTorch Documentation Search MCP Server")
    parser.add_argument("--transport", choices=["stdio", "sse"], default="stdio",
                     help="Transport mechanism to use (default: stdio)")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to for SSE transport")
    parser.add_argument("--port", type=int, default=5000, help="Port to bind to for SSE transport")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--data-dir", help="Path to the data directory containing data files")
    
    args = parser.parse_args()
    
    # Set data directory if provided
    if args.data_dir:
        data_dir = os.path.abspath(args.data_dir)
        logger.info(f"Using custom data directory: {data_dir}")
        settings.db_dir = os.path.join(data_dir, "chroma_db")
        settings.cache_dir = os.path.join(data_dir, "embedding_cache")
        settings.default_chunks_path = os.path.join(data_dir, "chunks.json")
    
    # Run the server
    run_server(args.transport, args.host, args.port, args.debug)


if __name__ == "__main__":
    main()