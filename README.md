# An AI Chatbot Concept
A bank Chatbot concept utilizing LLM &amp; RAG with API integrations

1. Prompt engineering to classify  intents of user messages from frontend UI.
2. If transfering fund between the users account money, the LLM will go the authentication using an ID and password with function calling. If authentication is successful, we will use function calling or MCP to call the function and transfer fund in database.
3. If the intent classification is unknown, the chatbot will escalate to a real agent (for this POC, just a text to represent the user is being transferred to a human agent).
4. If it's identified as a FAQ, the LLM will provide answers using the RAG-based FAQ document (FAQ source from RBC website).
