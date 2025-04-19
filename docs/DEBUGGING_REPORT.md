# PyTorch Documentation Search MCP Integration Debugging Report

## Problem Overview

The PyTorch Documentation Search tool is failing to connect as an MCP server for Claude Code. When checking MCP server status using `claude mcp`, the `pytorch_search` server consistently shows a failure status, while other MCP servers like `fetch` are working correctly.

## Error Details

### Connection Errors

The MCP logs show consistent connection failures:

1. **Connection Timeout**:
   ```json
   {
     "error": "Connection failed: Connection to MCP server \"pytorch_search\" timed out after 30000ms",
     "timestamp": "2025-04-18T16:15:53.577Z"
   }
   ```

2. **Connection Closed**:
   ```json
   {
     "error": "Connection failed: MCP error -32000: Connection closed",
     "timestamp": "2025-04-18T17:53:14.634Z"
   }
   ```

## Implementation Details

### Current Integration Approach

The project attempts to implement MCP integration through two approaches:

1. **Direct STDIO Transport**: 
   - Implementation in `ptsearch/stdio.py`
   - Run via `run_mcp.sh` script
   - Registered via `register_mcp.sh`

2. **UVX Integration**:
   - Run via `run_mcp_uvx.sh` script
   - Registered via `register_mcp_uvx.sh`

### System Configuration

- **Conda Environment**: `pytorch_docs_search` (exists and appears correctly configured)
- **OpenAI API Key**: Present in environment (`~/.bashrc`)
- **UVX Installation**: Installed but appears to have configuration issues (commands like `uvx info`, `uvx list` failing)

## Key Code Components

1. **MCP Server Module** (`ptsearch/mcp.py`):
   - Flask-based implementation for SSE transport
   - Defines tool descriptor for PyTorch docs search
   - Handles API endpoints for MCP protocol

2. **STDIO Transport Module** (`ptsearch/stdio.py`):
   - JSON-RPC implementation for STDIO transport
   - Reuses tool descriptor from MCP module
   - Handles stdin/stdout for communication

3. **Embedding Module** (`ptsearch/embedding.py`):
   - OpenAI API integration for embeddings
   - Cache implementation
   - Error handling and retry logic

## Potential Issues

1. **API Key Validation**:
   - Both `mcp.py` and `stdio.py` contain early API key validation
   - While API key exists in environment, it may not be loaded in the conda environment or UVX context

2. **Process Management**:
   - STDIO transport relies on persistent shell process
   - If the process exits early, connection will be closed
   - No visibility into process exit codes or output

3. **UVX Configuration**:
   - UVX tool appears to have configuration issues (`uvx info`, `uvx list` commands fail)
   - May not be correctly finding and running the MCP server

4. **Environment Activation**:
   - The scripts include proper activation of conda environment
   - However, environment variables might not be propagating correctly

5. **Database Connectivity**:
   - Services depend on ChromaDB for vector storage
   - Errors in database initialization may cause early termination

## Attempted Solutions

From the codebase and commit history, the following approaches have been tried:

1. Direct STDIO implementation
2. UVX integration approach
3. Configuration adjustments in conda environment
4. Fixed UVX configuration to use conda environment (latest commit)

## Recommendations

1. **Enhanced Logging**:
   - Add more detailed logging throughout MCP server lifecycle
   - Capture startup logs, initialization errors, and exit reasons
   - Write to a dedicated log file for easier debugging

2. **Direct Testing**:
   - Create a simple test script to invoke the STDIO server directly
   - Test MCP protocol implementation without Claude CLI infrastructure
   - Validate responses to basic initialize/list_tools/call_tool requests

3. **Environment Validation**:
   - Add environment validation script to check for all dependencies
   - Verify API keys, database connectivity, and conda environment
   - Create reproducible test cases

4. **UVX Configuration**:
   - Debug UVX installation and configuration
   - Test UVX integration with simpler example first
   - Create full documentation for UVX integration process

5. **Process Management**:
   - Add error trapping in scripts to report exit codes
   - Consider using named pipes for additional communication channel
   - Add health check capability to main scripts

## Next Steps

1. Implement detailed logging to identify exact failure point
2. Create a validation script to test each component individually
3. Debug UVX configuration issues
4. Implement proper error reporting in startup scripts
5. Consider alternative transport methods if STDIO proves unreliable

This report should provide a starting point for another team to continue debugging and resolving the MCP integration issues.