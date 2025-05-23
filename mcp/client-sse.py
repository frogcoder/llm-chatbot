# client_gemini.py
import os, asyncio
import sys
import re
import json
from mcp import ClientSession
from mcp.client.sse import sse_client
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv("../.env")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class InteractiveBankingAssistant:
    def __init__(self):
        self.conversation_history = []
        self.user_id = "test1"  # Default user ID from the database
        self.session = None
        self.read_stream = None
        self.write_stream = None
    
    async def initialize_session(self):
        """Initialize the MCP session"""
        self.sse_client = sse_client("http://127.0.0.1:8050/sse")
        self.read_stream, self.write_stream = await self.sse_client.__aenter__()
        self.session = ClientSession(self.read_stream, self.write_stream)
        await self.session.__aenter__()
        await self.session.initialize()
        print("\n🔄 Connected to RBC Banking Assistant")
    
    async def close_session(self):
        """Close the MCP session"""
        if self.session:
            await self.session.__aexit__(None, None, None)
        if hasattr(self, 'sse_client'):
            await self.sse_client.__aexit__(None, None, None)
    
    async def _process_response(self, response):
        """Process the response from Gemini, handling function calls"""
        try:
            # Check if the response has parts (structured response)
            if hasattr(response, 'parts'):
                result = []
                has_function_call = False
                
                for part in response.parts:
                    # Handle text parts
                    if hasattr(part, 'text') and part.text:
                        # Remove any function call syntax that might be in the text
                        text = part.text
                        text = re.sub(r'\[Function Call:.*?\]', '', text)
                        text = re.sub(r'^\s*Assistant:\s*', '', text)  # Remove "Assistant:" prefix
                        if text.strip():  # Only add non-empty text
                            result.append(text.strip())
                    
                    # Check if there's a function call
                    if hasattr(part, 'function_call'):
                        has_function_call = True
                    
                    # Handle function calls
                    if hasattr(part, 'function_call'):
                        func_call = part.function_call
                        function_name = func_call.name
                        
                        # Execute the function call through MCP and wait for result
                        try:
                            # Call the function through the MCP session and await the result
                            function_result = await self._execute_function_call(function_name, func_call.args)
                            
                            # Parse the function result to extract actual data
                            parsed_result = self._parse_function_result(function_result)
                            
                            # If we got a result from a banking function, format it nicely for the user
                            if function_name != "answer_banking_question":
                                # For account-related functions, format a nice response
                                if function_name == "get_account_balance":
                                    try:
                                        if isinstance(parsed_result, dict) and "balance" in parsed_result:
                                            result.append(f"Your {parsed_result.get('account_name', '')} account ({parsed_result.get('account_number', '')}) has a balance of {parsed_result.get('balance', '')} {parsed_result.get('currency', '')}.")
                                        else:
                                            # Try to extract from the content if it's a complex object
                                            result.append(self._format_account_balance(parsed_result))
                                    except Exception as e:
                                        print(f"Error formatting balance: {e}")
                                        result.append(self._format_account_balance(parsed_result))
                                elif function_name == "list_user_accounts":
                                    try:
                                        accounts = self._extract_accounts(parsed_result)
                                        if accounts and len(accounts) > 0:
                                            result.append("Here are your accounts:")
                                            for account in accounts:
                                                result.append(f"- {account.get('account_name', 'Account')} ({account.get('account_number', '')})")
                                        else:
                                            result.append("You don't have any accounts set up yet.")
                                    except Exception as e:
                                        print(f"Error formatting accounts: {e}")
                                        result.append("I found your accounts but couldn't format them properly.")
                                elif function_name == "transfer_funds":
                                    try:
                                        if isinstance(parsed_result, str):
                                            if "Transferred" in parsed_result:
                                                result.append(parsed_result)
                                            elif "failed" in parsed_result:
                                                result.append(parsed_result)
                                            else:
                                                result.append("I've completed the transfer for you.")
                                        else:
                                            result.append("I've completed the transfer for you.")
                                    except Exception as e:
                                        print(f"Error formatting transfer result: {e}")
                                        result.append("The transfer has been processed.")
                                elif function_name == "get_transaction_history":
                                    try:
                                        # Handle both list and single transaction object formats
                                        transactions = []
                                        
                                        if isinstance(parsed_result, list):
                                            transactions = parsed_result
                                        elif isinstance(parsed_result, dict):
                                            # Single transaction as a dict
                                            transactions = [parsed_result]
                                        elif isinstance(parsed_result, str):
                                            # Try to parse JSON string
                                            try:
                                                json_data = json.loads(parsed_result)
                                                if isinstance(json_data, list):
                                                    transactions = json_data
                                                elif isinstance(json_data, dict):
                                                    transactions = [json_data]
                                            except:
                                                pass
                                        
                                        if transactions and len(transactions) > 0:
                                            result.append(f"Here are the recent transactions for your account:")
                                            for i, transaction in enumerate(transactions[:5]):  # Show only first 5 transactions
                                                date = transaction.get('date', 'Unknown date')
                                                desc = transaction.get('description', 'Transaction')
                                                amount = transaction.get('amount', '0.00')
                                                result.append(f"- {date}: {desc} - {amount}")
                                            if len(transactions) > 5:
                                                result.append(f"...and {len(transactions) - 5} more transactions.")
                                        else:
                                            result.append("I couldn't find any transactions for this account.")
                                    except Exception as e:
                                        print(f"Error formatting transaction history: {e}")
                                        result.append("I found your transaction history but couldn't format it properly.")
                                else:
                                    # Generic handling for other functions
                                    result.append(self._format_generic_result(function_name, parsed_result))
                            else:
                                # For RAG questions, extract the answer
                                try:
                                    if isinstance(parsed_result, dict) and "answer" in parsed_result:
                                        answer = parsed_result["answer"]
                                        
                                        # Check if the answer indicates no information was found
                                        if "I don't have information" in answer or "I don't have specific information" in answer:
                                            result.append("I'm sorry, but I don't have specific information about that in my RBC knowledge base. I can only answer questions about RBC banking products, services, and policies. Is there something else I can help you with regarding RBC?")
                                        else:
                                            result.append(answer)
                                        
                                        # Optionally add sources
                                        if "sources" in parsed_result and parsed_result["sources"]:
                                            sources = parsed_result["sources"]
                                            if len(sources) == 1:
                                                result.append(f"\nSource: {sources[0]}")
                                            elif len(sources) > 1:
                                                result.append("\nSources:")
                                                for source in sources:
                                                    result.append(f"- {source}")
                                    else:
                                        # Try to extract answer from complex object
                                        answer = self._extract_rag_answer(parsed_result)
                                        if answer:
                                            result.append(answer)
                                        else:
                                            result.append("I couldn't find specific information about that in my knowledge base.")
                                except Exception as e:
                                    print(f"Error formatting RAG answer: {e}")
                                    result.append("I found some information but couldn't format it properly.")
                        except Exception as e:
                            result.append(f"I'm sorry, I couldn't complete that action: {str(e)}")
                
                # For simple greetings with no function calls, provide a friendly response
                if not has_function_call and not result:
                    greeting_responses = [
                        "Hello! How can I help with your RBC banking needs today?",
                        "Hi there! How may I assist you with your RBC accounts or services today?",
                        "Good day! I'm here to help with your RBC banking questions.",
                        "Welcome! How can I assist you with your RBC banking today?"
                    ]
                    import random
                    return random.choice(greeting_responses)
                
                return "\n".join(result) if result else "Hello! How can I help you with your banking needs today?"
            else:
                # Simple text response
                return response.text
        except Exception as e:
            return f"Error processing response: {str(e)}"
    
    def _parse_function_result(self, result):
        """Parse the function result to extract the actual data"""
        try:
            # Check if result has content attribute (MCP response format)
            if hasattr(result, 'content') and result.content:
                # Extract text content
                text_contents = []
                for content in result.content:
                    if hasattr(content, 'text'):
                        text_contents.append(content.text)
                
                # Try to parse each text content as JSON
                parsed_contents = []
                for text in text_contents:
                    try:
                        parsed_contents.append(json.loads(text))
                    except:
                        parsed_contents.append(text)
                
                # Special handling for get_transaction_history
                # If we have a single transaction object, wrap it in a list
                if len(parsed_contents) == 1:
                    content = parsed_contents[0]
                    # Check if this looks like a transaction object
                    if isinstance(content, dict) and all(key in content for key in ['transaction_id', 'date', 'description']):
                        return [content]
                    return content
                
                return parsed_contents
            
            # If it's a dictionary or list, return as is
            if isinstance(result, (dict, list)):
                return result
            
            # If it's a string that looks like JSON, parse it
            if isinstance(result, str):
                try:
                    if result.strip().startswith('{') or result.strip().startswith('['):
                        parsed = json.loads(result)
                        # Special handling for transaction objects
                        if isinstance(parsed, dict) and all(key in parsed for key in ['transaction_id', 'date', 'description']):
                            return [parsed]
                        return parsed
                except:
                    pass
            
            # Return as is if we couldn't parse it
            return result
        except Exception as e:
            print(f"Error parsing function result: {e}")
            return result
    
    def _extract_accounts(self, result):
        """Extract accounts from a complex result object"""
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
    
    def _format_account_balance(self, result):
        """Format account balance information from a complex result"""
        try:
            # If it's a dictionary with balance info
            if isinstance(result, dict):
                if 'balance' in result:
                    return f"Your {result.get('account_name', 'account')} ({result.get('account_number', '')}) has a balance of {result.get('balance', '')} {result.get('currency', 'CAD')}."
            
            # If it's a list, try to find the first item with balance info
            if isinstance(result, list):
                for item in result:
                    if isinstance(item, dict) and 'balance' in item:
                        return f"Your {item.get('account_name', 'account')} ({item.get('account_number', '')}) has a balance of {item.get('balance', '')} {item.get('currency', 'CAD')}."
            
            # If we couldn't extract structured data, return a generic message
            return "I found your account balance information."
        except:
            return "I found your account balance information."
    
    def _format_generic_result(self, function_name, result):
        """Format a generic function result in a user-friendly way"""
        if function_name == "transfer_funds":
            # Try to extract transfer details
            if isinstance(result, str) and "Transferred" in result:
                return result
            return "Your transfer has been processed."
        
        elif function_name == "get_transaction_history":
            # Format transaction history
            try:
                if isinstance(result, list) and len(result) > 0:
                    transactions_text = [f"- {tx.get('date', 'Unknown')}: {tx.get('description', 'Transaction')} - {tx.get('amount', '0.00')}" 
                                        for tx in result[:5]]  # Show only first 5
                    transactions_str = "\n".join(transactions_text)
                    if len(result) > 5:
                        transactions_str += f"\n...and {len(result) - 5} more transactions."
                    return f"Here are your recent transactions:\n{transactions_str}"
                return "I couldn't find any transactions for your account."
            except Exception as e:
                print(f"Error in transaction formatting: {e}")
                return "I found your transaction history."
        
        # More specific response based on function
        if function_name == "transfer_funds":
            return "Your transfer has been processed."
        elif function_name == "get_account_balance":
            return "I've retrieved your account balance."
        elif function_name == "get_transaction_history":
            return "Here's your transaction history."
        elif function_name == "list_user_accounts":
            return "Here are your accounts."
        else:
            return "I've processed your request."
    
    def _extract_rag_answer(self, result):
        """Extract the answer from a RAG result"""
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
    
    def is_short_response(self, text):
        """Check if this is likely a short response to a previous question"""
        # If it's just one or two words and not a clear command
        words = text.strip().split()
        return (len(words) <= 2 and 
                not any(cmd in text.lower() for cmd in ["transfer", "balance", "history", "accounts"]))
    
    async def _execute_function_call(self, function_name, args):
        """Execute a function call through the MCP session"""
        try:
            # Check if function name is empty or invalid
            if not function_name or function_name.strip() == "":
                print(f"\n⚠️ Warning: Empty function name received")
                return {"error": "No function specified", "skip_response": True}
            
            # Check if this is likely a non-banking query that doesn't need a function call
            if function_name == "answer_banking_question" and args and "question" in args:
                question = args["question"].lower()
                non_banking_keywords = ["fix", "repair", "washing machine", "microwave", "toaster", "car", "vehicle"]
                if any(keyword in question for keyword in non_banking_keywords):
                    return {
                        "answer": "I can't help with that topic. I'm designed to assist with RBC banking questions only.",
                        "skip_function_call": True
                    }
                
            # Convert args from Gemini format to what MCP expects
            mcp_args = {}
            if args:  # Check if args is not None before iterating
                for key, value in args.items():
                    # Special handling for amount to ensure it's a string
                    if key == "amount" and function_name == "transfer_funds":
                        # Remove any $ sign and ensure it's a string
                        if isinstance(value, (int, float)):
                            mcp_args[key] = str(value)
                        elif isinstance(value, str):
                            # Remove $ and any commas
                            clean_value = value.replace('$', '').replace(',', '')
                            mcp_args[key] = clean_value
                        else:
                            mcp_args[key] = "0"
                    else:
                        mcp_args[key] = value
            
            # Add user_id automatically if not provided
            if function_name != "answer_banking_question" and "user_id" not in mcp_args:
                mcp_args["user_id"] = self.user_id
            
            # Map account names to account numbers for transfer_funds
            if function_name == "transfer_funds":
                # Map from_account if it's a name
                if "from_account" in mcp_args:
                    from_acc = mcp_args["from_account"].lower()
                    if "check" in from_acc or "chequ" in from_acc:
                        mcp_args["from_account"] = "1234567890"
                    elif "sav" in from_acc:
                        mcp_args["from_account"] = "2345678901"
                    elif "credit" in from_acc:
                        mcp_args["from_account"] = "3456789012"
                
                # Map to_account if it's a name
                if "to_account" in mcp_args:
                    to_acc = mcp_args["to_account"].lower()
                    if "check" in to_acc or "chequ" in to_acc:
                        mcp_args["to_account"] = "1234567890"
                    elif "sav" in to_acc:
                        mcp_args["to_account"] = "2345678901"
                    elif "credit" in to_acc:
                        mcp_args["to_account"] = "3456789012"
            
            # Map account names for get_transaction_history and get_account_balance
            if function_name in ["get_transaction_history", "get_account_balance"] and "account_number" in mcp_args:
                acc = mcp_args["account_number"].lower()
                if "check" in acc or "chequ" in acc:
                    mcp_args["account_number"] = "1234567890"
                elif "sav" in acc:
                    mcp_args["account_number"] = "2345678901"
                elif "credit" in acc:
                    mcp_args["account_number"] = "3456789012"
            
            print(f"\n🔧 Executing function: {function_name} with args: {mcp_args}")
            
            # Check if we should skip the function call
            if "skip_function_call" in mcp_args and mcp_args["skip_function_call"]:
                return {"answer": "I can only help with RBC banking-related questions.", "sources": []}
                
            # Call the function through MCP
            result = await self.session.call_tool(function_name, mcp_args)
            
            # Format the result for logging
            if isinstance(result, dict):
                # Try to pretty print if it's a dict
                result_str = json.dumps(result, indent=2)
            elif isinstance(result, list):
                # For lists of objects (like accounts)
                if result and hasattr(result[0], '__dict__'):
                    # Convert dataclass objects to dicts for better display
                    result_str = json.dumps([item.__dict__ for item in result], indent=2)
                else:
                    result_str = "\n".join(str(item) for item in result)
            else:
                # Handle string results that might be JSON
                try:
                    if isinstance(result, str) and (result.startswith('{') or result.startswith('[')):
                        parsed = json.loads(result)
                        result_str = json.dumps(parsed, indent=2)
                    else:
                        result_str = str(result)
                except:
                    result_str = str(result)
            
            # Print the result for debugging
            print(f"\n🔧 Function Result ({function_name}):")
            print(result_str)
            
            # We don't add function results to conversation history anymore
            # They'll be incorporated into the assistant's response
            
            return result
        except Exception as e:
            error_msg = f"Error executing function {function_name}: {str(e)}"
            print(f"\n❌ {error_msg}")
            return {"error": error_msg}
    
    def build_prompt(self, user_input):
        """Build the prompt with conversation history"""
        # Start with system instructions
        system_prompt = f"""
You are my RBC banking assistant. You can help me with both:
1. Banking operations like checking balances and making transfers for user ID: {self.user_id}
2. Answering questions about RBC's products and services using your knowledge base

ALWAYS use the appropriate tools when needed:
- For account balances, ALWAYS use get_account_balance with the account number
- For listing accounts, ONLY use list_user_accounts when explicitly asked to show accounts
- For transfers, ALWAYS use transfer_funds with from_account, to_account, and amount
- For transaction history, ALWAYS use get_transaction_history with the account number
- For product/service questions, ALWAYS use answer_banking_question

IMPORTANT: For transfers and balance checks, use the account numbers directly:
- Savings account: ABC123
- Checking account: DEF456

CRITICAL: ONLY use transfer_funds when I explicitly ask to transfer money between accounts.
For all other questions, including questions about banking products or services, use answer_banking_question.

NEVER say you don't have access to account information - use the tools instead.
"""
        
        # Add conversation history
        history = "\n\n".join([f"User: {msg['content']}" 
                              if msg['role'] == 'user' else f"Assistant: {msg['content']}" 
                              for msg in self.conversation_history])
        
        # Add current user input
        full_prompt = f"{system_prompt}\n\n{history}\n\nUser: {user_input}\n\nAssistant:"
        return full_prompt
    
    async def send_message(self, user_input):
        """Send a message to the assistant and get a response"""
        # Add user message to history
        self.conversation_history.append({"role": "user", "content": user_input})
        
        # Check if this is a simple greeting
        greeting_patterns = ["hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening", "yo", "sup", "howdy"]
        is_simple_greeting = user_input.lower().strip() in greeting_patterns or user_input.lower().strip() + "!" in greeting_patterns
        
        # Check if this is a short response to a previous question
        is_short_response = self.is_short_response(user_input) and len(self.conversation_history) >= 2
        
        # Check if this is a transfer request
        transfer_keywords = ["transfer", "send", "move money", "move funds"]
        is_transfer_request = any(keyword in user_input.lower() for keyword in transfer_keywords)
        
        # For simple greetings, respond directly without calling the model
        if is_simple_greeting:
            greeting_responses = [
                "Hello! How can I help with your RBC banking needs today?",
                "Hi there! How may I assist you with your RBC accounts or services today?",
                "Good day! I'm here to help with your RBC banking questions.",
                "Welcome! How can I assist you with your RBC banking today?"
            ]
            import random
            response_text = random.choice(greeting_responses)
            print("\n🔁 Assistant:")
            print(response_text)
            self.conversation_history.append({"role": "assistant", "content": response_text})
            return response_text
        
        # No special flag needed - the system instructions will handle question routing
        
        # For non-greetings, build the prompt with history
        prompt = self.build_prompt(user_input)
        
        try:
            # Send to Gemini
            model = genai.GenerativeModel('gemini-1.5-pro')
            
            # Define the tools directly in the format Gemini expects
            # Add more specific instructions to guide the model
            system_instructions = f"""
You are an RBC Banking Assistant helping user {self.user_id}.

IMPORTANT INSTRUCTIONS:
1. ONLY USE ONE FUNCTION PER REQUEST. Choose the most appropriate function for each user request.

2. For account information and operations:
   - For checking balances: use get_account_balance with account_number="1234567890" for checking or "2345678901" for savings
   - For listing accounts: use list_user_accounts ONLY when explicitly asked to see accounts
   - For transfers: use transfer_funds with exact account numbers and amount as a string (e.g., "50.00")
   - For transaction history: use get_transaction_history with the exact account number

3. For general banking questions about RBC products and services, use answer_banking_question.

4. NEVER use multiple functions for a single request.

5. For transfers, map account names to numbers:
   - "Checking" or "Chequing" = "1234567890"
   - "Savings" or "Saving" = "2345678901"
   - "Credit Card" = "3456789012"

6. CRITICAL: For money transfers, ALWAYS use transfer_funds with:
   - from_account: the exact account number (not name)
   - to_account: the exact account number (not name)
   - amount: the amount as a string (e.g., "50.00")

7. NEVER call transfer_funds unless the user explicitly asks to transfer money.

8. For transaction history, use get_transaction_history with the exact account number.

9. NEVER call multiple functions for the same request.

10. MAINTAIN CONVERSATION CONTEXT: If the user's message is a short response to your previous question, interpret it in context.
    - If you asked "What account are you transferring from?" and they reply "savings", use that to complete the previous request.
    - If you can't determine what function to call, DO NOT call any function. Just respond conversationally.

11. For short, ambiguous messages like "yo", "sup", etc., treat them as greetings and DO NOT call any functions.
"""
            
            tool_config = [{
                "function_declarations": [
                    {
                        "name": "answer_banking_question",
                        "description": "Answer a banking question using the RAG system with RBC documentation.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "question": {
                                    "type": "string",
                                    "description": "The banking question to answer"
                                }
                            },
                            "required": ["question"]
                        }
                    },
                    {
                        "name": "list_user_accounts",
                        "description": "List all accounts for a given user.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "user_id": {
                                    "type": "string",
                                    "description": "The ID of the user"
                                }
                            },
                            "required": ["user_id"]
                        }
                    },
                    {
                        "name": "list_target_accounts",
                        "description": "List all other accounts this user can transfer to.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "user_id": {
                                    "type": "string",
                                    "description": "The ID of the user"
                                },
                                "from_account": {
                                    "type": "string",
                                    "description": "The source account number"
                                }
                            },
                            "required": ["user_id", "from_account"]
                        }
                    },
                    {
                        "name": "transfer_funds",
                        "description": "Transfer funds from one account to another.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "user_id": {
                                    "type": "string",
                                    "description": "The ID of the user"
                                },
                                "from_account": {
                                    "type": "string",
                                    "description": "The source account number"
                                },
                                "to_account": {
                                    "type": "string",
                                    "description": "The destination account number"
                                },
                                "amount": {
                                    "type": "string",
                                    "description": "The amount to transfer"
                                }
                            },
                            "required": ["user_id", "from_account", "to_account", "amount"]
                        }
                    },
                    {
                        "name": "get_account_balance",
                        "description": "Get the balance of a specific account.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "user_id": {
                                    "type": "string",
                                    "description": "The ID of the user"
                                },
                                "account_number": {
                                    "type": "string",
                                    "description": "The account number"
                                }
                            },
                            "required": ["user_id", "account_number"]
                        }
                    },
                    {
                        "name": "get_transaction_history",
                        "description": "Get the transaction history for a specific account.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "user_id": {
                                    "type": "string",
                                    "description": "The ID of the user"
                                },
                                "account_number": {
                                    "type": "string",
                                    "description": "The account number"
                                },
                                "days": {
                                    "type": "integer",
                                    "description": "Number of days of history to retrieve (default: 30)"
                                }
                            },
                            "required": ["user_id", "account_number"]
                        }
                    }
                ]
            }]
            
            # Create a model with the tools
            model = genai.GenerativeModel(
                model_name='gemini-1.5-pro',
                generation_config=genai.GenerationConfig(
                    temperature=0.1  # Slight increase in temperature for more natural responses
                ),
                tools=tool_config,
                tool_config={"function_calling_config": {"mode": "AUTO"}}
            )
            
            # Generate content with system instructions
            response = await asyncio.to_thread(
                model.generate_content,
                [system_instructions, user_input]
            )
            
            # For short responses that might be follow-ups to previous questions
            if is_short_response:
                # Get the last assistant message to provide context
                last_assistant_msg = ""
                for msg in reversed(self.conversation_history[:-1]):  # Skip the current user message
                    if msg["role"] == "assistant":
                        last_assistant_msg = msg["content"]
                        break
                
                # Add context to the prompt
                if "what account" in last_assistant_msg.lower():
                    # If the assistant asked about accounts, interpret the response in that context
                    print(f"\n🔄 Interpreting short response in context of previous question")
                
                # For very short, ambiguous inputs like "yo", just respond conversationally without calling functions
                if len(user_input.strip()) <= 3 and not user_input.strip().isdigit():
                    greeting_responses = [
                        "Hello! How can I help with your RBC banking needs today?",
                        "Hi there! How may I assist you with your RBC accounts or services today?",
                        "I'm here to help with your banking needs. What can I do for you?",
                        "Welcome! How can I assist you with your RBC banking today?"
                    ]
                    import random
                    assistant_response = random.choice(greeting_responses)
                    print("\n🔁 Assistant:")
                    print(assistant_response)
                    self.conversation_history.append({"role": "assistant", "content": assistant_response})
                    return assistant_response
                    
            # Process and print response
            assistant_response = await self._process_response(response)
            
            # Remove any "I've completed that action for you" that might have been added
            if "I've completed that action for you" in assistant_response:
                assistant_response = assistant_response.replace("I've completed that action for you", "").strip()
            
            print("\n🔁 Assistant:")
            print(assistant_response)
            
            # Add assistant response to history
            self.conversation_history.append({"role": "assistant", "content": assistant_response})
            
            return assistant_response
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(f"\n❌ {error_msg}")
            return error_msg
    
    async def run_interactive(self):
        """Run the assistant in interactive mode"""
        try:
            await self.initialize_session()
            
            print("\n🏦 RBC Banking Assistant")
            print("Type 'exit' to quit, 'clear' to clear conversation history")
            print("Type 'user <id>' to change user ID (current: " + self.user_id + ")")
            
            while True:
                try:
                    user_input = input("\n💬 You: ")
                    
                    if user_input.lower() in ['exit', 'quit', 'q']:
                        print("Goodbye! Thank you for using RBC Banking Assistant.")
                        break
                    
                    elif user_input.lower() == 'clear':
                        self.conversation_history = []
                        print("Conversation history cleared.")
                        continue
                    
                    elif user_input.lower().startswith('user '):
                        # Change user ID
                        new_user_id = user_input[5:].strip()
                        if new_user_id:
                            self.user_id = new_user_id
                            print(f"User ID changed to: {self.user_id}")
                        else:
                            print(f"Current user ID: {self.user_id}")
                        continue
                    
                    # Normal message
                    await self.send_message(user_input)
                except KeyboardInterrupt:
                    print("\nInterrupted. Exiting...")
                    break
                except Exception as e:
                    print(f"\n❌ Error: {str(e)}")
                    print("Continuing...")
        finally:
            print("\nClosing connection...")
            await self.close_session()

async def main():
    try:
        assistant = InteractiveBankingAssistant()
        await assistant.run_interactive()
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        print("The assistant has encountered an unrecoverable error and must exit.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
