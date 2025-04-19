#!/bin/bash
# Script to run PyTorch Documentation Search MCP server with UVX

# Set current directory to script location
cd "$(dirname "$0")"

# Export OpenAI API key if not already set
if [ -z "$OPENAI_API_KEY" ]; then
  echo "Warning: OPENAI_API_KEY environment variable not set."
  echo "The server will fail to start without this variable."
  echo "Please set the API key with: export OPENAI_API_KEY=sk-..."
  exit 1
fi

# Run the server with UVX
uvx mcp-server-pytorch --transport sse --host 127.0.0.1 --port 5000 --data-dir ./data