import os
from dotenv import load_dotenv
import google.generativeai as genai
from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI
from vector_store import load_vector_store

load_dotenv()

# Configure the Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class RBCChatbot:
    def __init__(self, persist_directory="./chroma_db"):
        # Load the vector store
        self.vector_store = load_vector_store(persist_directory)
        
        # Initialize the LLM
        self.llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.2)
        
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
    
    def answer_question(self, question):
        """Answer a question using RAG"""
        try:
            # Combine the system prompt with the user's question
            full_query = f"{self.system_prompt}\n\nQuestion: {question}"
            
            # Get the answer from the chain
            result = self.qa_chain({"query": full_query})
            
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
