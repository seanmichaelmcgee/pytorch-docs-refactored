"""
Settings module for PyTorch Documentation Search Tool.
Centralizes configuration with environment variable support and validation.
"""

import os
from dataclasses import dataclass, field
from typing import Optional, Dict, Any

@dataclass
class Settings:
    """Application settings with defaults and environment variable overrides."""
    
    # API settings
    openai_api_key: str = ""
    embedding_model: str = "text-embedding-3-large"
    embedding_dimensions: int = 3072
    
    # Document processing
    chunk_size: int = 1000
    overlap_size: int = 200
    
    # Search configuration
    max_results: int = 5
    
    # Database configuration
    db_dir: str = "./data/chroma_db"
    collection_name: str = "pytorch_docs"
    
    # Cache configuration
    cache_dir: str = "./data/embedding_cache"
    max_cache_size_gb: float = 1.0
    
    # File paths
    default_chunks_path: str = "./data/chunks.json"
    default_embeddings_path: str = "./data/chunks_with_embeddings.json"
    
    # MCP Configuration
    tool_name: str = "search_pytorch_docs"
    tool_description: str = ("Search PyTorch documentation or examples. Call when the user asks "
                             "about a PyTorch API, error message, best-practice or needs a code snippet.")
    
    def __post_init__(self):
        """Load settings from environment variables."""
        # Load all settings from environment variables
        for field_name in self.__dataclass_fields__:
            env_name = f"PTSEARCH_{field_name.upper()}"
            env_value = os.environ.get(env_name)
            
            if env_value is not None:
                field_type = self.__dataclass_fields__[field_name].type
                # Convert the string to the appropriate type
                if field_type == int:
                    setattr(self, field_name, int(env_value))
                elif field_type == float:
                    setattr(self, field_name, float(env_value))
                elif field_type == bool:
                    setattr(self, field_name, env_value.lower() in ('true', 'yes', '1'))
                else:
                    setattr(self, field_name, env_value)
        
        # Special case for OPENAI_API_KEY which has a different env var name
        if not self.openai_api_key:
            self.openai_api_key = os.environ.get("OPENAI_API_KEY", "")
    
    def validate(self) -> Dict[str, str]:
        """Validate settings and return any errors."""
        errors = {}
        
        # Validate required settings
        if not self.openai_api_key:
            errors["openai_api_key"] = "OPENAI_API_KEY environment variable is required"
        
        # Validate numeric settings
        if self.chunk_size <= 0:
            errors["chunk_size"] = "Chunk size must be positive"
        if self.overlap_size < 0:
            errors["overlap_size"] = "Overlap size cannot be negative"
        if self.max_results <= 0:
            errors["max_results"] = "Max results must be positive"
        
        return errors

# Singleton instance of settings
settings = Settings()