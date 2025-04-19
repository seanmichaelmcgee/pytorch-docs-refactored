# PyTorch Documentation Search - MCP Integration with Claude Code CLI

This guide explains how to set up and use the MCP integration for the PyTorch Documentation Search tool with Claude Code CLI.

## Overview

The PyTorch Documentation Search tool is now integrated with Claude Code CLI through the Model-Context Protocol (MCP), allowing Claude to directly access our semantic search capabilities.

Key features of this integration:
- Progressive search with fallback behavior
- MCP-compliant API endpoint
- Detailed timing and diagnostics
- Compatibility with both code and concept queries
- Structured JSON responses

## Setup Instructions

### 1. Install Required Dependencies

First, set up the environment using conda:

```bash
# Create and activate the conda environment
conda env create -f environment.yml
conda activate pytorch_docs_search
```

### 2. Set Environment Variables

The server requires an OpenAI API key for embeddings:

```bash
# Export your OpenAI API key
export OPENAI_API_KEY="your-api-key-here"
```

### 3. Start the Server

You have two options for running the server:

#### Option A: With UVX (Recommended)

```bash
# Run directly with UVX
uvx mcp-server-pytorch --transport sse --host 127.0.0.1 --port 5000 --data-dir ./data

# Or use the provided script
./run_mcp_uvx.sh
```

#### Option B: With Stdio Transport

```bash
# Run with stdio transport
./run_mcp.sh
```

### 4. Register the Tool with Claude Code CLI

Register the tool with Claude CLI using the exact name from the tool descriptor:

```bash
# For SSE transport
claude mcp add search_pytorch_docs http://localhost:5000/events --transport sse

# For stdio transport
claude mcp add search_pytorch_docs stdio ./run_mcp.sh
```

### 5. Verify Registration

Check that the tool is registered correctly:

```bash
claude mcp list
```

You should see `search_pytorch_docs` in the list of available tools.

## Usage

### Testing with CLI

To test the tool directly from the command line:

```bash
claude run tool search_pytorch_docs --input '{"query": "freeze layers in PyTorch"}'
```

For filtering results:

```bash
claude run tool search_pytorch_docs --input '{"query": "batch normalization", "filter": "code"}'
```

To retrieve more results:

```bash
claude run tool search_pytorch_docs --input '{"query": "autograd example", "num_results": 10}'
```

### Using with Claude CLI

When using Claude CLI, you can integrate the tool into your conversations:

```bash
claude run
```

Then within your conversation with Claude, you can ask about PyTorch topics and Claude will automatically use the tool to search the documentation.

## Command Line Options

The MCP server accepts the following command line options:

- `--transport {stdio,sse}`: Transport mechanism (default: stdio)
- `--host HOST`: Host to bind to for SSE transport (default: 0.0.0.0)
- `--port PORT`: Port to bind to for SSE transport (default: 5000)
- `--debug`: Enable debug mode
- `--data-dir PATH`: Path to the data directory containing chunks.json and chunks_with_embeddings.json

## Data Directory Structure

The tool expects the following files in the data directory:
- `chunks.json`: The raw document chunks
- `chunks_with_embeddings.json`: Cached document embeddings
- `chroma_db/`: Vector database files

## Monitoring and Logging

All API requests and responses are logged to `mcp_server.log` in the project root directory. This file contains detailed information about:

- Request timestamps and content
- Query processing stages
- Search timing information
- Any errors encountered
- Result counts and metadata

To monitor the log in real-time:

```bash
tail -f mcp_server.log
```

## Troubleshooting

### Common Issues

1. **Tool Registration Fails**
   - Ensure the server is running
   - Check that you have the correct URL (http://localhost:5000/events)
   - Verify you have the latest Claude CLI installed
   - Make sure the tool name matches exactly: `search_pytorch_docs`

2. **Server Won't Start with ConfigError**
   - Ensure the `OPENAI_API_KEY` is set in your environment
   - Check for any import errors in the console output
   - Verify the port 5000 is available

3. **No Results Returned**
   - Verify that the data files exist in the specified data directory
   - Check that the chunks and embeddings files have the expected content
   - Check the log file for detailed error messages

4. **Tool Not Found in Claude CLI**
   - Make sure the tool name in your registration command matches the descriptor (`search_pytorch_docs`)
   - Ensure the server is running when you try to use the tool

### Getting Help

If you encounter issues not covered here, check:
1. The main log file: `mcp_server.log`
2. The Python error output in the terminal running the server
3. The Claude CLI error messages when attempting to use the tool

## Architecture

The MCP integration consists of:

1. `mcp_server_pytorch/__main__.py`: Main entry point
2. `ptsearch/protocol/`: MCP protocol implementation
3. `ptsearch/transport/`: Transport implementations (SSE/stdio)
4. `ptsearch/core/`: Core search functionality

The standard flow is:
1. Client sends a query
2. MCP protocol handler processes the message
3. Query is passed to the search handler
4. Vector search happens via the SearchEngine
5. Results are formatted and returned

## Security Notes

- The server binds to 127.0.0.1 by default with UVX; only change to 0.0.0.0 if needed
- OpenAI API keys are loaded from environment variables; ensure they're properly secured
- The UVX tool.json can use ${OPENAI_API_KEY} to reference environment variables

## Next Steps

- Add authentication to the API endpoint
- Implement caching for frequent queries
- Add support for more filter types
- Create a dashboard for monitoring API usage and performance