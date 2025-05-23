from datetime import date
from datetime import timedelta
from decimal import Decimal
import chatbot.database
from chatbot.models import Account
from chatbot.models import Transaction


def list_accounts(user_id: str) -> list[Account]:
    """
    List all of the user's accoutns.
    
    :param user_id: The user ID of the account owner.
    :return: All accounts that are avaialbe for transfering.
    """
    return chatbot.database.load_accounts(user_id)


def list_transfer_target_accounts(user_id: str,
                                  from_account: str) -> list[Account]:
    """
    List all of the user's accounts that the specified account can transfer to.

    :param user_id: The user ID of the account owner.
    :param from_account: The account number or account name that the fund will be transfered from.
    :return: All the accounts that funds can be transfered from the specified account.
    """
    return chatbot.database.load_transfer_target_accounts(user_id, from_account)


def transfer_between_accounts(user_id: str,
                              from_account: str, to_account: str,
                              amount: Decimal, description: str=""):
    """ Transfer specific amount of fund from one account to the other of the same owner.

    :param user_id: The user ID of the account owner.
    :param from_account: The account number or account name that the fund will be transfered from.
    :param to_account: The account number or account name that the fund will be transfered to.
    """
    chatbot.database.transfer_fund(user_id, from_account, to_account, amount,
                                   description)


def list_transactions(user_id: str, account: str,
                      days: int) -> list[Transaction]:
    """
    List all the transactions of the specified account.

    :param user_id: The user ID of the owner of the account.
    :param account: The number or name of the account.
    :param days: How many days in the past that the transactions need to be queried.
    :return: The transactions that match conditions set by the arguments.
    """
    to_date = date.today()
    from_date = to_date - timedelta(days=days)
    return chatbot.database.load_transactions(user_id, account,
                                              from_date, to_date)


def withdraw(user_id: str, account: str, amount: Decimal, description: str=""):
    transfer_between_accounts(user_id,
                              account,
                              chatbot.database.ACCOUNT_WITHDRAW_TO,
                              amount, description)


def deposit(user_id: str, account: str, amount: Decimal, description: str=""):
    transfer_between_accounts(user_id,
                              chatbot.database.ACCOUNT_DEPOSIT_FROM,
                              account,
                              amount,
                              description)
