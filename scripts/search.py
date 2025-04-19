#!/usr/bin/env python3
"""
Search script for PyTorch Documentation Search Tool.
Provides command-line interface for searching documentation.
"""

import sys
import os
import json
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ptsearch.database import DatabaseManager
from ptsearch.embedding import EmbeddingGenerator
from ptsearch.search import SearchEngine
from ptsearch.config import MAX_RESULTS

def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description='Search PyTorch documentation')
    parser.add_argument('query', nargs='?', help='The search query')
    parser.add_argument('--interactive', '-i', action='store_true', help='Run in interactive mode')
    parser.add_argument('--results', '-n', type=int, default=MAX_RESULTS, help='Number of results to return')
    parser.add_argument('--filter', '-f', choices=['code', 'text'], help='Filter results by type')
    parser.add_argument('--json', '-j', action='store_true', help='Output results as JSON')
    args = parser.parse_args()
    
    # Initialize components
    db_manager = DatabaseManager()
    embedding_generator = EmbeddingGenerator()
    search_engine = SearchEngine(db_manager, embedding_generator)
    
    if args.interactive:
        # Interactive mode
        print("PyTorch Documentation Search (type 'exit' to quit)")
        while True:
            query = input("\nEnter search query: ")
            if query.lower() in ('exit', 'quit'):
                break
            
            results = search_engine.search(query, args.results, args.filter)
            
            if "error" in results:
                print(f"Error: {results['error']}")
            else:
                print(f"\nFound {len(results['results'])} results for '{query}':")
                
                for i, res in enumerate(results["results"]):
                    print(f"\n--- Result {i+1} ({res['chunk_type']}) ---")
                    print(f"Title: {res['title']}")
                    print(f"Source: {res['source']}")
                    print(f"Score: {res['score']:.4f}")
                    print(f"Snippet: {res['snippet']}")
    
    elif args.query:
        # Direct query mode
        results = search_engine.search(args.query, args.results, args.filter)
        
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print(f"\nFound {len(results['results'])} results for '{args.query}':")
            
            for i, res in enumerate(results["results"]):
                print(f"\n--- Result {i+1} ({res['chunk_type']}) ---")
                print(f"Title: {res['title']}")
                print(f"Source: {res['source']}")
                print(f"Score: {res['score']:.4f}")
                print(f"Snippet: {res['snippet']}")
    
    else:
        # Read from stdin (for Claude Code tool integration)
        query = sys.stdin.read().strip()
        if query:
            results = search_engine.search(query, args.results)
            print(json.dumps(results))
        else:
            print(json.dumps({"error": "No query provided", "results": []}))

if __name__ == "__main__":
    main()