import os
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# Configure the Gemini API with the API key from .env
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables")
genai.configure(api_key=api_key)

from chatbot.config import VECTOR_DB_DIR

def create_vector_store(documents, persist_directory=None):
    if persist_directory is None:
        persist_directory = VECTOR_DB_DIR
    """Create a vector store from document chunks"""
    # Initialize the embeddings using Gemini with explicit API key
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=api_key
    )
    
    # Create the vector store (persistence is automatic)
    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    print(f"Vector store created with {len(documents)} document chunks")
    print(f"Vector store persisted to {persist_directory}")
    return vector_store

def load_vector_store(persist_directory=None):
    if persist_directory is None:
        persist_directory = VECTOR_DB_DIR
    """Load an existing vector store"""
    # Use the same API key as in create_vector_store
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=api_key
    )
    vector_store = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
    return vector_store
