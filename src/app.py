from document_loader import load_documents, split_documents
from vector_store import create_vector_store
from rag_chatbot import RBCChatbot
import os
import sys

def initialize_database(docs_directory):
    """Initialize the vector database if it doesn't exist"""
    if not os.path.exists("./chroma_db"):
        print("Creating vector database...")
        documents = load_documents(docs_directory)
        chunks = split_documents(documents)
        create_vector_store(chunks)
        print("Vector database created successfully!")
    else:
        print("Using existing vector database.")

def main():
    # Path to your RBC documents
    docs_directory = "./rbc_documents"  # Update this to your actual path
    
    # Initialize the database if needed
    initialize_database(docs_directory)
    
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
