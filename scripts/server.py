#!/usr/bin/env python3
"""
Server script for PyTorch Documentation Search Tool.
Provides an MCP-compatible server for Claude Code CLI integration.
"""

import os
import sys
import json
import logging
import time
from flask import Flask, Response, request, jsonify, stream_with_context, g, abort

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ptsearch.database import DatabaseManager
from ptsearch.embedding import EmbeddingGenerator
from ptsearch.search import SearchEngine
from ptsearch.config import MAX_RESULTS, logger

# Tool descriptor for MCP
TOOL_NAME = "search_pytorch_docs"
TOOL_DESCRIPTOR = {
    "name": TOOL_NAME,
    "schema_version": "0.4",
    "type": "function",
    "description": (
        "Search PyTorch documentation or examples. Call when the user asks "
        "about a PyTorch API, error message, best-practice or needs a code snippet."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "num_results": {"type": "integer", "default": 5},
            "filter": {"type": "string", "enum": ["code", "text", None]},
        },
        "required": ["query"],
    },
    "endpoint": {"path": "/tools/call", "method": "POST"},
}

# Flask app
app = Flask(__name__)
seq = 0

# Initialize search components
db_manager = DatabaseManager()
embedding_generator = EmbeddingGenerator()
search_engine = SearchEngine(db_manager, embedding_generator)

@app.before_request
def tag_request():
    global seq
    g.cid = f"c{int(time.time())}-{seq}"
    seq += 1
    logger.info("[%s] %s %s", g.cid, request.method, request.path)

@app.after_request
def log_response(resp):
    logger.info("[%s] → %s", g.cid, resp.status)
    return resp

# SSE events endpoint for tool registration
@app.route("/events")
def events():
    cid = g.cid
    
    def stream():
        payload = json.dumps([TOOL_DESCRIPTOR])
        for tag in ("tool_list", "tools"):
            logger.debug("[%s] send %s", cid, tag)
            yield f"event: {tag}\ndata: {payload}\n\n"
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
    if body.get("tool") != TOOL_NAME:
        abort(400, description="Unknown tool")
    
    args = body.get("args", {})
    
    # Echo for testing
    if args.get("echo") == "ping":
        return {"ok": True}
    
    # Process search
    query = args.get("query", "")
    n = int(args.get("num_results", 5))
    filter_type = args.get("filter")
    
    return search_engine.search(query, n, filter_type)

# Register endpoints for various call paths
for path in ("/tools/call", "/call", "/invoke", "/run"):
    app.add_url_rule(
        path,
        path,
        lambda path=path: jsonify(handle_call(request.get_json(force=True))),
        methods=["POST"],
    )

# Catch-all for unknown routes
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def catch_all(path):
    logger.warning("[%s] catch-all: %s", g.cid, path)
    return jsonify({"error": "no such endpoint", "path": path}), 404

# List tools
@app.route("/tools/list")
def list_tools():
    return jsonify([TOOL_DESCRIPTOR])

# Health check
@app.route("/health")
def health():
    return "ok", 200

# Direct search endpoint
@app.route("/search", methods=["POST"])
def search():
    data = request.get_json(force=True)
    query = data.get("query", "")
    n = int(data.get("num_results", 5))
    filter_type = data.get("filter")
    
    return jsonify(search_engine.search(query, n, filter_type))

if __name__ == "__main__":
    print("Starting PyTorch Documentation Search Server")
    print("Run: claude mcp add --transport sse pytorch_search http://localhost:5000/events")
    app.run(host="0.0.0.0", port=5000, debug=False)