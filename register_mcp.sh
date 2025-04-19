#!/bin/bash
# This script registers the PyTorch Documentation Search MCP server with Claude CLI

# Get the absolute path to the run script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN_SCRIPT="${SCRIPT_DIR}/run_mcp.sh"

# Register with Claude CLI using stdio transport
echo "Registering PyTorch Documentation Search MCP server with Claude CLI..."
claude mcp add search_pytorch_docs stdio "${RUN_SCRIPT}"

# Alternative SSE registration
echo "Alternatively, to register with SSE transport, run:"
echo "claude mcp add search_pytorch_docs http://localhost:5000/events --transport sse"

echo "Registration complete. You can now use the tool with Claude."
echo "To test your installation, ask Claude Code about PyTorch:"
echo "claude"
echo "Then type: How do I use PyTorch DataLoader for custom datasets?"