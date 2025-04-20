# PyTorch Documentation Search Tool (Project Paused)

A semantic search prototype for PyTorch documentation with command-line capabilities.

## Current Status (April 19, 2025)

**⚠️ This project is currently paused for significant redesign.**

The tool provides a basic command-line search interface for PyTorch documentation but requires substantial improvements in several areas. While the core embedding and search functionality works at a basic level, both relevance quality and MCP integration require additional development.

### Example Output

```
$ python scripts/search.py "How are multi-attention heads plotted out in PyTorch?"

Found 5 results for 'How are multi-attention heads plotted out in PyTorch?':

--- Result 1 (code) ---
Title: plot_visualization_utils.py
Source: plot_visualization_utils.py
Score: 0.3714
Snippet: # models. Let's start by analyzing the output of a Mask-RCNN model. Note that...

--- Result 2 (code) ---
Title: plot_transforms_getting_started.py
Source: plot_transforms_getting_started.py
Score: 0.3571
Snippet: https://github.com/pytorch/vision/tree/main/gallery/...
```

## What Works

✅ **Basic Semantic Search**: Command-line interface for querying PyTorch documentation  
✅ **Vector Database**: Functional ChromaDB integration for storing and querying embeddings  
✅ **Content Differentiation**: Distinguishes between code and text content  
✅ **Interactive Mode**: Option to run continuous interactive queries in a session

## What Needs Improvement

❌ **Relevance Quality**: Moderate similarity scores (0.35-0.37) indicate suboptimal results  
❌ **Content Coverage**: Specialized topics may have insufficient representation in the database  
❌ **Chunking Strategy**: Current approach breaks documentation at arbitrary points  
❌ **Result Presentation**: Snippets are too short and lack sufficient context  
❌ **MCP Integration**: Connection timeout issues prevent Claude Code integration  

## Getting Started

### Environment Setup

Create a conda environment with all dependencies:

```bash
conda env create -f environment.yml
conda activate pytorch_docs_search
```

### API Key Setup

The tool requires an OpenAI API key for embedding generation:

```bash
export OPENAI_API_KEY=your_key_here
```

## Command-line Usage

```bash
# Search with a direct query
python scripts/search.py "your search query here"

# Run in interactive mode
python scripts/search.py --interactive

# Additional options
python scripts/search.py "query" --results 5  # Limit to 5 results
python scripts/search.py "query" --filter code  # Only code results
python scripts/search.py "query" --json  # Output in JSON format
```

## Project Architecture

- `ptsearch/core/`: Core search functionality (database, embedding, search)
- `ptsearch/config/`: Configuration management
- `ptsearch/utils/`: Utility functions and logging
- `scripts/`: Command-line tools
- `data/`: Embedded documentation and database
- `ptsearch/protocol/`: MCP protocol handling (currently unused)
- `ptsearch/transport/`: Transport implementations (STDIO, SSE) (currently unused)

## Why This Project Is Paused

After evaluating the current implementation, we've identified several challenges that require significant redesign:

1. **Data Quality Issues**: The current embedding approach doesn't capture semantic relationships between PyTorch concepts effectively enough. Relevance scores around 0.35-0.37 are too low for a quality user experience.

2. **Chunking Limitations**: Our current method divides documentation into chunks based on character count rather than conceptual boundaries, leading to fragmented results.

3. **MCP Integration Problems**: Despite multiple implementation approaches, we encountered persistent timeout issues when attempting to integrate with Claude Code:
   - STDIO integration failed at connection establishment
   - Flask server with SSE transport couldn't maintain stable connections
   - UVX deployment experienced similar timeout issues

## Future Roadmap

When development resumes, we plan to focus on:

1. **Improved Chunking Strategy**: Implement semantic chunking that preserves conceptual boundaries
2. **Enhanced Result Formatting**: Provide more context and better snippet selection
3. **Expanded Documentation Coverage**: Ensure comprehensive representation of all PyTorch topics
4. **MCP Integration Redesign**: Work with the Claude team to resolve timeout issues

## Development

### Running Tests

```bash
pytest -v tests/
```

### Format Code

```bash
black .
```

## License

MIT License