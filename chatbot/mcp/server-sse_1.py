from dataclasses import asdict
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from decimal import Decimal
import os
import sys
from chatbot.models import Account
from chatbot.account import list_accounts
from chatbot.account import list_transfer_target_accounts
from chatbot.account import transfer_between_accounts
from chatbot.rag.rag_chatbot import RBCChatbot

# Load environment variables from .env file
load_dotenv("../.env")

# Initialize the RAG chatbot
chatbot = RBCChatbot()

# Create the MCP server
mcp = FastMCP(name="RBC-RAG-MCP", host="127.0.0.1", port=8050)

# RAG Tool: Answer questions using the RAG system
@mcp.tool()
def answer_banking_question(question: str) -> dict:
    """
    Answer a banking question using the RAG system with RBC documentation.
    Returns the answer and sources.
    """
    print(f"[RAG] Processing question: {question}")
    result = chatbot.answer_question(question)
    print(f"[RAG] Found answer with {len(result['sources'])} sources")
    return {
        "answer": result["answer"],
        "sources": result["sources"]
    }

# Tool 1: List all accounts belonging to a user
@mcp.tool()
def list_user_accounts(user_id: str) -> list[dict]:
    """List all accounts for a given user."""
    accounts = list_accounts(user_id)
    print(f"[DEBUG] list_user_accounts called with user_id={user_id}")
    print(f"[DEBUG] Accounts: {accounts}")
    return list(map(asdict, accounts))


# Tool 2: List target accounts that can receive transfers
@mcp.tool()
def list_target_accounts(user_id: str, from_account: str) -> list[dict]:
    """List all other accounts this user can transfer to."""
    accounts = list_transfer_target_accounts(user_id, from_account)
    print(f"[DEBUG] list_target_accounts called with user_id={user_id}, from_account={from_account}")
    print(f"[DEBUG] Transfer targets: {accounts}")
    return list(map(asdict, accounts))


# Tool 3: Transfer funds between two accounts
@mcp.tool()
def transfer_funds(user_id: str, from_account: str, to_account: str, amount: str) -> str:
    """Transfer funds from one account to another."""
    print(f"[DEBUG] transfer_funds called with user_id={user_id}, from_account={from_account}, to_account={to_account}, amount={amount}")
    transfer_between_accounts(user_id, from_account, to_account, Decimal(amount))
    return f"✅ Transferred {amount} from {from_account} to {to_account}."

# Tool 4: Get account balance
@mcp.tool()
def get_account_balance(user_id: str, account_number: str) -> str:
    """Get the balance of a specific account."""
    print(f'[DEBUG] get_account_balance called with user_id={user_id}, account_number={account_number}')
    balance_info = get_balance(user_id, account_number)
    return balance_info

# Tool 5: Get transaction history
@mcp.tool()
def get_transaction_history(user_id: str, account_number: str, days: int = 30) -> list[dict]:
    """Get the transaction history for a specific account."""
    print(f"[DEBUG] get_transaction_history called with user_id={user_id}, account_number={account_number}, days={days}")
    transactions = get_transactions(user_id, account_number, days)
    print(f"[DEBUG] Transactions: {len(transactions)} transactions found")
    return [transaction.__dict__ for transaction in transactions]



# ================================
# Simulated in-memory account system (mock database)
# ================================
from dataclasses import dataclass

@dataclass
class Balance:
    account_number: str
    account_name: str
    balance: Decimal
    currency: str = "CAD"

@dataclass
class Transaction:
    transaction_id: str
    date: str
    description: str
    amount: Decimal
    transaction_type: str  # "debit" or "credit"
    balance_after: Decimal

# Hardcoded in-memory database for demonstration purposes
_fake_db = {
    "user_abc123": [
        Account("Savings", "ABC123"),
        Account("Checking", "DEF456"),
    ]
}

_balance_db = {
    "user_abc123": {
        "ABC123": Balance("ABC123", "Savings", Decimal("5000.00")),
        "DEF456": Balance("DEF456", "Checking", Decimal("2500.75")),
    }
}

_transactions_db = {
    "user_abc123": {
        "ABC123": [
            Transaction("TXN001", "2025-05-20", "Direct Deposit - Salary", Decimal("3000.00"), "credit", Decimal("5000.00")),
            Transaction("TXN002", "2025-05-18", "Interest Payment", Decimal("15.50"), "credit", Decimal("2000.00")),
            Transaction("TXN003", "2025-05-15", "ATM Withdrawal", Decimal("-200.00"), "debit", Decimal("1984.50")),
        ],
        "DEF456": [
            Transaction("TXN004", "2025-05-21", "Grocery Store", Decimal("-85.25"), "debit", Decimal("2500.75")),
            Transaction("TXN005", "2025-05-20", "Transfer from Savings", Decimal("500.00"), "credit", Decimal("2586.00")),
            Transaction("TXN006", "2025-05-19", "Online Purchase", Decimal("-45.99"), "debit", Decimal("2086.00")),
            Transaction("TXN007", "2025-05-18", "Coffee Shop", Decimal("-12.50"), "debit", Decimal("2131.99")),
        ]
    }
}


# Get account balance
def get_balance(user_id: str, account_number: str) -> dict:
    print(f"[DEBUG] get_balance called with user_id={user_id}, account_number={account_number}")

    if user_id in _balance_db and account_number in _balance_db[user_id]:
        balance = _balance_db[user_id][account_number]
        return {
            "account_number": balance.account_number,
            "account_name": balance.account_name,
            "balance": str(balance.balance),
            "currency": balance.currency
        }
    else:
        return {"error": f"Account {account_number} not found."}
    
# Get transaction history
def get_transactions(user_id: str, account_number: str, days: int = 30) -> list[Transaction]:
    print(f"[DEBUG] get_transaction_history called with user_id={user_id}, account_number={account_number}, days={days}")

    if user_id in _transactions_db and account_number in _transactions_db[user_id]:
        transactions = _transactions_db[user_id][account_number]
        print(f"[DEBUG] Returning: {len(transactions)} transactions")
        return transactions
    else:
        print(f"[DEBUG] No transactions found for user_id={user_id}, account_number={account_number}")
        return []

# Run the MCP server using SSE transport
if __name__ == "__main__":
    print("[INFO] Starting MCP server on http://127.0.0.1:8050 using SSE transport...")
    mcp.run(transport="sse")
