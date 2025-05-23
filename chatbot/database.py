import sqlite3
import uuid
from datetime import date
from datetime import datetime
from datetime import timedelta
from decimal import Decimal
from pathlib import Path
from chatbot.models import Account
from chatbot.models import Transaction


ACCOUNT_WITHDRAW_TO = "0000000001"
ACCOUNT_DEPOSIT_FROM = "0000000002"
THE_BANK_USER_ID = "thebank"


DB_FILE = "bank.db"


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
    sql = "SELECT AccountNumber, AccountName, Balance, CurrencyCode FROM Accounts WHERE UserId=:user_id"
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute(sql, { "user_id": user_id })
    accounts = [Account(account_number=a[0],
                        account_name=a[1],
                        balance=a[2],
                        currency_code=a[3]) for a in cur.fetchall()]
    con.close()
    return accounts


def load_transfer_target_accounts(user_id: str, from_account: str) -> list[Account]:
    """
    Query accounts that the specified account can trasfer fund to.

    :param user_id: The user ID of the account owner
    :param from_account: The account number or account name that the fund would be transferred from.
    :return: All the accounts that the specified account can transfer to.
    """
    sql_account_number = "SELECT AccountNumber FROM Accounts WHERE UserId=:user_id AND AccountName=:account_name"
    sql_accounts = "SELECT AccountNumber, AccountName, Balance, CurrencyCode FROM Accounts WHERE UserId=:user_id AND AccountNumber<>:account_number"
    
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute(sql_account_number, {
        "user_id": user_id,
        "account_name": from_account
    })
    from_account_query = cur.fetchone()
    from_account_number = (from_account_query[0] if from_account_query
                           else from_account)

    cur.execute(sql_accounts, { "user_id": user_id,
                                "account_number": from_account_number })
    
    accounts = [Account(account_number=a[0],
                        account_name=a[1],
                        balance=a[2],
                        currency_code=a[3]) for a in cur.fetchall()]
    con.close()
    return accounts


def transfer_fund(user_id: str, from_account: str, to_account: str,
                  amount: Decimal, description: str=""):
    """
    Deduct fund from one account then add to the other account all under the same owner
    
    :param user_id: The user ID of the account owner
    :param from_account: The account number or account name that the fund would be transferred from.
    :param to_account: The account number or account name that the fund would be transferred to.
    :param amount: The amount that is going to be transfered.
    :param description: Optional description of the nature of the transaction.
    """
    sql_account_number = "SELECT AccountNumber FROM Accounts WHERE UserId=:user_id AND AccountName=:account_name"
    sql_balance_update = "UPDATE Account WHERE AccountNumber=:account_number AND LastTransactionNumber=:transactionNumber"
    sql_transaction = """
        INSERT INTO Transactions (TransactionNumber, AccountNumber, OtherAccountNumber, TransactionDateTime, Amount, BalanceAfter, TransactionTypeCode) 
        VALUES (:transaction_number, :account_number, :other_account_number, :date_time, :amount, :balance_after, :transaction_type_code)
    """
    sql_balance = "UPDATE Accounts SET Balance=balance + :amount WHERE AccountNumber=:accountNumber RETURNING Balance"

    transaction_number = uuid.uuid4().int
    date_time = datetime.now()
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()

    cur.execute(sql_account_number, { "user_id": user_id, "account_name": from_account })
    from_account_query = cur.fetchone()
    from_account_number = from_account_query[0] if from_account_query else from_account
    
    cur.execute(sql_account_number, { "user_id": user_id, "account_name": to_account })
    to_account_query = cur.fetchone()
    to_account_number = to_account_query[0] if to_account_query else to_account

    cur.execute(sql_balance_update, {
        "account_number": from_account_number,
        "amount": -amount
    })
    from_account_balance = cur.fetchone()[0]

    cur.execute(sql_balance_update, {
        "account_number": to_account_number,
        "amount": amount
    })
    to_account_balance = cur.fetchone()[0]
    
    cur.executemany(sql_transaction, [
        { "transaction_number": transaction_number,
          "account_number": from_account_number,
          "other_account_number": to_account_number,
          "date_time": date_time,
          "amount": amount,
          "balance_after": from_account_balance,
          "transaction_type_code": "D" },
        { "transaction_number": transaction_number,
          "account_number": to_account_number,
          "other_account_number": from_account_number,
          "date_time": date_time,
          "amount": amount,
          "balance_after": to_account_balance,
          "transaction_type_code": "C" }
    ])
    con.commit()
    con.close()


def load_transactions(user_id: str, account: str, from_date: date, to_date: date):
    sql_account_number = "SELECT AccountNumber FROM Accounts WHERE UserId=:user_id AND AccountName=:account_name"
    sql_transactions = ("SELECT TransactionNumber, AccountNumber, TransactionDateTime, TransactionTypeCode, Amount, BalanceAfter, OtherAccountNumber, Description"
                        "WHERE AccountNumber=:account_number AND TransactionDateTime>=:from_time AND TransactionDateTime<:before_time")
    before_date = to_date + timedelta(days=1)
    from_time = datetime.combine(from_date, datetime.min.time()).isoformat()
    before_time = datetime.combine(before_date, datetime.min.time()).isoformat()
    
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute(sql_account_number, { "user_id": user_id, "account_name": account })
    account_query = cur.fetchone()
    account_number = account_query[0] if account_query else account

    cur.execute(sql_transactions, {
        "account_number": account_number,
        "from_time": from_time,
        "before_time": before_time
    })

    describe = lambda o: ("Withdraw" if o == ACCOUNT_WITHDRAW_TO
                          else "Deposit" if o == ACCOUNT_DEPOSIT_FROM
                          else "Transfer")
    
    transactions = [Transaction(
        transaction_number=t[0],
        account_number=t[1],
        date_time=t[2],
        transaction_type="Credit" if t[3] == "C" else "Debit",
        amount=t[4],
        balance_after=t[5],
        description = describe(t[6]) + (" " + t[7]) if t[7] else ""
    ) for t in cur.fetchall()]
    con.close()
    return transactions


def init_db():
    """
    Create the database and add inital test data.
    """

    sql_path = Path(__file__).parent / "init.sql"
    with open(sql_path) as sql_file:
        sql = sql_file.read()
        con = sqlite3.connect(DB_FILE)
        cur = con.cursor()
        cur.executescript(sql)
        con.commit()
        con.close()


if not Path(DB_FILE).exists():
    init_db()
