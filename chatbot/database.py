
import sqlite3
import uuid
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

from models import Account, Transaction

ACCOUNT_WITHDRAW_TO    = "0000000001"
ACCOUNT_DEPOSIT_FROM   = "0000000002"
THE_BANK_USER_ID       = "thebank"

DB_FILE = Path(__file__).parent / "bank.db"


def auth_user(user_id: str, password: str) -> bool:
    """
    Return True if credentials match a record in UserCredentials.
    """
    sql = """
    SELECT UserId
      FROM UserCredentials
     WHERE UserId = :user_id
       AND Password = :password
    """
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute(sql, {"user_id": user_id, "password": password})
    authenticated = cur.fetchone() is not None
    con.close()
    return authenticated


def load_accounts(user_id: str) -> list[Account]:
    """
    Return all Account objects for the given user_id.
    """
    sql = """
    SELECT AccountNumber, AccountName, Balance, CurrencyCode
      FROM Accounts
     WHERE UserId = :user_id
    """
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute(sql, {"user_id": user_id})
    rows = cur.fetchall()
    con.close()

    return [
        Account(
            account_number=row[0],
            account_name=row[1],
            balance=row[2],
            currency_code=row[3]
        )
        for row in rows
    ]


def load_transfer_target_accounts(user_id: str, from_account: str) -> list[Account]:
    """
    Return all accounts for this user except the `from_account`.
    """
    sql_num = """
    SELECT AccountNumber
      FROM Accounts
     WHERE UserId = :user_id
       AND AccountName = :account_name
    """
    sql_all = """
    SELECT AccountNumber, AccountName, Balance, CurrencyCode
      FROM Accounts
     WHERE UserId = :user_id
       AND AccountNumber <> :account_number
    """

    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()

    cur.execute(sql_num, {"user_id": user_id, "account_name": from_account})
    found = cur.fetchone()
    acct_num = found[0] if found else from_account

    cur.execute(sql_all, {"user_id": user_id, "account_number": acct_num})
    rows = cur.fetchall()
    con.close()

    return [
        Account(
            account_number=r[0],
            account_name=r[1],
            balance=r[2],
            currency_code=r[3]
        )
        for r in rows
    ]


def transfer_fund(user_id: str,
                  from_account: str,
                  to_account: str,
                  amount: Decimal,
                  description: str = ""):
    """
    Move `amount` from one account to another under the same user.
    Records two transaction rows (debit + credit).
    """
    # Resolve account numbers
    sql_num = "SELECT AccountNumber FROM Accounts WHERE UserId=:user_id AND AccountName=:account_name"
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()

    def resolve(name_or_num):
        cur.execute(sql_num, {"user_id": user_id, "account_name": name_or_num})
        r = cur.fetchone()
        return r[0] if r else name_or_num

    from_num = resolve(from_account)
    to_num   = resolve(to_account)

    # Update balances
    sql_update = "UPDATE Accounts SET Balance = Balance + :delta WHERE AccountNumber = :acct"
    cur.execute(sql_update, {"delta": -amount, "acct": from_num})
    cur.execute(sql_update, {"delta":  amount, "acct": to_num})

    # Record transactions
    txn_no = uuid.uuid4().int
    now    = datetime.now().isoformat()
    entries = [
        (txn_no, from_num, to_num, now, -amount, description, "D"),
        (txn_no, to_num,   from_num, now,  amount, description, "C")
    ]
    sql_txn = """
    INSERT INTO Transactions
        (TransactionNumber, AccountNumber, OtherAccountNumber,
         TransactionDateTime, Amount, Description, TransactionTypeCode)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    cur.executemany(sql_txn, entries)
    con.commit()
    con.close()


def load_transactions(user_id: str,
                      account: str,
                      from_date: date,
                      to_date: date) -> list[Transaction]:
    """
    Return all Transaction objects for `account` between `from_date` and `to_date`.
    """
    sql_num = "SELECT AccountNumber FROM Accounts WHERE UserId=:user_id AND AccountName=:account_name"
    sql_txn = """
    SELECT TransactionNumber, AccountNumber, TransactionDateTime,
           TransactionTypeCode, Amount, BalanceAfter, OtherAccountNumber, Description
      FROM Transactions
     WHERE AccountNumber = :acct
       AND TransactionDateTime >= :from_time
       AND TransactionDateTime <  :before_time
    """

    before = to_date + timedelta(days=1)
    from_ts = datetime.combine(from_date, datetime.min.time()).isoformat()
    before_ts = datetime.combine(before,  datetime.min.time()).isoformat()

    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute(sql_num, {"user_id": user_id, "account_name": account})
    row = cur.fetchone()
    acct = row[0] if row else account

    cur.execute(sql_txn, {
        "acct": acct,
        "from_time": from_ts,
        "before_time": before_ts
    })
    rows = cur.fetchall()
    con.close()

    def describe(other_acct):
        if other_acct == ACCOUNT_WITHDRAW_TO:
            return "Withdraw"
        if other_acct == ACCOUNT_DEPOSIT_FROM:
            return "Deposit"
        return "Transfer"

    return [
        Transaction(
            transaction_number = r[0],
            account_number     = r[1],
            date_time          = r[2],
            transaction_type   = "Credit" if r[3] == "C" else "Debit",
            amount             = r[4],
            balance_after      = r[5],
            description        = describe(r[6]) + (" " + r[7] if r[7] else "")
        )
        for r in rows
    ]


def init_db():
    """
    Create the database and seed it from init.sql if bank.db is missing.
    """
    sql_path = Path(__file__).parent / "init.sql"
    con      = sqlite3.connect(DB_FILE)
    cur      = con.cursor()
    cur.executescript(sql_path.read_text())
    con.commit()
    con.close()
    
# Auto-init if missing
if not DB_FILE.exists():
    init_db()
