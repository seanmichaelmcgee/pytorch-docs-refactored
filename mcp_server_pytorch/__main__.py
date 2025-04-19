#!/usr/bin/env python3
"""
PyTorch Documentation Search Tool - MCP Server
Provides semantic search over PyTorch documentation with code-aware results.
"""

import sys
import argparse
import os
import signal
import time

from ptsearch.utils import logger
from ptsearch.utils.error import ConfigError
from ptsearch.config import settings
from ptsearch.server import run_server

# Early API key validation
if not os.environ.get("OPENAI_API_KEY"):
    print("Error: OPENAI_API_KEY not found in environment variables.", file=sys.stderr)
    print("Please set this key in your environment before running.", file=sys.stderr)
    sys.exit(1)

def main(argv=None):
    """Main entry point for MCP server."""
    # Configure logging
    log_file = os.environ.get("MCP_LOG_FILE", "mcp_server.log")
    import logging
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logging.getLogger().addHandler(file_handler)
    
    parser = argparse.ArgumentParser(description="PyTorch Documentation Search MCP Server")
    parser.add_argument("--transport", choices=["stdio", "sse"], default="stdio",
                      help="Transport mechanism to use (default: stdio)")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to for SSE transport")
    parser.add_argument("--port", type=int, default=5000, help="Port to bind to for SSE transport")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--data-dir", help="Path to the data directory containing data files")
    
    args = parser.parse_args(argv)
    
    # Set data directory if provided
    if args.data_dir:
        # Update paths to include the provided data directory
        data_dir = os.path.abspath(args.data_dir)
        logger.info(f"Using custom data directory: {data_dir}")
        settings.default_chunks_path = os.path.join(data_dir, "chunks.json")
        settings.default_embeddings_path = os.path.join(data_dir, "chunks_with_embeddings.json")
        settings.db_dir = os.path.join(data_dir, "chroma_db")
        settings.cache_dir = os.path.join(data_dir, "embedding_cache")
    
    try:
        # Run the server with appropriate transport
        run_server(args.transport, args.host, args.port, args.debug)
    except Exception as e:
        logger.exception(f"Fatal error", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()