#!/usr/bin/env python3
"""
Database indexing script for PyTorch Documentation Search Tool.
Loads embeddings into ChromaDB for vector search.
"""

import argparse
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ptsearch.database import DatabaseManager
from ptsearch.config import DEFAULT_EMBEDDINGS_PATH

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Index chunks into database")
    parser.add_argument("--input-file", type=str, default=DEFAULT_EMBEDDINGS_PATH,
                      help="Input JSON file with chunks and embeddings")
    parser.add_argument("--batch-size", type=int, default=50,
                      help="Batch size for database operations")
    parser.add_argument("--no-reset", action="store_true",
                      help="Don't reset the collection before loading")
    parser.add_argument("--stats", action="store_true",
                      help="Show database statistics after loading")
    args = parser.parse_args()
    
    # Initialize database manager
    db_manager = DatabaseManager()
    
    # Load chunks into database
    db_manager.load_from_file(
        args.input_file, 
        reset=not args.no_reset, 
        batch_size=args.batch_size
    )
    
    # Show stats if requested
    if args.stats:
        stats = db_manager.get_stats()
        print("\nDatabase Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")

if __name__ == "__main__":
    main()