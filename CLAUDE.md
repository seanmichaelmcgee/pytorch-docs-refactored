# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build/Lint/Test Commands
- Setup environment (Conda - strongly recommended): 
  ```bash
  # Create and activate the conda environment
  ./setup_conda_env.sh
  # OR manually
  conda env create -f environment.yml
  conda activate pytorch_docs_search
  ```
- [ONLY USE IF EXPLICITLY REQUESTED] Alternative setup (Virtual Environment): 
  ```bash
  python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
  ```
- Run tests: `pytest -v tests/`
- Run single test: `pytest -v tests/test_file.py::test_function`
- Format code: `black .`
- Lint code: `pytest --flake8`

## Code Style Guidelines
- Python: Version 3.10+ with type hints
- Imports: Group in order (stdlib, third-party, local) with alphabetical sorting
- Formatting: Use Black formatter with 88 character line limit
- Naming: snake_case for functions/variables, CamelCase for classes
- Error handling: Use try/except blocks with specific exceptions
- Documentation: Docstrings for all functions/classes using NumPy format
- Testing: Write unit tests for all components using pytest