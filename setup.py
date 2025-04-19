# setup.py
from setuptools import setup, find_packages

setup(
    name="mcp-server-pytorch",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "flask>=2.2.3",
        "openai>=1.2.4",
        "chromadb>=0.4.18",
        "tree-sitter>=0.20.1",
        "tree-sitter-languages>=1.7.0",
        "python-dotenv>=1.0.0",
        "flask-cors>=3.0.10",
        "mcp>=1.1.3"
    ],
    entry_points={
        'console_scripts': [
            'mcp-server-pytorch=mcp_server_pytorch:main',
        ],
    },
)
