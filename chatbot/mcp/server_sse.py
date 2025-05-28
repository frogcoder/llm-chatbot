from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from decimal import Decimal
import os
import sys
import datetime

# Add the parent directory to the Python path to import from src and chatbot
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(parent_dir)
print(f"Added to Python path: {parent_dir}")

# Import RAG components
from chatbot.rag.rag_chatbot import RBCChatbot

# Import the actual database functions
from chatbot.account import list_accounts, list_transfer_target_accounts, transfer_between_accounts
from chatbot.database import init_db
from chatbot.models import Account

# Load environment variables from .env file
load_dotenv("../../.env")

# Initialize the database if it doesn't exist (will check internally)
init_db()

# Initialize the RAG chatbot
chatbot = RBCChatbot()

# Import configuration
from chatbot.config import MCP_NAME, MCP_HOST, MCP_PORT, DEFAULT_USER_ID

# Create the MCP server
mcp = FastMCP(name=MCP_NAME, host=MCP_HOST, port=MCP_PORT)

# RAG Tool: Answer questions using the RAG system
@mcp.tool()
def answer_banking_question(question: str) -> dict:
    """
    Answer a banking question using the RAG system with RBC documentation.
    Only for banking, financial services, or RBC-related questions.
    Returns the answer and sources.
    """
    print(f"[RAG] Processing question: {question}")
    
    # Process the question - the model should determine if it's banking-related
    # based on the system instructions
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
    
    # Query for transactions with balances
    cur.execute("""
        SELECT 
            TransactionNumber, 
            TransferDateTime, 
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
            END as description,
            CASE 
                WHEN FromAccountNumber = :account_number THEN FromAccountBalance
                ELSE ToAccountBalance
            END as balance_after
        FROM Transfers
        WHERE (FromAccountNumber = :account_number OR ToAccountNumber = :account_number)
        AND TransferDateTime >= :start_date
        ORDER BY TransferDateTime DESC
    """, {"account_number": account_number, "start_date": start_date})
    
    rows = cur.fetchall()
    
    # Create transaction objects using stored balances
    transactions = []
    
    for row in rows:
        amount = Decimal(str(row['amount']))
        
        transaction = {
            "transaction_id": row['TransactionNumber'],
            "date": row['TransferDateTime'].split('T')[0],  # Just the date part
            "description": row['description'],
            "amount": str(amount),
            "transaction_type": row['transaction_type'],
            "balance_after": str(row['balance_after'])
        }
        transactions.append(transaction)
    
    con.close()
    print(f"[DEBUG] Returning: {len(transactions)} transactions")
    return transactions

# Run the MCP server using SSE transport
if __name__ == "__main__":
    print("[INFO] Starting MCP server on http://127.0.0.1:8050 using SSE transport...")
    mcp.run(transport="sse")
