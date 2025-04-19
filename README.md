# PyTorch Documentation Search Tool

A semantic search tool for PyTorch documentation with MCP integration for Claude Code.

## Overview

This tool provides semantic search capabilities over PyTorch documentation, allowing users to find relevant documentation, APIs, code examples, and error messages. It utilizes vector embeddings and semantic similarity to provide high-quality search results.

## Features

- Semantic search for PyTorch documentation
- Code-aware search results (differentiates between code and text)
- Easy integration with Claude Code via MCP
- Multiple transport options (STDIO, SSE, UVX)
- Configurable search parameters and result formatting

## Installation

### Environment Setup

Create a conda environment with all dependencies:

```bash
conda env create -f environment.yml
conda activate pytorch_docs_search
```

For a minimal environment:

```bash
conda env create -f minimal_env.yml
conda activate pytorch_docs_search_min
```

### API Key Setup

The tool requires an OpenAI API key for generating embeddings:

```bash
export OPENAI_API_KEY=your_key_here
```

## MCP Integration

The tool can be integrated with Claude Code in three ways:

### 1. Direct STDIO Integration (Local Development)

```bash
# Register with Claude CLI
./register_mcp.sh

# This runs:
# claude mcp add search_pytorch_docs stdio ./run_mcp.sh
```

### 2. SSE Integration (Server Deployment)

```bash
# Start the server
python -m ptsearch.server --transport sse --host 0.0.0.0 --port 5000

# Register with Claude CLI
claude mcp add search_pytorch_docs http://localhost:5000/events --transport sse
```

### 3. UVX Integration (Packaged Distribution)

```bash
# Run with UVX
./run_mcp_uvx.sh

# This executes:
# uvx mcp-server-pytorch --transport sse --host 127.0.0.1 --port 5000 --data-dir ./data
```

## Usage

Once registered with Claude Code, you can use the tool by asking questions about PyTorch:

```
How do I implement a custom dataset in PyTorch?
```

Claude Code will automatically use the PyTorch Documentation Search Tool to find relevant documentation.

## Direct CLI Usage

You can also use the tool directly:

```bash
# Search from command line
python -m ptsearch.server --transport stdio --data-dir ./data
```

## Architecture

- `ptsearch/server.py`: Unified server implementation
- `ptsearch/protocol/`: MCP protocol handling
- `ptsearch/transport/`: Transport implementations (STDIO, SSE)
- `ptsearch/core/`: Core search functionality

## Development

### Running Tests

```bash
pytest -v tests/
```

### Format Code

```bash
black .
```

## License

MIT License