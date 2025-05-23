from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from decimal import Decimal
import os
import sys
import datetime

# Add the parent directory to the Python path to import from src and chatbot
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import RAG components
from src.rag_chatbot import RBCChatbot

# Import the actual database functions
from chatbot.account import list_accounts, list_transfer_target_accounts, transfer_between_accounts
from chatbot.database import init_db
from chatbot.models import Account

# Load environment variables from .env file
load_dotenv("../.env")

# Initialize the database if it doesn't exist (will check internally)
init_db()

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
    try:
        # Convert amount to Decimal, handling any formatting issues
        clean_amount = amount.replace('$', '').replace(',', '')
        decimal_amount = Decimal(clean_amount)
        
        # Debug the parameters
        print(f"[DEBUG] Parsed amount: {decimal_amount} (type: {type(decimal_amount)})")
        print(f"[DEBUG] from_account: {from_account} (type: {type(from_account)})")
        print(f"[DEBUG] to_account: {to_account} (type: {type(to_account)})")
        
        # Call the transfer function
        transfer_between_accounts(user_id, from_account, to_account, decimal_amount)
        return f"✅ Transferred ${clean_amount} from {from_account} to {to_account}."
    except Exception as e:
        print(f"[ERROR] Transfer failed: {str(e)}")
        return f"❌ Transfer failed: {str(e)}"

# Tool 4: Get account balance
@mcp.tool()
def get_account_balance(user_id: str, account_number: str) -> dict:
    """Get the balance of a specific account."""
    print(f'[DEBUG] get_account_balance called with user_id={user_id}, account_number={account_number}')
    
    # Find the account in the user's accounts
    accounts = list_accounts(user_id)
    for account in accounts:
        if account.account_number == account_number:
            return {
                "account_number": account.account_number,
                "account_name": account.account_name,
                "balance": str(account.balance),
                "currency": "CAD"
            }
    
    return {"error": f"Account {account_number} not found."}

# Tool 5: Get transaction history
@mcp.tool()
def get_transaction_history(user_id: str, account_number: str, days: int = 30) -> list[dict]:
    """Get the transaction history for a specific account."""
    print(f"[DEBUG] get_transaction_history called with user_id={user_id}, account_number={account_number}, days={days}")
    
    # Connect to the database to get transaction history
    import sqlite3
    from chatbot.database import DB_FILE
    
    con = sqlite3.connect(DB_FILE)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    
    # Calculate the date range
    today = datetime.datetime.now()
    start_date = (today - datetime.timedelta(days=days)).isoformat()
    
    # Query for transactions
    cur.execute("""
        SELECT TransactionNumber, TransferDateTime, 
               CASE 
                   WHEN FromAccountNumber = :account_number THEN 'debit' 
                   ELSE 'credit' 
               END as transaction_type,
               CASE 
                   WHEN FromAccountNumber = :account_number THEN -Amount 
                   ELSE Amount 
               END as amount,
               CASE 
                   WHEN FromAccountNumber = :account_number THEN 'Transfer to ' || ToAccountNumber
                   ELSE 'Transfer from ' || FromAccountNumber
               END as description
        FROM Transfers
        WHERE (FromAccountNumber = :account_number OR ToAccountNumber = :account_number)
        AND TransferDateTime >= :start_date
        ORDER BY TransferDateTime DESC
    """, {"account_number": account_number, "start_date": start_date})
    
    rows = cur.fetchall()
    
    # Get the current balance
    accounts = list_accounts(user_id)
    current_balance = None
    for account in accounts:
        if account.account_number == account_number:
            current_balance = account.balance
            break
    
    # Create transaction objects
    transactions = []
    running_balance = current_balance if current_balance is not None else Decimal("0")
    
    for row in rows:
        amount = Decimal(str(row['amount']))
        
        # For display purposes, adjust the running balance
        if row['transaction_type'] == 'debit':
            # For past transactions, we add the amount back since we're going backwards in time
            running_balance = running_balance - amount
        else:
            running_balance = running_balance + amount
        
        transaction = {
            "transaction_id": row['TransactionNumber'],
            "date": row['TransferDateTime'].split('T')[0],  # Just the date part
            "description": row['description'],
            "amount": str(amount),
            "transaction_type": row['transaction_type'],
            "balance_after": str(running_balance)
        }
        transactions.append(transaction)
    
    con.close()
    print(f"[DEBUG] Returning: {len(transactions)} transactions")
    return transactions

# Run the MCP server using SSE transport
if __name__ == "__main__":
    print("[INFO] Starting MCP server on http://127.0.0.1:8050 using SSE transport...")
    mcp.run(transport="sse")
