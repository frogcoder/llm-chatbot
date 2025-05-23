from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from decimal import Decimal
<<<<<<< HEAD
import os
import sys

# Add the parent directory to the Python path to import from chatbot
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(parent_dir)

# Import the actual database functions
from chatbot.account import list_accounts, list_transfer_target_accounts, transfer_between_accounts
from chatbot.database import init_db

# Load environment variables from .env file
load_dotenv("../../.env")

# Initialize the database if it doesn't exist (will check internally)
init_db()
=======

# Load environment variables from .env file
load_dotenv("../.env")
>>>>>>> main

# Create the MCP server
mcp = FastMCP(name="BankMCP", host="127.0.0.1", port=8050)

# Tool 1: List all accounts belonging to a user
@mcp.tool()
def list_user_accounts(user_id: str) -> list[dict]:
    """List all accounts for a given user."""
    accounts = list_accounts(user_id)
    print(f"[DEBUG] list_user_accounts called with user_id={user_id}")
    print(f"[DEBUG] Accounts: {accounts}")
    return [account.__dict__ for account in accounts]

# Tool 2: List target accounts that can receive transfers
@mcp.tool()
def list_target_accounts(user_id: str, from_account: str) -> list[dict]:
    """List all other accounts this user can transfer to."""
    accounts = list_transfer_target_accounts(user_id, from_account)
    print(f"[DEBUG] list_target_accounts called with user_id={user_id}, from_account={from_account}")
    print(f"[DEBUG] Transfer targets: {accounts}")
    return [account.__dict__ for account in accounts]

# Tool 3: Transfer funds between two accounts
@mcp.tool()
def transfer_funds(user_id: str, from_account: str, to_account: str, amount: str) -> str:
    """Transfer funds from one account to another."""
    print(f"[DEBUG] transfer_funds called with user_id={user_id}, from_account={from_account}, to_account={to_account}, amount={amount}")
    transfer_between_accounts(user_id, from_account, to_account, Decimal(amount))
    return f"✅ Transferred {amount} from {from_account} to {to_account}."

<<<<<<< HEAD
=======
# ================================
# Simulated in-memory account system (mock database)
# ================================
from dataclasses import dataclass

# A simple data structure representing a bank account
@dataclass
class Account:
    account_name: str
    account_number: str

# Hardcoded in-memory database for demonstration purposes
_fake_db = {
    "user_abc123": [
        Account("Savings", "ABC123"),
        Account("Checking", "DEF456"),
    ]
}

# Get all accounts for a specific user
def list_accounts(user_id: str) -> list[Account]:
    print(f"[DEBUG] list_accounts called with user_id={user_id}")
    return _fake_db.get(user_id, [])

# Get transfer targets (all accounts except the source account)
def list_transfer_target_accounts(user_id: str, from_account: str) -> list[Account]:
    print(f"[DEBUG] list_transfer_target_accounts called with user_id={user_id}, from_account={from_account}")
    return [acc for acc in list_accounts(user_id) if acc.account_number != from_account]

# Simulate transferring money between two accounts
def transfer_between_accounts(user_id: str, from_account: str, to_account: str, amount):
    print(f"[DEBUG] list_accounts(user_id): {list_accounts(user_id)}")
    print(f"[TRANSFER] Transferring {amount} from {from_account} to {to_account} for user {user_id}")

>>>>>>> main
# Run the MCP server using SSE transport
if __name__ == "__main__":
    print("[INFO] Starting MCP server on http://127.0.0.1:8050 using SSE transport...")
    mcp.run(transport="sse")
