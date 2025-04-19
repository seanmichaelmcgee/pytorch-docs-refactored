"""
Database module for PyTorch Documentation Search Tool.
Handles storage and retrieval of chunks in ChromaDB.
"""

import os
import json
from typing import List, Dict, Any, Optional

import chromadb

from ptsearch.utils import logger
from ptsearch.utils.error import DatabaseError
from ptsearch.config import settings

class DatabaseManager:
    """Manages storage and retrieval of document chunks in ChromaDB."""
    
    def __init__(self, db_dir: str = settings.db_dir, collection_name: str = settings.collection_name):
        """Initialize database manager for ChromaDB."""
        self.db_dir = db_dir
        self.collection_name = collection_name
        self.collection = None
        
        # Create directory if it doesn't exist
        os.makedirs(db_dir, exist_ok=True)
        
        # Initialize ChromaDB client
        try:
            self.client = chromadb.PersistentClient(path=db_dir)
            logger.info(f"ChromaDB client initialized", path=db_dir)
        except Exception as e:
            error_msg = f"Error initializing ChromaDB client: {e}"
            logger.error(error_msg)
            raise DatabaseError(error_msg)
    
    def reset_collection(self) -> None:
        """Delete and recreate the collection with standard settings."""
        try:
            self.client.delete_collection(self.collection_name)
            logger.info(f"Deleted existing collection", collection=self.collection_name)
        except Exception as e:
            # Collection might not exist yet
            logger.info(f"No existing collection to delete", error=str(e))
        
        # Create a new collection with standard settings
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        logger.info(f"Created new collection", collection=self.collection_name)
    
    def get_collection(self):
        """Get or create the collection."""
        if self.collection is not None:
            return self.collection
            
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
            logger.info(f"Retrieved existing collection", collection=self.collection_name)
        except Exception as e:
            # Collection doesn't exist, create it
            logger.info(f"Creating new collection", error=str(e))
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Created new collection", collection=self.collection_name)
        
        return self.collection
    
    def add_chunks(self, chunks: List[Dict[str, Any]], batch_size: int = 50) -> None:
        """Add chunks to the collection with batching."""
        collection = self.get_collection()
        
        # Prepare data for ChromaDB
        ids = [str(chunk.get("id", idx)) for idx, chunk in enumerate(chunks)]
        embeddings = [self._ensure_vector_format(chunk.get("embedding")) for chunk in chunks]
        documents = [chunk.get("text", "") for chunk in chunks]
        metadatas = [chunk.get("metadata", {}) for chunk in chunks]
        
        # Add data in batches
        total_batches = (len(chunks) - 1) // batch_size + 1
        logger.info(f"Adding chunks in batches", count=len(chunks), batches=total_batches)
        
        for i in range(0, len(chunks), batch_size):
            end_idx = min(i + batch_size, len(chunks))
            batch_num = i // batch_size + 1
            
            try:
                collection.add(
                    ids=ids[i:end_idx],
                    embeddings=embeddings[i:end_idx],
                    documents=documents[i:end_idx],
                    metadatas=metadatas[i:end_idx]
                )
                logger.info(f"Added batch", batch=batch_num, total=total_batches, chunks=end_idx-i)
                
            except Exception as e:
                error_msg = f"Error adding batch {batch_num}: {e}"
                logger.error(error_msg)
                raise DatabaseError(error_msg, details={
                    "batch": batch_num,
                    "total_batches": total_batches,
                    "batch_size": end_idx - i
                })
    
    def query(self, query_embedding: List[float], n_results: int = 5, 
              filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Query the collection with vector search."""
        collection = self.get_collection()
        
        # Ensure query embedding has the correct format
        query_embedding = self._ensure_vector_format(query_embedding)
        
        # Prepare query parameters
        query_params = {
            "query_embeddings": [query_embedding],
            "n_results": n_results,
            "include": ["documents", "metadatas", "distances"]
        }
        
        # Add filters if provided
        if filters:
            query_params["where"] = filters
        
        # Execute query
        try:
            results = collection.query(**query_params)
            
            # Format results for consistency
            formatted_results = {
                "ids": results.get("ids", [[]]),
                "documents": results.get("documents", [[]]),
                "metadatas": results.get("metadatas", [[]]),
                "distances": results.get("distances", [[]])
            }
            
            # Log query info
            if formatted_results["ids"] and formatted_results["ids"][0]:
                logger.info(f"Query completed", results_count=len(formatted_results["ids"][0]))
            
            return formatted_results
        except Exception as e:
            error_msg = f"Error during query: {e}"
            logger.error(error_msg)
            raise DatabaseError(error_msg)
    
    def load_from_file(self, filepath: str, reset: bool = True, batch_size: int = 50) -> None:
        """Load chunks from a file into ChromaDB."""
        logger.info(f"Loading chunks from file", path=filepath)
        
        # Load the chunks
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                chunks = json.load(f)
            
            logger.info(f"Loaded chunks from file", count=len(chunks))
            
            # Reset collection if requested
            if reset:
                self.reset_collection()
            
            # Add chunks to collection
            self.add_chunks(chunks, batch_size)
            
            logger.info(f"Successfully loaded chunks into ChromaDB", count=len(chunks))
        except Exception as e:
            error_msg = f"Error loading from file: {e}"
            logger.error(error_msg)
            raise DatabaseError(error_msg, details={"filepath": filepath})
    
    def get_stats(self) -> Dict[str, Any]:
        """Get basic statistics about the collection."""
        collection = self.get_collection()
        
        try:
            # Get count
            count = collection.count()
            
            return {
                "total_chunks": count,
                "collection_name": self.collection_name,
                "db_dir": self.db_dir
            }
        except Exception as e:
            error_msg = f"Error getting collection stats: {e}"
            logger.error(error_msg)
            raise DatabaseError(error_msg)
    
    def _ensure_vector_format(self, embedding: Any) -> List[float]:
        """Ensure vector is in the correct format for ChromaDB."""
        # Handle empty or None embeddings
        if not embedding:
            return [0.0] * settings.embedding_dimensions
        
        # Handle NumPy arrays
        if hasattr(embedding, "tolist"):
            embedding = embedding.tolist()
        
        # Ensure all values are Python floats
        try:
            embedding = [float(x) for x in embedding]
        except Exception as e:
            logger.error(f"Error converting embedding values to float", error=str(e))
            return [0.0] * settings.embedding_dimensions
        
        # Verify dimensions
        if len(embedding) != settings.embedding_dimensions:
            # Pad or truncate if necessary
            if len(embedding) < settings.embedding_dimensions:
                logger.warning(f"Padding embedding dimensions", 
                              from_dim=len(embedding), 
                              to_dim=settings.embedding_dimensions)
                embedding.extend([0.0] * (settings.embedding_dimensions - len(embedding)))
            else:
                logger.warning(f"Truncating embedding dimensions", 
                              from_dim=len(embedding), 
                              to_dim=settings.embedding_dimensions)
                embedding = embedding[:settings.embedding_dimensions]
        
        return embedding