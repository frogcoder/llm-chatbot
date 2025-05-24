import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai
from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI

# Handle imports whether called directly or from MCP
try:
    from chatbot.rag.vector_store import load_vector_store, create_vector_store
    from chatbot.rag.document_loader import load_documents, split_documents
except ImportError:
    from vector_store import load_vector_store, create_vector_store
    from document_loader import load_documents, split_documents

load_dotenv()

# Configure the Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class RBCChatbot:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        """Singleton pattern to ensure only one instance is created"""
        if cls._instance is None:
            cls._instance = super(RBCChatbot, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, persist_directory=None):
        from chatbot.config import VECTOR_DB_DIR
        
        # Use config value if persist_directory is not provided
        if persist_directory is None:
            persist_directory = VECTOR_DB_DIR
        # Only initialize once
        if getattr(self, '_initialized', False):
            return
            
        # Initialize the vector store
        self._ensure_vector_store_exists(persist_directory)
        self.vector_store = load_vector_store(persist_directory)
        
        # Initialize the LLM with explicit API key
        api_key = os.getenv("GEMINI_API_KEY")
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.2, google_api_key=api_key)
        
        # Create the retrieval chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(search_kwargs={"k": 5}),
            return_source_documents=True
        )
        
        # Set a system prompt for better context
        self.system_prompt = """
        You are an AI assistant for RBC Bank. Your purpose is to provide accurate information 
        about RBC's products, services, and policies based on the official documentation. 
        If you're unsure or the information isn't in the provided context, acknowledge that 
        and suggest the user contact RBC directly. Always be professional, helpful, and concise.
        """
        
        self._initialized = True
    
    def _ensure_vector_store_exists(self, persist_directory):
        """Make sure the vector store exists, create it if it doesn't"""
        from chatbot.config import DOCS_DIRECTORY
        
        if not os.path.exists(persist_directory):
            print("Vector store not found. Creating new vector store...")
            if os.path.exists(DOCS_DIRECTORY):
                documents = load_documents(DOCS_DIRECTORY)
                chunks = split_documents(documents)
                create_vector_store(chunks, persist_directory)
            else:
                print(f"Warning: Documents directory {DOCS_DIRECTORY} not found.")
                print("Creating empty vector store.")
                # Create an empty vector store
                create_vector_store([], persist_directory)
    
    def answer_question(self, question):
        """Answer a question using RAG"""
        try:
            # Combine the system prompt with the user's question
            full_query = f"{self.system_prompt}\n\nQuestion: {question}"
            
            # Get the answer from the chain using invoke instead of __call__
            result = self.qa_chain.invoke({"query": full_query})
            
            # Extract the answer and sources
            answer = result["result"]
            source_docs = result["source_documents"]
            
            # Format sources for citation
            sources = []
            for doc in source_docs:
                if hasattr(doc, "metadata") and "source" in doc.metadata:
                    sources.append(doc.metadata["source"])
            
            # Return the answer and unique sources
            return {
                "answer": answer,
                "sources": list(set(sources))
            }
        except Exception as e:
            return {
                "answer": f"I encountered an error: {str(e)}",
                "sources": []
            }
    
    def get_relevant_documents(self, query):
        """Retrieve relevant documents for a query without generating an answer"""
        try:
            docs = self.vector_store.similarity_search(query, k=5)
            sources = []
            for doc in docs:
                if hasattr(doc, "metadata") and "source" in doc.metadata:
                    sources.append(doc.metadata["source"])
            return {
                "documents": docs,
                "sources": list(set(sources))
            }
        except Exception as e:
            return {
                "documents": [],
                "sources": [],
                "error": str(e)
            }
