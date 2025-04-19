#!/usr/bin/env python3
"""
Embedding generation script for PyTorch Documentation Search Tool.
Generates embeddings for document chunks with caching.
"""

import argparse
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ptsearch.embedding import EmbeddingGenerator
from ptsearch.config import DEFAULT_CHUNKS_PATH, DEFAULT_EMBEDDINGS_PATH

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Generate embeddings for document chunks")
    parser.add_argument("--input-file", type=str, default=DEFAULT_CHUNKS_PATH,
                      help="Input JSON file with document chunks")
    parser.add_argument("--output-file", type=str, default=DEFAULT_EMBEDDINGS_PATH,
                      help="Output JSON file to save chunks with embeddings")
    parser.add_argument("--batch-size", type=int, default=20,
                      help="Batch size for embedding generation")
    parser.add_argument("--no-cache", action="store_true",
                      help="Disable embedding cache")
    args = parser.parse_args()
    
    # Create generator and process embeddings
    generator = EmbeddingGenerator(use_cache=not args.no_cache)
    chunks = generator.process_file(args.input_file, args.output_file)
    
    print(f"Embedding generation complete! Processed {len(chunks)} chunks")
    print(f"Embeddings saved to {args.output_file}")

if __name__ == "__main__":
    main()