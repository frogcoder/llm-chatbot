import sqlite3
import uuid
from datetime import date
from datetime import datetime
from datetime import timedelta
from decimal import Decimal
from pathlib import Path
from chatbot.models import Account
from chatbot.config import DB_FILE, DB_INIT_SQL


def auth_user(user_id: str, password: str) -> bool:
    """
    Ensure the user id and password are match to pair stored in database.  This is a just a part of a simple demo, you should never store clear text passwords in production.

    :param user_id: The user ID that needing authentcation.
    :param password: The matching password to the user ID.
    :return: True if user ID and password are matched, False otherwise.
    """
    sql = "SELECT UserId FROM UserCredentials WHERE UserId=:user_id AND Password=:password"
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute(sql, {"user_id": user_id, "password": password})
    authenticated = cur.fetchone() is not None
    con.close()
    return authenticated


def load_accounts(user_id: str) -> list[Account]:
    """
    Query accounts that belong to the speicfied user.

    :param user_id: The user ID of the account owner
    :return: All the accounts that belong the the user
    """
    sql = "SELECT AccountNumber, AccountName, Balance FROM Accounts WHERE UserId=:user_id"
    con = sqlite3.connect(DB_FILE)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute(sql, {"user_id": user_id})
    rows = cur.fetchall()
    accounts = []
    for row in rows:
        account = Account()
        account.account_number = row['AccountNumber']
        account.account_name = row['AccountName']
        account.balance = Decimal(str(row['Balance']))
        accounts.append(account)
    con.close()
    return accounts


def load_transfer_target_accounts(user_id: str, from_account: str) -> list[Account]:
    """
    Query accounts that the specified account can trasfer fund to.

    :param user_id: The user ID of the account owner
    :param from_account: The account number or account name that the fund would be transferred from.
    :return: All the accounts that the specified account can transfer to.
    """
    sql = """
    SELECT AccountNumber, AccountName, Balance 
    FROM Accounts 
    WHERE UserId=:user_id AND AccountNumber!=:from_account
    """
    con = sqlite3.connect(DB_FILE)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute(sql, {"user_id": user_id, "from_account": from_account})
    rows = cur.fetchall()
    accounts = []
    for row in rows:
        account = Account()
        account.account_number = row['AccountNumber']
        account.account_name = row['AccountName']
        account.balance = Decimal(str(row['Balance']))
        accounts.append(account)
    con.close()
    return accounts


def transfer_fund_between_accounts(user_id: str,
                                   from_account: str, to_account: str,
                                   amount: Decimal):
    """
    Deduct fund from one account then add to the other account all under the same owner
    
    :param user_id: The user ID of the account owner
    :param from_account: The account number or account name that the fund would be transferred from.
    :param to_account: The account number or account name that the fund would be transferred to.
    :param amount: The amount that is going to be transfered.
    """
    # Debug the parameters
    print(f"[DEBUG] transfer_fund_between_accounts: user_id={user_id}, from={from_account}, to={to_account}, amount={amount} (type: {type(amount)})")
    
    # Ensure amount is a Decimal
    if not isinstance(amount, Decimal):
        amount = Decimal(str(amount))
    
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    
    try:
        # Start a transaction
        con.execute("BEGIN TRANSACTION")
        
        # Convert amount to string for SQLite
        amount_str = str(amount)
        
        # Deduct from source account
        cur.execute(
            "UPDATE Accounts SET Balance = Balance - ? WHERE UserId=? AND AccountNumber=?",
            (amount_str, user_id, from_account)
        )
        
        # Add to destination account
        cur.execute(
            "UPDATE Accounts SET Balance = Balance + ? WHERE UserId=? AND AccountNumber=?",
            (amount_str, user_id, to_account)
        )
        
        # Get the updated balances after the transfer
        cur.execute("SELECT Balance FROM Accounts WHERE UserId=? AND AccountNumber=?", 
                   (user_id, from_account))
        from_account_balance = cur.fetchone()[0]
        
        cur.execute("SELECT Balance FROM Accounts WHERE UserId=? AND AccountNumber=?", 
                   (user_id, to_account))
        to_account_balance = cur.fetchone()[0]
        
        # Record the transfer with balances
        import uuid
        import datetime
        transaction_id = str(uuid.uuid4())
        current_time = datetime.datetime.now().isoformat()
        
        cur.execute(
            """
            INSERT INTO Transfers (
                TransactionNumber, FromAccountNumber, ToAccountNumber, 
                TransferDateTime, Amount, FromAccountBalance, ToAccountBalance
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (transaction_id, from_account, to_account, current_time, 
             amount_str, from_account_balance, to_account_balance)
        )
        
        # Commit the transaction
        con.commit()
        print(f"[DEBUG] Transfer successful: {amount_str} from {from_account} to {to_account}")
    except Exception as e:
        # Rollback in case of error
        con.rollback()
        print(f"[ERROR] Database error during transfer: {str(e)}")
        raise e
    finally:
        con.close()


def init_db():
    """
    Create the database and add inital test data.
    """
    # Check if database file already exists and has tables
    db_exists = Path(DB_FILE).exists()
    
    if db_exists:
        # Check if tables already exist
        con = sqlite3.connect(DB_FILE)
        cur = con.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='UserCredentials'")
        table_exists = cur.fetchone() is not None
        con.close()
        
        if table_exists:
            print(f"Database {DB_FILE} already initialized.")
            return
    
    # Create and initialize the database
    with open(DB_INIT_SQL) as sql_file:
        sql = sql_file.read()
        con = sqlite3.connect(DB_FILE)
        cur = con.cursor()
        cur.executescript(sql)
        con.commit()
        con.close()
        print(f"Database {DB_FILE} initialized successfully.")
