# RBC AI Banking Agent

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

4. **Modern User Interface**
   - Responsive web interface with chat functionality
   - Draggable and resizable chat window
   - Secure authentication flow
   - Real-time typing indicators

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

4. **Web Interface**
   - Flask-based web server
   - Modern responsive UI with CSS animations
   - JWT-based authentication
   - Asynchronous message handling

### Setup Instructions

1. **Prerequisites**
   - Python 3.8+
   - Google Gemini API key

2. **Installation**
   ```bash
   # Clone the repository
   git clone https://github.com/yourusername/rbc-banking-agent.git
   cd rbc-banking-agent

   # Install dependencies
   pip install -r requirements.txt

   # Create .env file with your API key
   echo "GEMINI_API_KEY=your_api_key_here" > .env
   ```

3. **Document Collection (First-time setup)**
   ```bash
   # Run the document scraper to collect RBC documentation
   python -m chatbot.rag.rbc_explorer
   
   # Collect investment FAQs
   python -m chatbot.rag.save_investment_faqs
   ```

4. **Running the Agent**
   ```bash
   # Start the MCP server in one terminal
   python -m chatbot.mcp.server-sse_1

   # In another terminal, start the web application
   python app.py
   ```

5. **Accessing the Web Interface**
   - Open your browser and navigate to http://localhost:3000
   - Click on the chat icon in the bottom right corner
   - Log in with your credentials (default: test1/password)
   - Start chatting with the RBC AI Banking Agent

## Project Structure

```
├── app.py              # Flask web application
├── templates/          # HTML templates
│   └── chat.html       # Main chat interface
├── static/             # Static assets
│   ├── script.js       # Client-side JavaScript
│   └── style.css       # CSS styling
├── chatbot/
│   ├── __init__.py
│   ├── account.py      # Account management functionality
│   ├── config.py       # Core configuration settings
│   ├── database.py     # Database operations
│   ├── intent_detector.py # User intent detection
│   ├── models.py       # Data models
│   ├── response_formatter.py # Response formatting
│   ├── mcp/
│   │   ├── client_sse.py  # Interactive client
│   │   └── server_sse.py  # MCP server with RAG
│   └── rag/
│       ├── document_loader.py # Document processing
│       ├── rag_chatbot.py # RAG implementation
│       ├── rbc_explorer.py # Document collection
│       ├── save_investment_faqs.py # FAQ scraper
│       └── vector_store.py # Vector database management
```

## Usage Examples

### Banking Operations
- Check account balances: "What's my savings account balance?"
- Transfer funds: "Transfer $50 from my savings to checking account"
- View transactions: "Show me recent transactions in my checking account"
- List accounts: "Show me all my accounts"

### Banking Information
- Product inquiries: "Tell me about the cash back program."
- Service questions: "How do I set up direct deposit?"
- Policy questions: "What is RBC's mortgage pre-approval process?"
- Investment guidance: "How can I withdraw money from my TFSA account?"

## Technologies Used

- **Google Gemini**: Large language model for natural language understanding
- **LangChain**: Framework for building LLM applications
- **ChromaDB**: Vector database for document embeddings
- **SQLite**: Lightweight database for banking operations
- **Flask**: Web application framework
- **JWT**: JSON Web Tokens for authentication
- **HTML/CSS/JavaScript**: Frontend web technologies
