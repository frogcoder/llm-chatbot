from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class Account:
    """Represent an account of a user""" 

    account_number: str
    """The unique account number."""
    
    account_name: str
    """Name of the account."""

    balance: Decimal
    """The current balance of the account."""
<<<<<<< HEAD
    
    def __init__(self):
        self.account_number = ""
        self.account_name = ""
        self.balance = Decimal("0")
    
    def __str__(self):
        return f"{self.account_name} ({self.account_number}): {self.balance}"
=======

    currency_code: str
    """The currency of the fund in the account"""

    
@dataclass
class Transaction:
    """Represent one transaction of an account"""
    
    transaction_number: int
    """A unique string identifyig the transaction.  All records involved in one transaction share a transaction number"""
    
    account_number: str
    """The account number of transaction being applied to."""
    
    transaction_type: str
    """The transaction can be credit or debit."""
    
    date_time: datetime
    """The date and time the transaction happens."""
    
    amount: Decimal
    """The amount involved in the transaction"""
    
    description: str
    """Additional description of the transaction"""
    
    balance_after: Decimal
    """The account balance after the transaction"""
>>>>>>> main
