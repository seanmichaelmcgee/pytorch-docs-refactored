"""
Result formatter module for PyTorch Documentation Search Tool.
Formats and ranks search results.
"""

from typing import List, Dict, Any, Optional

from ptsearch.utils import logger
from ptsearch.utils.error import SearchError

class ResultFormatter:
    """Formats and ranks search results."""
    
    def format_results(self, results: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Format raw ChromaDB results into a structured response."""
        formatted_results = []
        
        # Handle empty results
        if results is None:
            logger.warning("Received None results to format")
            return {
                "results": [],
                "query": query,
                "count": 0
            }
        
        # Extract data from ChromaDB response
        try:
            if isinstance(results.get('documents'), list):
                if len(results['documents']) > 0 and isinstance(results['documents'][0], list):
                    # Nested lists format (older ChromaDB versions)
                    documents = results.get('documents', [[]])[0]
                    metadatas = results.get('metadatas', [[]])[0]
                    distances = results.get('distances', [[]])[0]
                else:
                    # Flat lists format (newer ChromaDB versions)
                    documents = results.get('documents', [])
                    metadatas = results.get('metadatas', [])
                    distances = results.get('distances', [])
            else:
                # Empty or unexpected format
                documents = []
                metadatas = []
                distances = []
                
            # Log the number of results
            logger.info(f"Formatting search results", count=len(documents))
            
            # Format each result
            for i, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances)):
                # Create snippet
                max_snippet_length = 250
                snippet = doc[:max_snippet_length] + "..." if len(doc) > max_snippet_length else doc
                
                # Convert distance to similarity score (1.0 is exact match)
                if isinstance(distance, (int, float)):
                    similarity = 1.0 - distance
                else:
                    similarity = 0.5  # Default if distance is not a scalar
                
                # Extract metadata fields with fallbacks
                if isinstance(metadata, dict):
                    title = metadata.get("title", f"Result {i+1}")
                    source = metadata.get("source", "")
                    chunk_type = metadata.get("chunk_type", "unknown")
                    language = metadata.get("language", "")
                    section = metadata.get("section", "")
                else:
                    # Handle unexpected metadata format
                    logger.warning(f"Unexpected metadata format", type=str(type(metadata)))
                    title = f"Result {i+1}"
                    source = ""
                    chunk_type = "unknown"
                    language = ""
                    section = ""
                
                # Add formatted result
                formatted_results.append({
                    "title": title,
                    "snippet": snippet,
                    "source": source,
                    "chunk_type": chunk_type,
                    "language": language,
                    "section": section,
                    "score": round(float(similarity), 4)
                })
        except Exception as e:
            error_msg = f"Error formatting results: {e}"
            logger.error(error_msg)
            raise SearchError(error_msg)
        
        # Return formatted response
        return {
            "results": formatted_results,
            "query": query,
            "count": len(formatted_results)
        }
    
    def rank_results(self, results: Dict[str, Any], is_code_query: bool) -> Dict[str, Any]:
        """Rank results based on query type with intelligent scoring."""
        if "results" not in results or not results["results"]:
            return results
        
        formatted_results = results["results"]
        
        # Set up ranking parameters
        boost_factor = 1.2  # 20% boost for matching content type
        title_boost = 1.1   # 10% boost for matches in title
        
        for result in formatted_results:
            base_score = result["score"]
            
            # Apply content type boosting
            if is_code_query and result.get("chunk_type") == "code":
                result["score"] = min(1.0, base_score * boost_factor)
                result["match_reason"] = "code query & code content"
            elif not is_code_query and result.get("chunk_type") == "text":
                result["score"] = min(1.0, base_score * boost_factor)
                result["match_reason"] = "concept query & text content"
            
            # Additional boosting for title matches
            title = result.get("title", "").lower()
            query_terms = results.get("query", "").lower().split()
            
            title_match = any(term in title for term in query_terms if len(term) > 3)
            if title_match:
                result["score"] = min(1.0, result["score"] * title_boost)
                result["title_match"] = True
            
            # Round score for consistency
            result["score"] = round(result["score"], 4)
        
        # Re-sort by score
        formatted_results.sort(key=lambda x: x["score"], reverse=True)
        
        # Update results
        results["results"] = formatted_results
        results["is_code_query"] = is_code_query
        
        # Log ranking results
        if formatted_results:
            logger.info(f"Ranked results", 
                       count=len(formatted_results), 
                       top_score=formatted_results[0]["score"], 
                       is_code_query=is_code_query)
        
        return results