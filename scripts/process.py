#!/usr/bin/env python3
"""
Document processing script for PyTorch Documentation Search Tool.
Processes documentation into chunks with code-aware boundaries.
"""

import argparse
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ptsearch.document import DocumentProcessor
from ptsearch.config import DEFAULT_CHUNKS_PATH, CHUNK_SIZE, OVERLAP_SIZE

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Process documents into chunks")
    parser.add_argument("--docs-dir", type=str, required=True,
                      help="Directory containing documentation files")
    parser.add_argument("--output-file", type=str, default=DEFAULT_CHUNKS_PATH,
                      help="Output JSON file to save chunks")
    parser.add_argument("--chunk-size", type=int, default=CHUNK_SIZE,
                      help="Size of document chunks")
    parser.add_argument("--overlap", type=int, default=OVERLAP_SIZE,
                      help="Overlap between chunks")
    args = parser.parse_args()
    
    # Create processor and process documents
    processor = DocumentProcessor(chunk_size=args.chunk_size, overlap=args.overlap)
    chunks = processor.process_directory(args.docs_dir, args.output_file)
    
    print(f"Processing complete! Generated {len(chunks)} chunks from {args.docs_dir}")
    print(f"Chunks saved to {args.output_file}")

if __name__ == "__main__":
    main()