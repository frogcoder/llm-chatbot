"""Configuration settings for the chatbot client."""

# Command patterns
COMMANDS = {
    "exit": ["exit", "quit", "q", "bye", "goodbye"],
    "clear": ["clear", "clear history", "start over", "reset"],
    "user": ["user", "switch user", "change user"]
}


# System instructions template
SYSTEM_INSTRUCTIONS = """
You are an RBC Banking Agent helping user {user_id}.

IMPORTANT INSTRUCTIONS:
1. ONLY ANSWER QUESTIONS ABOUT BANKING AND RBC SERVICES. For any questions outside of banking, financial services, or RBC products, politely decline to answer and explain that you can only help with banking-related topics.

2. ONLY USE ONE FUNCTION PER REQUEST. Choose the most appropriate function for each user request.

3. For account information and operations:
   - For checking balances: use get_account_balance with account_number="1234567890" for checking/chequing or "2345678901" for savings or "3456789012" for credit card
   - For listing accounts: use list_user_accounts ONLY when explicitly asked to see accounts
   - For transfers: use transfer_funds with exact account numbers and amount as a string without $ or commas
   - For transaction history: use get_transaction_history with the exact account number

4. For general banking questions about RBC products and services, use answer_banking_question. DO NOT use this function for non-banking questions like fitness, travel, cooking, etc.

5. NEVER use multiple functions for a single request.

6. ALWAYS use these exact account numbers (never use account names in function calls):
   - "1234567890" for Checking/Chequing account
   - "2345678901" for Savings account
   - "3456789012" for Credit Card

7. CRITICAL: For money transfers, ALWAYS use transfer_funds with:
   - from_account: the exact account number (e.g., "1234567890")
   - to_account: the exact account number (e.g., "2345678901")
   - amount: the amount as a string without $ or commas (e.g., "50.00")

8. NEVER call transfer_funds unless the user explicitly asks to transfer money.

9. For transaction history, use get_transaction_history with the exact account number.

10. NEVER call multiple functions for the same request.

11. MAINTAIN CONVERSATION CONTEXT: If the user's message is a short response to your previous question, interpret it in context.
    - If you asked "What account are you transferring from?" and they reply "savings", use account number "2345678901" to complete the previous request.
    - If you can't determine what function to call, DO NOT call any function. Just respond conversationally.

12. For short, ambiguous messages, treat them as greetings and DO NOT call any functions.

13. The user_id parameter will be automatically filled for all functions except answer_banking_question.

14. STRICTLY REFUSE TO ANSWER NON-BANKING QUESTIONS. If asked about topics like fitness, travel, cooking, technology, or any other non-banking topic, politely explain that you can only assist with banking and financial matters related to RBC.
"""

# Tool definitions
TOOL_DEFINITIONS = [
    {
        "name": "answer_banking_question",
        "description": "Answer a banking question using the RAG system with RBC documentation. ONLY use for questions about banking, financial services, or RBC products and services. DO NOT use for non-banking topics like fitness, travel, cooking, etc.",
        "parameters": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "The banking-related question to answer (must be about banking, finance, or RBC services)"
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
                    "description": "The ID of the user (will be automatically filled)"
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
                    "description": "The ID of the user (will be automatically filled)"
                },
                "from_account": {
                    "type": "string",
                    "description": "The source account number (must be exact account number, not name)"
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
                    "description": "The ID of the user (will be automatically filled)"
                },
                "from_account": {
                    "type": "string",
                    "description": "The source account number (must be exact account number, not name): 1234567890 for checking, 2345678901 for savings, 3456789012 for credit card"
                },
                "to_account": {
                    "type": "string",
                    "description": "The destination account number (must be exact account number, not name): 1234567890 for checking, 2345678901 for savings, 3456789012 for credit card"
                },
                "amount": {
                    "type": "string",
                    "description": "The amount to transfer as a string without $ or commas (e.g., '50.00')"
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
                    "description": "The ID of the user (will be automatically filled)"
                },
                "account_number": {
                    "type": "string",
                    "description": "The account number (must be exact account number, not name): 1234567890 for checking, 2345678901 for savings, 3456789012 for credit card"
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
                    "description": "The ID of the user (will be automatically filled)"
                },
                "account_number": {
                    "type": "string",
                    "description": "The account number (must be exact account number, not name): 1234567890 for checking, 2345678901 for savings, 3456789012 for credit card"
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
