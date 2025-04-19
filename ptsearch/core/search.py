"""
Search module for PyTorch Documentation Search Tool.
Combines embedding generation, database querying, and result formatting.
"""

from typing import List, Dict, Any, Optional
import time

from ptsearch.utils import logger
from ptsearch.utils.error import SearchError
from ptsearch.config import settings
from ptsearch.core.formatter import ResultFormatter
from ptsearch.core.database import DatabaseManager
from ptsearch.core.embedding import EmbeddingGenerator

class SearchEngine:
    """Main search engine that combines all components."""
    
    def __init__(self, database_manager: Optional[DatabaseManager] = None, 
                 embedding_generator: Optional[EmbeddingGenerator] = None):
        """Initialize search engine with components."""
        # Initialize components if not provided
        self.database = database_manager or DatabaseManager()
        self.embedder = embedding_generator or EmbeddingGenerator()
        self.formatter = ResultFormatter()
        
        logger.info("Search engine initialized")
    
    def search(self, query: str, num_results: int = settings.max_results, 
               filter_type: Optional[str] = None) -> Dict[str, Any]:
        """Search for documents matching the query."""
        start_time = time.time()
        timing = {}
        
        try:
            # Process query to get embedding and determine intent
            query_start = time.time()
            query_data = self._process_query(query)
            query_end = time.time()
            timing["query_processing"] = query_end - query_start
            
            # Log search info
            logger.info("Executing search", 
                       query=query, 
                       is_code_query=query_data["is_code_query"],
                       filter=filter_type)
            
            # Create filters
            filters = {"chunk_type": filter_type} if filter_type else None
            
            # Query database
            db_start = time.time()
            raw_results = self.database.query(
                query_data["embedding"],
                n_results=num_results,
                filters=filters
            )
            db_end = time.time()
            timing["database_query"] = db_end - db_start
            
            # Format results
            format_start = time.time()
            formatted_results = self.formatter.format_results(raw_results, query)
            format_end = time.time()
            timing["format_results"] = format_end - format_start
            
            # Rank results based on query intent
            rank_start = time.time()
            ranked_results = self.formatter.rank_results(
                formatted_results,
                query_data["is_code_query"]
            )
            rank_end = time.time()
            timing["rank_results"] = rank_end - rank_start
            
            # Add timing information and search metadata
            end_time = time.time()
            total_time = end_time - start_time
            
            # Add metadata to results
            result_count = len(ranked_results.get("results", []))
            ranked_results["metadata"] = {
                "timing": timing,
                "total_time": total_time,
                "result_count": result_count,
                "is_code_query": query_data["is_code_query"],
                "filter": filter_type
            }
            
            logger.info("Search completed", 
                      result_count=result_count,
                      time_taken=f"{total_time:.3f}s",
                      is_code_query=query_data["is_code_query"])
            
            return ranked_results
            
        except Exception as e:
            error_msg = f"Error during search: {e}"
            logger.exception(error_msg)
            raise SearchError(error_msg, details={
                "query": query,
                "filter": filter_type,
                "time_taken": time.time() - start_time
            })
    
    def _process_query(self, query: str) -> Dict[str, Any]:
        """Process query to determine intent and generate embedding."""
        # Clean query
        query = query.strip()
        
        # Generate embedding
        embedding = self.embedder.generate_embedding(query)
        
        # Determine if this is a code query
        is_code_query = self._is_code_query(query)
        
        return {
            "query": query,
            "embedding": embedding,
            "is_code_query": is_code_query
        }
    
    def _is_code_query(self, query: str) -> bool:
        """Determine if a query is looking for code."""
        query_lower = query.lower()
        
        # Code indicator keywords
        code_indicators = [
            "code", "example", "implementation", "function", "class", "method",
            "snippet", "syntax", "parameter", "argument", "return", "import",
            "module", "api", "call", "invoke", "instantiate", "create", "initialize"
        ]
        
        # Check for code indicators
        for indicator in code_indicators:
            if indicator in query_lower:
                return True
        
        # Check for code patterns
        code_patterns = [
            "def ", "class ", "import ", "from ", "torch.", "nn.",
            "->", "=>", "==", "!=", "+=", "-=", "*=", "():", "@"
        ]
        
        for pattern in code_patterns:
            if pattern in query:
                return True
        
        return False