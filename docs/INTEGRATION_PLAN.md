# PyTorch Documentation Search Tool Integration Plan

This document outlines the MCP integration plan for the PyTorch Documentation Search Tool.

## 1. Overview

The PyTorch Documentation Search Tool is designed to be integrated with Claude Code as a Model Control Protocol (MCP) service. This integration allows Claude Code to search through PyTorch documentation for users directly from the chat interface.

## 2. Unified Architecture

The refactored architecture consists of:

### Core Components

- **Server Module** (`ptsearch/server.py`): Unified implementation for both STDIO and SSE transports
- **Protocol Handling** (`ptsearch/protocol/`): MCP protocol implementation with schema version 1.0
- **Transport Layer** (`ptsearch/transport/`): Clean implementations for STDIO and SSE

### Entry Points

- **Package Entry** (`mcp_server_pytorch/__main__.py`): Command-line interface
- **Scripts**:
  - `run_mcp.sh`: Run with STDIO transport
  - `run_mcp_uvx.sh`: Run with UVX packaging
  - `register_mcp.sh`: Register with Claude CLI

## 3. Integration Methods

### Method 1: Direct STDIO Integration (Recommended for local use)

1. Install the package: `pip install -e .`
2. Register with Claude CLI: `./register_mcp.sh`
3. Use in conversation: "How do I implement a custom dataset in PyTorch?"

### Method 2: HTTP/SSE Integration (For shared servers)

1. Run the server: `python -m ptsearch.server --transport sse --host 0.0.0.0 --port 5000`
2. Register with Claude CLI: `claude mcp add search_pytorch_docs http://localhost:5000/events --transport sse`

### Method 3: UVX Integration (For packaged distribution)

1. Build the UVX package: `uvx build`
2. Run with UVX: `./run_mcp_uvx.sh`
3. Register with Claude CLI as in Method 2

## 4. Requirements

- Python 3.10+
- OpenAI API key for embeddings
- PyTorch documentation data in the `data/` directory

## 5. Testing

Use the following to verify the integration:

```bash
# Test STDIO transport
python -m ptsearch.server --transport stdio --data-dir ./data

# Test SSE transport 
python -m ptsearch.server --transport sse --data-dir ./data
```

## 6. Troubleshooting

- Check `mcp_server.log` for detailed logs
- Verify OPENAI_API_KEY is set in environment
- Ensure data directory exists with required files