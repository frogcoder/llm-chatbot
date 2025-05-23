"""Configuration settings for the chatbot application."""
import os
from pathlib import Path

# Database settings
DB_FILE = os.environ.get("CHATBOT_DB_FILE", "bank.db")
DB_INIT_SQL = Path(__file__).parent / "init.sql"

# Account number mappings (for client-side account name resolution)
ACCOUNT_MAPPINGS = {
    "checking": "1234567890",
    "chequing": "1234567890",
    "cheque": "1234567890",
    "saving": "2345678901",
    "savings": "2345678901",
    "credit": "3456789012",
    "credit card": "3456789012"
}

# Default user for testing
DEFAULT_USER_ID = "test1"

# Vector database settings
VECTOR_DB_DIR = os.environ.get("VECTOR_DB_DIR", "./chroma_db")
DOCS_DIRECTORY = os.environ.get("DOCS_DIRECTORY", "./rbc_documents")

# API settings
MCP_HOST = os.environ.get("MCP_HOST", "127.0.0.1")
MCP_PORT = int(os.environ.get("MCP_PORT", "8050"))
MCP_NAME = os.environ.get("MCP_NAME", "RBC-RAG-MCP")
