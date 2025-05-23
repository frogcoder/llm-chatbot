import sqlite3
from decimal import Decimal
from pathlib import Path
from chatbot.models import Account


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
    matched_user_id = cur.fetchone()
    con.close()
    return True if matched_user_id else False


def load_accounts(user_id: str) -> list[Account]:
    """
    Query accounts that belong to the speicfied user.

    :param user_id: The user ID of the account owner
    :return: All the accounts that belong the the user
    """
    pass


def load_transfer_target_accounts(user_id: str, from_account: str) -> list[Account]:
    """
    Query accounts that the specified account can trasfer fund to.

    :param user_id: The user ID of the account owner
    :param from_account: The account number or account name that the fund would be transferred from.
    :return: All the accounts that the specified account can transfer to.
    """
    pass


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
    pass


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
