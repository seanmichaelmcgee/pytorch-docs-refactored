"""Compatibility utilities for handling API and library version differences."""

import numpy as np

# Add monkey patch for NumPy 2.0+ compatibility with ChromaDB
if not hasattr(np, 'float_'):
    np.float_ = np.float64
