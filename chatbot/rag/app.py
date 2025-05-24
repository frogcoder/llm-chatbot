from chatbot.rag.document_loader import load_documents, split_documents
from chatbot.rag.vector_store import create_vector_store
from chatbot.rag.rag_chatbot import RBCChatbot
import os
import sys

def initialize_database():
    """Initialize the vector database if it doesn't exist"""
    from chatbot.config import VECTOR_DB_DIR, DOCS_DIRECTORY
    
    if not os.path.exists(VECTOR_DB_DIR):
        print("Creating vector database...")
        documents = load_documents(DOCS_DIRECTORY)
        chunks = split_documents(documents)
        create_vector_store(chunks, VECTOR_DB_DIR)
        print("Vector database created successfully!")
    else:
        print("Using existing vector database.")

def main():
    # Initialize the database if needed
    initialize_database()
    
    # Create the chatbot
    chatbot = RBCChatbot()
    
    print("RBC Bank Assistant (type 'exit' to quit)")
    print("-----------------------------------------")
    
    while True:
        user_input = input("\nYour question: ")
        
        if user_input.lower() in ["exit", "quit", "q"]:
            print("Thank you for using the RBC Bank Assistant!")
            break
        
        response = chatbot.answer_question(user_input)
        
        print("\nAnswer:", response["answer"])
        
        if response["sources"]:
            print("\nSources:")
            for source in response["sources"]:
                print(f"- {source}")

if __name__ == "__main__":
    main()
