#!/bin/bash
# Script to run PyTorch Documentation Search MCP server with stdio transport

# Set current directory to script location
cd "$(dirname "$0")"

# Enable debug mode
set -x

# Export log file path for detailed logging
export MCP_LOG_FILE="./mcp_server.log"

# Check for OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
  echo "Warning: OPENAI_API_KEY environment variable not set."
  echo "The server will fail to start without this variable."
  echo "Please set the API key with: export OPENAI_API_KEY=sk-..."
  exit 1
fi

# Source conda to ensure it's available
if [ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]; then
    source "$HOME/miniconda3/etc/profile.d/conda.sh"
elif [ -f "$HOME/anaconda3/etc/profile.d/conda.sh" ]; then
    source "$HOME/anaconda3/etc/profile.d/conda.sh"
else
    echo "Could not find conda.sh. Please ensure Miniconda or Anaconda is installed."
    exit 1
fi

# Activate the conda environment
conda activate pytorch_docs_search

# Run the server with stdio transport and specify data directory
exec python -m ptsearch.server --transport stdio --data-dir ./data