"""Intent detection for the banking assistant."""
import re
from typing import Dict, List, Any, Optional, Tuple
from chatbot.config_client import BANKING_DOMAINS, GREETING_PATTERNS, FAREWELL_PATTERNS, COMMANDS

class IntentDetector:
    """Detects user intents from input text."""
    
    @staticmethod
    def is_banking_related(text: str) -> bool:
        """Check if the text is related to banking."""
        text_lower = text.lower()
        return any(domain in text_lower for domain in BANKING_DOMAINS)
    
    @staticmethod
    def get_account_number_from_text(text: str, account_mappings: dict) -> str:
        """Extract account number from text based on account name mentions."""
        text_lower = text.lower()
        for key, value in account_mappings.items():
            if key in text_lower:
                return value
        return None
    
    @staticmethod
    def is_greeting(text: str) -> bool:
        """Check if the text is a greeting."""
        text_lower = text.strip().lower()
        return (text_lower in GREETING_PATTERNS or 
                text_lower + "!" in GREETING_PATTERNS or
                text_lower.startswith("hello") or
                text_lower.startswith("hi "))
    
    @staticmethod
    def is_farewell(text: str) -> bool:
        """Check if the text is a farewell."""
        text_lower = text.strip().lower()
        return any(text_lower == pattern or text_lower.startswith(pattern + " ")
                  for pattern in FAREWELL_PATTERNS)
    
    @staticmethod
    def is_short_response(text: str) -> bool:
        """Check if this is likely a short response to a previous question."""
        # If it's just one or two words and not a clear command
        words = text.strip().split()
        return (len(words) <= 2 and 
                not any(cmd in text.lower() for cmd in ["transfer", "balance", "history", "accounts"]))
    
    @staticmethod
    def is_transfer_request(text: str) -> bool:
        """Check if this is a transfer request."""
        transfer_keywords = ["transfer", "send", "move money", "move funds"]
        return any(keyword in text.lower() for keyword in transfer_keywords)
    
    @staticmethod
    def detect_command(text: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Detect if the text contains a command.
        
        Returns:
            Tuple of (command_type, command_arg) or (None, None) if no command detected
        """
        text_lower = text.strip().lower()
        
        # Check for exit command
        if any(text_lower == cmd for cmd in COMMANDS["exit"]):
            return ("exit", None)
            
        # Check for clear command
        if any(text_lower == cmd for cmd in COMMANDS["clear"]):
            return ("clear", None)
            
        # Check for user command
        if text_lower.startswith("user "):
            return ("user", text[5:].strip())
            
        return (None, None)
    
    @staticmethod
    def extract_amount(text: str) -> Optional[str]:
        """Extract a monetary amount from text."""
        # Look for dollar amounts like $50, $50.00, 50 dollars, etc.
        dollar_pattern = r'\$?(\d+(?:\.\d{1,2})?)\s*(?:dollars?|CAD)?'
        match = re.search(dollar_pattern, text)
        if match:
            return match.group(1)
        return None
