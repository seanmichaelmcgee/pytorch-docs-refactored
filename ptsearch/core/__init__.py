"""
Core functionality for PyTorch Documentation Search Tool.
"""

# Import compatibility patches first
from ptsearch.utils.compat import *

from ptsearch.core.database import DatabaseManager
from ptsearch.core.embedding import EmbeddingGenerator
from ptsearch.core.search import SearchEngine
from ptsearch.core.formatter import ResultFormatter

__all__ = ["DatabaseManager", "EmbeddingGenerator", "SearchEngine", "ResultFormatter"]