from decimal import Decimal


class Account:
    """Represent an account of a user""" 
    account_number: str
    """The unique account number."""
    
    account_name: str
    """Name of the account."""

    balance: Decimal
    """The current balance of the account."""
