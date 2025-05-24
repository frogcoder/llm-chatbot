# RBC Banking Agent

An intelligent banking assistant that combines LLM capabilities with RAG (Retrieval Augmented Generation) to provide accurate information about RBC banking products and services while enabling account management functionality.

## Key Features

1. **Intelligent Banking Operations**
   - Account balance inquiries
   - Fund transfers between accounts
   - Transaction history retrieval
   - Account listing and management

2. **Knowledge-Based Assistance**
   - RAG-powered responses using official RBC documentation
   - Accurate information about banking products and services
   - Investment and financial planning guidance

3. **Advanced AI Techniques**
   - **Retrieval Augmented Generation (RAG)**: Combines LLM capabilities with a knowledge base of RBC documents
   - **Prompt Engineering**: Carefully crafted system instructions to guide the model's behavior
   - **Intent Detection**: Identifies user intents to route queries appropriately
   - **Function Calling**: Uses LLM to determine which banking operations to perform

4. **Modular Architecture**
   - MCP (Modular Capability Platform) for extensible function calling
   - Vector database for efficient document retrieval
   - Configurable response templates and system instructions

## Technical Architecture

### Components

1. **RAG System**
   - Document loader and processor for RBC banking documents
   - Vector store using Chroma DB for semantic search
   - Embedding generation using Google's embedding models
   - RAG pipeline for answering banking questions with citations

2. **Banking Operations**
   - SQLite database for account and transaction management
   - Secure fund transfer functionality
   - Transaction history tracking
   - Account balance management

3. **Conversation Management**
   - Intent detection for understanding user queries
   - Response formatting for consistent user experience
   - Conversation history tracking for contextual responses
   - Command handling for system operations

4. **MCP Integration**
   - Server-side function registration
   - Client-side function calling
   - Tool definitions for LLM function selection

### Setup Instructions

1. **Prerequisites**
   - Python 3.8+
   - Google Gemini API key

2. **Installation**
   ```bash
   # Clone the repository
   git clone https://github.com/yourusername/rbc-banking-assistant.git
   cd rbc-banking-assistant

   # Install dependencies
   pip install -r requirements.txt

   # Create .env file with your API key
   echo "GEMINI_API_KEY=your_api_key_here" > .env
   ```

3. **Document Collection**
   ```bash
   # Run the document scraper to collect RBC documentation
   python -m chatbot.rag.rbc_explorer
   ```

4. **Running the Agent**
   ```bash
   # Start the MCP server
   python -m chatbot.mcp.server-sse_1

   # In another terminal, start the client
   python -m chatbot.mcp.client-sse
   ```

## Project Structure

```
chatbot/
├── __init__.py
├── account.py         # Account management functionality
├── config.py          # Core configuration settings
├── config_client.py   # Client-specific configuration
├── database.py        # Database operations
├── init.sql           # Database initialization
├── intent_detector.py # User intent detection
├── models.py          # Data models
├── response_formatter.py # Response formatting
├── mcp/
│   ├── client-sse.py  # Interactive client
│   ├── server-sse.py  # Basic MCP server
│   └── server-sse_1.py # Enhanced MCP server with RAG
└── rag/
    ├── app.py         # Standalone RAG application
    ├── document_loader.py # Document processing
    ├── rag_chatbot.py # RAG implementation
    ├── rbc_explorer.py # Document collection
    ├── save_investment_faqs.py # FAQ scraper
    └── vector_store.py # Vector database management
```

## Usage Examples

### Banking Operations
- Check account balances: "What's my savings account balance?"
- Transfer funds: "Transfer $50 from my savings to checking account"
- View transactions: "Show me recent transactions in my checking account"
- List accounts: "Show me all my accounts"

### Banking Information
- Product inquiries: "What are the benefits of an RBC TFSA?"
- Service questions: "How do I set up direct deposit?"
- Policy questions: "What is RBC's mortgage pre-approval process?"
- Investment guidance: "How can I withdraw money from my TFSA account?"

## Technologies Used

- **Google Gemini**: Large language model for natural language understanding
- **LangChain**: Framework for building LLM applications
- **ChromaDB**: Vector database for document embeddings
- **SQLite**: Lightweight database for banking operations
- **MCP**: Moddel Context Protocol for function calling
