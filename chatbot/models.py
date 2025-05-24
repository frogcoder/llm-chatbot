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
    
    def __init__(self):
        self.account_number = ""
        self.account_name = ""
        self.balance = Decimal("0")
    
    def __str__(self):
        return f"{self.account_name} ({self.account_number}): {self.balance}"