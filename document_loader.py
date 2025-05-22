import os
import glob
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def load_documents(directory_path):
    """Load documents from a directory containing PDFs and text files"""
    # Get all PDF files in the directory
    pdf_files = glob.glob(os.path.join(directory_path, "**/*.pdf"), recursive=True)
    
    # Get all text files in the directory
    txt_files = glob.glob(os.path.join(directory_path, "**/*.txt"), recursive=True)
    
    # Load each document file individually to handle errors gracefully
    all_documents = []
    
    # Process PDF files
    for pdf_file in pdf_files:
        try:
            loader = PyPDFLoader(pdf_file)
            documents = loader.load()
            all_documents.extend(documents)
            print(f"Loaded {len(documents)} pages from {os.path.basename(pdf_file)}")
        except Exception as e:
            print(f"Error loading file {pdf_file}")
            print(f"  Error details: {str(e)}")
    
    # Process text files
    for txt_file in txt_files:
        try:
            loader = TextLoader(txt_file)
            documents = loader.load()
            all_documents.extend(documents)
            print(f"Loaded text file: {os.path.basename(txt_file)}")
        except Exception as e:
            print(f"Error loading file {txt_file}")
            print(f"  Error details: {str(e)}")
    
    print(f"Loaded {len(all_documents)} document pages in total")
    return all_documents

def split_documents(documents, chunk_size=1000, chunk_overlap=200):
    """Split documents into chunks for better processing"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks")
    return chunks
