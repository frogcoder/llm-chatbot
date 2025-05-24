from datetime import date
from datetime import timedelta
from decimal import Decimal
import chatbot.database
from chatbot.models import Account
from chatbot.database import load_accounts, load_transfer_target_accounts, transfer_fund_between_accounts


def list_accounts(user_id: str) -> list[Account]:
    """
    List all of the user's accoutns.
    
    :param user_id: The user ID of the account owner.
    :return: All accounts that are avaialbe for transfering.
    """
    return load_accounts(user_id)


def list_transfer_target_accounts(user_id: str,
                                  from_account: str) -> list[Account]:
    """
    List all of the user's accounts that the specified account can transfer to.

    :param user_id: The user ID of the account owner.
    :param from_account: The account number or account name that the fund will be transfered from.
    :return: All the accounts that funds can be transfered from the specified account.
    """
    return load_transfer_target_accounts(user_id, from_account)


def transfer_between_accounts(user_id: str,
                              from_account: str, to_account: str,
                              amount: Decimal, description: str=""):
    """ Transfer specific amount of fund from one account to the other of the same owner.

    :param user_id: The user ID of the account owner.
    :param from_account: The account number or account name that the fund will be transfered from.
    :param to_account: The account number or account name that the fund will be transfered to.
    """
    transfer_fund_between_accounts(user_id, from_account, to_account, amount)
