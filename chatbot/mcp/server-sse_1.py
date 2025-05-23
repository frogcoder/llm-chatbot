from dataclasses import asdict
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from decimal import Decimal
import os
import sys

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from chatbot.account import list_accounts
from chatbot.account import list_transactions
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
def get_account_balance(user_id: str, account_number: str) -> dict:
    """Get the balance of a specific account."""
    print(f'[DEBUG] get_account_balance called with user_id={user_id}, account_number={account_number}')
    try:
        accounts = list_accounts(user_id)
        account = next((a for a in accounts if a.account_number == account_number), None)
        if account:
            return {
                "account_number": account.account_number,
                "account_name": account.account_name,
                "balance": str(account.balance),
                "currency": account.currency_code
            }
        return {"error": "Account not found"}
    except Exception as e:
        print(f"Error in get_account_balance: {str(e)}")
        return {"error": str(e)}


# Tool 5: Get transaction history
@mcp.tool()
def get_transaction_history(user_id: str, account_number: str, days: int = 30) -> list[dict]:
    """Get the transaction history for a specific account."""
    print(f"[DEBUG] get_transaction_history called with user_id={user_id}, account_number={account_number}, days={days}")
    try:
        transactions = list_transactions(user_id, account_number, days)
        print(f"[DEBUG] Transactions: {len(transactions)} transactions found")
        
        # Convert each transaction to a dictionary manually to avoid asdict() issues
        result = []
        for tx in transactions:
            tx_dict = {
                "transaction_number": tx.transaction_number,
                "account_number": tx.account_number,
                "date": tx.date_time.strftime("%Y-%m-%d"),
                "transaction_type": tx.transaction_type,
                "amount": str(tx.amount),
                "description": tx.description,
                "balance_after": str(tx.balance_after)
            }
            result.append(tx_dict)
        return result
    except Exception as e:
        print(f"Error in get_transaction_history: {str(e)}")
        return {"error": str(e)}


# Run the MCP server using SSE transport
if __name__ == "__main__":
    print("[INFO] Starting MCP server on http://127.0.0.1:8050 using SSE transport...")
    mcp.run(transport="sse")
