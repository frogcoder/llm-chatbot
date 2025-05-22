# RBC Bank RAG Chatbot

A bank Chatbot concept utilizing LLM & RAG with API integrations for RBC Bank documents.

## Current Features

1. **Document Retrieval**: Automatically scrapes and processes RBC Bank documents
2. **RAG-based Answers**: Provides accurate responses based on official RBC documentation
3. **Conversational Interface**: Simple command-line interface for asking questions

## Planned Features

1. **Prompt engineering** to classify intents of user messages from frontend UI.
2. **Authentication Flow**: If transferring funds between the user's accounts, the LLM will handle authentication using an ID and password with function calling. If authentication is successful, we will use function calling or MCP to call the function and transfer funds in database.
3. **Escalation Path**: If the intent classification is unknown, the chatbot will escalate to a real agent (for this POC, just a text to represent the user is being transferred to a human agent).
4. **FAQ Handling**: If it's identified as a FAQ, the LLM will provide answers using the RAG-based FAQ document (FAQ source from RBC website).

## Setup Instructions

### Prerequisites

- Python 3.8+
- Google Gemini API key

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/rbc-rag-chatbot.git
   cd rbc-rag-chatbot
   ```

2. Install dependencies:
   ```bash
   pip install google-generativeai python-dotenv langchain langchain-google-genai langchain-chroma chromadb pypdf sentence-transformers requests beautifulsoup4 cryptography
   ```

3. Create a `.env` file in the project root with your Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

### Document Collection

The chatbot requires RBC Bank documents to function. These are not included in the repository but can be collected using the included scraper:

1. Run the document scraper:
   ```bash
   python rbc_explorer.py
   ```

   This will:
   - Explore RBC's website
   - Download relevant PDF documents
   - Save them to the `rbc_documents` folder
   - Take approximately 5-10 minutes to complete

### Running the Chatbot

1. Start the chatbot:
   ```bash
   python app.py
   ```

   On first run, the system will:
   - Process the documents in `rbc_documents`
   - Create a vector database in `chroma_db`
   - This initial processing may take several minutes

2. Ask questions about RBC Bank products, services, and policies.

## Project Structure

- `app.py`: Main application entry point
- `document_loader.py`: Handles loading and processing PDF documents
- `vector_store.py`: Manages the vector database for document retrieval
- `rag_chatbot.py`: Core chatbot logic using RAG
- `rbc_explorer.py`: Web scraper for collecting RBC documents

## Troubleshooting

- **API Rate Limits**: If you encounter rate limit errors, consider:
  - Switching to a less resource-intensive model
  - Reducing the number of retrieved documents
  - Upgrading to a paid tier of the Gemini API

- **Document Processing Errors**: Some PDFs may fail to process. The system will skip these and continue with the rest.
