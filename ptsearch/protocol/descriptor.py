"""
MCP tool descriptor definition for PyTorch Documentation Search Tool.
"""

from typing import Dict, Any

from ptsearch.config import settings

def get_tool_descriptor() -> Dict[str, Any]:
    """Get the MCP tool descriptor for PyTorch Documentation Search."""
    return {
        "name": settings.tool_name,
        "schema_version": "1.0",
        "type": "function",
        "description": settings.tool_description,
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "num_results": {"type": "integer", "default": settings.max_results},
                "filter": {"type": "string", "enum": ["code", "text", ""]},
            },
            "required": ["query"],
        }
    }