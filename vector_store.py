import os
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

def create_vector_store(documents, persist_directory="./chroma_db"):
    """Create a vector store from document chunks"""
    # Initialize the embeddings using Gemini
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    # Create and persist the vector store
    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    vector_store.persist()
    print(f"Vector store created with {len(documents)} document chunks")
    print(f"Vector store persisted to {persist_directory}")
    return vector_store

def load_vector_store(persist_directory="./chroma_db"):
    """Load an existing vector store"""
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
    return vector_store
