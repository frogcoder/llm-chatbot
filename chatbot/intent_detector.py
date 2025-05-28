"""Intent detection for the banking assistant."""
from typing import Optional, Tuple
from chatbot.config_client import COMMANDS

class IntentDetector:
    """Detects user commands from input text."""
    
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
