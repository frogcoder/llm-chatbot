"""Response formatter for the banking assistant."""
import json
import random
from decimal import Decimal
from typing import Dict, List, Any, Optional, Union

class ResponseFormatter:
    """Formats responses from function calls into user-friendly messages."""
    
    @staticmethod
    def format_response(function_name: str, result: Any) -> str:
        """Format a function result based on the function name."""
        formatter_method = getattr(
            ResponseFormatter, 
            f"format_{function_name}", 
            ResponseFormatter.format_generic
        )
        return formatter_method(result)
    
    @staticmethod
    def format_generic(result: Any) -> str:
        """Generic formatter for any result."""
        if isinstance(result, dict) and result.get("skip_response", False):
            return ""
        
        if isinstance(result, dict) and "error" in result:
            return f"I'm sorry, there was an error: {result['error']}"
            
        return ""
    
    @staticmethod
    def format_get_account_balance(result: Any) -> str:
        """Format account balance information."""
        try:
            # If it's a dictionary with balance info
            if isinstance(result, dict):
                if 'balance' in result:
                    return (f"Your {result.get('account_name', 'account')} "
                           f"({result.get('account_number', '')}) has a balance of "
                           f"{result.get('balance', '')} {result.get('currency', 'CAD')}.")
            
            # If it's a list, try to find the first item with balance info
            if isinstance(result, list):
                for item in result:
                    if isinstance(item, dict) and 'balance' in item:
                        return (f"Your {item.get('account_name', 'account')} "
                               f"({item.get('account_number', '')}) has a balance of "
                               f"{item.get('balance', '')} {item.get('currency', 'CAD')}.")
            
            # If we couldn't extract structured data, return a generic message
            return "I found your account balance information."
        except Exception as e:
            print(f"Error formatting balance: {e}")
            return "I found your account balance information."
    
    @staticmethod
    def format_list_user_accounts(result: Any) -> str:
        """Format a list of accounts."""
        try:
            accounts = ResponseFormatter._extract_accounts(result)
            if accounts and len(accounts) > 0:
                account_lines = ["Here are your accounts:"]
                for account in accounts:
                    account_lines.append(
                        f"- {account.get('account_name', 'Account')} "
                        f"({account.get('account_number', '')})"
                    )
                return "\n".join(account_lines)
            else:
                return "You don't have any accounts set up yet."
        except Exception as e:
            print(f"Error formatting accounts: {e}")
            return "I found your accounts but couldn't format them properly."
    
    @staticmethod
    def format_transfer_funds(result: Any) -> str:
        """Format transfer result."""
        try:
            if isinstance(result, str):
                if "Transferred" in result:
                    return result
                elif "failed" in result:
                    return result
                else:
                    return "I've completed the transfer for you."
            else:
                return "I've completed the transfer for you."
        except Exception as e:
            print(f"Error formatting transfer result: {e}")
            return "The transfer has been processed."
    
    @staticmethod
    def format_get_transaction_history(result: Any) -> str:
        """Format transaction history."""
        try:
            # Handle both list and single transaction object formats
            transactions = []
            
            if isinstance(result, list):
                transactions = result
            elif isinstance(result, dict):
                # Single transaction as a dict
                transactions = [result]
            elif isinstance(result, str):
                # Try to parse JSON string
                try:
                    json_data = json.loads(result)
                    if isinstance(json_data, list):
                        transactions = json_data
                    elif isinstance(json_data, dict):
                        transactions = [json_data]
                except:
                    pass
            
            if transactions and len(transactions) > 0:
                lines = ["Here are the recent transactions for your account:"]
                for i, transaction in enumerate(transactions[:5]):  # Show only first 5 transactions
                    date = transaction.get('date', 'Unknown date')
                    desc = transaction.get('description', 'Transaction')
                    amount = transaction.get('amount', '0.00')
                    lines.append(f"- {date}: {desc}: ${amount}")
                if len(transactions) > 5:
                    lines.append(f"...and {len(transactions) - 5} more transactions.")
                return "\n".join(lines)
            else:
                return "I couldn't find any transactions for this account."
        except Exception as e:
            print(f"Error formatting transaction history: {e}")
            return "I found your transaction history but couldn't format it properly."
    
    @staticmethod
    def format_answer_banking_question(result: Any) -> str:
        """Format RAG answer."""
        try:
            if isinstance(result, dict) and "answer" in result:
                answer = result["answer"]
                
                # Check if the answer indicates no information was found
                if ("I don't have information" in answer or 
                    "I don't have specific information" in answer):
                    return ("I'm sorry, but I don't have specific information about that in my "
                           "RBC knowledge base. I can only answer questions about RBC banking "
                           "products, services, and policies. Is there something else I can "
                           "help you with regarding RBC?")
                else:
                    response = answer
                
                # Optionally add sources with clear visual distinction
                if "sources" in result and result["sources"]:
                    sources = result["sources"]
                    if len(sources) == 1:
                        # Truncate long source URLs if needed
                        source = sources[0]
                        if len(source) > 80:
                            display_source = source[:77] + "..."
                        else:
                            display_source = source
                        response += f"<div class='sources-section'><strong>Source:</strong> {display_source}</div>"
                    elif len(sources) > 1:
                        sources_html = "<div class='sources-section'><strong>Sources:</strong><ul>"
                        for source in sources:
                            # Truncate long source URLs if needed
                            if len(source) > 80:
                                display_source = source[:77] + "..."
                            else:
                                display_source = source
                            sources_html += f"<li>{display_source}</li>"
                        sources_html += "</ul></div>"
                        response += sources_html
                
                return response
            else:
                # Try to extract answer from complex object
                answer = ResponseFormatter._extract_rag_answer(result)
                if answer:
                    return answer
                else:
                    return "I couldn't find specific information about that in my knowledge base."
        except Exception as e:
            print(f"Error formatting RAG answer: {e}")
            return "I found some information but couldn't format it properly."
    
    @staticmethod
    def _extract_accounts(result: Any) -> List[Dict[str, Any]]:
        """Extract accounts from a complex result object."""
        accounts = []
        
        # If result is a list of dictionaries
        if isinstance(result, list):
            for item in result:
                if isinstance(item, dict) and 'account_name' in item and 'account_number' in item:
                    accounts.append(item)
        
        # If result is a dictionary with account info
        elif isinstance(result, dict) and 'account_name' in result and 'account_number' in result:
            accounts.append(result)
        
        return accounts
    
    @staticmethod
    def _extract_rag_answer(result: Any) -> Optional[str]:
        """Extract the answer from a RAG result."""
        try:
            # If it's a dictionary with an answer
            if isinstance(result, dict) and 'answer' in result:
                return result['answer']
            
            # If it's a list, try to find the first item with an answer
            if isinstance(result, list):
                for item in result:
                    if isinstance(item, dict) and 'answer' in item:
                        return item['answer']
            
            # If it's a string, return it directly
            if isinstance(result, str):
                return result
            
            return None
        except:
            return None
