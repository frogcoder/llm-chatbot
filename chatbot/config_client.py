"""Configuration settings for the chatbot client."""

# Banking domains and intents
BANKING_DOMAINS = [
    "account", "balance", "transfer", "payment", "deposit", "withdraw", "credit", 
    "debit", "mortgage", "loan", "interest", "fee", "card", "statement", 
    "transaction", "banking", "rbc", "royal bank", "invest", "saving", "checking",
    "chequing", "tfsa", "rrsp", "resp", "insurance", "online banking", "mobile banking"
]

# Greeting patterns
GREETING_PATTERNS = [
    "hi", "hello", "hey", "greetings", "good morning", "good afternoon", 
    "good evening", "yo", "sup", "howdy", "hi there", "hello there"
]

# Farewell patterns
FAREWELL_PATTERNS = [
    "bye", "goodbye", "see you", "farewell", "exit", "quit", "q", "end"
]

# Command patterns
COMMANDS = {
    "exit": ["exit", "quit", "q", "bye", "goodbye"],
    "clear": ["clear", "clear history", "start over", "reset"],
    "user": ["user", "switch user", "change user"]
}

# Response templates
RESPONSE_TEMPLATES = {
    "greeting": [
        "Hello! How can I help with your RBC banking needs today?",
        "Hi there! How may I assist you with your RBC accounts or services today?",
        "Good day! I'm here to help with your RBC banking questions.",
        "Welcome! How can I assist you with your RBC banking today?"
    ],
    "farewell": [
        "Goodbye! Thank you for using RBC Banking Assistant.",
        "Thank you for using RBC Banking Assistant. Have a great day!",
        "It was a pleasure assisting you. Goodbye!",
        "Have a wonderful day! Goodbye!"
    ],
    "non_banking": [
        "I can only help with RBC banking-related questions.",
        "I'm specialized in RBC banking services. I can't help with that topic.",
        "That's outside my area of expertise. I can assist with RBC banking questions."
    ],
    "error": [
        "I'm sorry, I couldn't complete that action: {error}",
        "There was an error processing your request: {error}",
        "I encountered a problem: {error}"
    ],
    "transfer_success": [
        "✅ Transferred ${amount} from {from_account} to {to_account}.",
        "Your transfer of ${amount} from {from_account} to {to_account} was successful."
    ]
}

# System instructions template
SYSTEM_INSTRUCTIONS = """
You are an RBC Banking Assistant helping user {user_id}.

IMPORTANT INSTRUCTIONS:
1. ONLY USE ONE FUNCTION PER REQUEST. Choose the most appropriate function for each user request.

2. For account information and operations:
   - For checking balances: use get_account_balance with account_number="2345678901" for savings or "1234567890" for checking
   - For listing accounts: use list_user_accounts ONLY when explicitly asked to see accounts
   - For transfers: use transfer_funds with exact account numbers and amount as a string
   - For transaction history: use get_transaction_history with the exact account number

3. For general banking questions about RBC products and services, use answer_banking_question.

4. NEVER use multiple functions for a single request.

5. For transfers, map account names to numbers:
   - "Checking" or "Chequing" = "1234567890"
   - "Savings" or "Saving" = "2345678901"
   - "Credit Card" = "3456789012"

6. CRITICAL: For money transfers, ALWAYS use transfer_funds with:
   - from_account: the exact account number (not name)
   - to_account: the exact account number (not name)
   - amount: the amount as a string (e.g., "50.00")

7. NEVER call transfer_funds unless the user explicitly asks to transfer money.

8. For transaction history, use get_transaction_history with the exact account number.

9. NEVER call multiple functions for the same request.

10. MAINTAIN CONVERSATION CONTEXT: If the user's message is a short response to your previous question, interpret it in context.
    - If you asked "What account are you transferring from?" and they reply "savings", use that to complete the previous request.
    - If you can't determine what function to call, DO NOT call any function. Just respond conversationally.

11. For short, ambiguous messages, treat them as greetings and DO NOT call any functions.

12. IMPORTANT: When user asks about "savings account", ALWAYS use account number "2345678901".
    When user asks about "checking account", ALWAYS use account number "1234567890".
    When user asks about "credit card", ALWAYS use account number "3456789012".
"""

# Tool definitions
TOOL_DEFINITIONS = [
    {
        "name": "answer_banking_question",
        "description": "Answer a banking question using the RAG system with RBC documentation.",
        "parameters": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "The banking question to answer"
                }
            },
            "required": ["question"]
        }
    },
    {
        "name": "list_user_accounts",
        "description": "List all accounts for a given user.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "The ID of the user"
                }
            },
            "required": ["user_id"]
        }
    },
    {
        "name": "list_target_accounts",
        "description": "List all other accounts this user can transfer to.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "The ID of the user"
                },
                "from_account": {
                    "type": "string",
                    "description": "The source account number"
                }
            },
            "required": ["user_id", "from_account"]
        }
    },
    {
        "name": "transfer_funds",
        "description": "Transfer funds from one account to another.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "The ID of the user"
                },
                "from_account": {
                    "type": "string",
                    "description": "The source account number"
                },
                "to_account": {
                    "type": "string",
                    "description": "The destination account number"
                },
                "amount": {
                    "type": "string",
                    "description": "The amount to transfer"
                }
            },
            "required": ["user_id", "from_account", "to_account", "amount"]
        }
    },
    {
        "name": "get_account_balance",
        "description": "Get the balance of a specific account.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "The ID of the user"
                },
                "account_number": {
                    "type": "string",
                    "description": "The account number"
                }
            },
            "required": ["user_id", "account_number"]
        }
    },
    {
        "name": "get_transaction_history",
        "description": "Get the transaction history for a specific account.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "The ID of the user"
                },
                "account_number": {
                    "type": "string",
                    "description": "The account number"
                },
                "days": {
                    "type": "integer",
                    "description": "Number of days of history to retrieve (default: 30)"
                }
            },
            "required": ["user_id", "account_number"]
        }
    }
]

# Model configuration
MODEL_CONFIG = {
    "model_name": "gemini-1.5-pro",
    "temperature": 0.1,
    "tool_calling_config": {"mode": "AUTO"}
}
