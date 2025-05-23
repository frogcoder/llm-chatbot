"""Interactive Banking Assistant using Gemini and MCP."""
import os
import asyncio
import sys
import json
import random
from typing import Dict, List, Any, Optional, Tuple

# Add the parent directory to the Python path to import from src and chatbot
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from mcp import ClientSession
from mcp.client.sse import sse_client
import google.generativeai as genai
from dotenv import load_dotenv

# Import custom modules
from chatbot.config import DEFAULT_USER_ID, ACCOUNT_MAPPINGS
from chatbot.config_client import (
    RESPONSE_TEMPLATES, SYSTEM_INSTRUCTIONS, 
    TOOL_DEFINITIONS, MODEL_CONFIG
)
from chatbot.response_formatter import ResponseFormatter
from chatbot.intent_detector import IntentDetector

# Load environment variables
load_dotenv("../../.env")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class InteractiveBankingAssistant:
    """Interactive banking assistant using Gemini and MCP."""
    
    def __init__(self):
        """Initialize the banking assistant."""
        self.conversation_history = []
        self.user_id = DEFAULT_USER_ID
        self.session = None
        self.read_stream = None
        self.write_stream = None
        self.account_mappings = ACCOUNT_MAPPINGS
    
    async def initialize_session(self):
        """Initialize the MCP session."""
        from chatbot.config import MCP_HOST, MCP_PORT
        
        mcp_url = f"http://{MCP_HOST}:{MCP_PORT}/sse"
        self.sse_client = sse_client(mcp_url)
        self.read_stream, self.write_stream = await self.sse_client.__aenter__()
        self.session = ClientSession(self.read_stream, self.write_stream)
        await self.session.__aenter__()
        await self.session.initialize()
        print("\n🔄 Connected to RBC Banking Assistant")
    
    async def close_session(self):
        """Close the MCP session."""
        if self.session:
            await self.session.__aexit__(None, None, None)
        if hasattr(self, 'sse_client'):
            await self.sse_client.__aexit__(None, None, None)
    
    async def _process_response(self, response):
        """Process the response from Gemini, handling function calls."""
        try:
            # Check if the response has parts (structured response)
            if hasattr(response, 'parts'):
                result = []
                has_function_call = False
                
                for part in response.parts:
                    # Handle text parts
                    if hasattr(part, 'text') and part.text:
                        # Clean up the text
                        text = part.text
                        # Remove any function call syntax that might be in the text
                        text = text.replace('[Function Call:', '').replace(']', '')
                        # Remove "Assistant:" prefix
                        text = text.replace('Assistant:', '')
                        if text.strip():  # Only add non-empty text
                            result.append(text.strip())
                    
                    # Check if there's a function call
                    if hasattr(part, 'function_call'):
                        has_function_call = True
                    
                    # Handle function calls
                    if hasattr(part, 'function_call'):
                        func_call = part.function_call
                        function_name = func_call.name
                        
                        # Auto-fill account numbers for common account types
                        if function_name in ["get_account_balance", "get_transaction_history"]:
                            args = func_call.args
                            if "account_number" not in args or not args["account_number"]:
                                # Try to infer from the conversation history
                                last_user_msg = self.conversation_history[-1]["content"].lower()
                                if "savings" in last_user_msg or "saving" in last_user_msg:
                                    args["account_number"] = "2345678901"
                                elif "checking" in last_user_msg or "chequing" in last_user_msg:
                                    args["account_number"] = "1234567890"
                                elif "credit" in last_user_msg:
                                    args["account_number"] = "3456789012"
                        
                        # Execute the function call through MCP and wait for result
                        try:
                            # Call the function through the MCP session and await the result
                            function_result = await self._execute_function_call(function_name, func_call.args)
                            
                            # Parse the function result to extract actual data
                            parsed_result = self._parse_function_result(function_result)
                            
                            # Format the result using the ResponseFormatter
                            formatted_result = ResponseFormatter.format_response(function_name, parsed_result)
                            if formatted_result:
                                result.append(formatted_result)
                                
                        except Exception as e:
                            error_msg = random.choice(RESPONSE_TEMPLATES["error"]).format(error=str(e))
                            result.append(error_msg)
                
                # For simple greetings with no function calls, provide a friendly response
                if not has_function_call and not result:
                    return random.choice(RESPONSE_TEMPLATES["greeting"])
                
                # If there's an empty function call, provide a generic response
                if has_function_call and not result:
                    return "How can I help you with your banking needs today?"
                
                return "\n".join(result) if result else random.choice(RESPONSE_TEMPLATES["greeting"])
            else:
                # Simple text response
                return response.text
        except Exception as e:
            return f"Error processing response: {str(e)}"
    
    def _parse_function_result(self, result):
        """Parse the function result to extract the actual data."""
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
            
                        parsed = json.loads(result)
                        # Special handling for transaction objects
                        if isinstance(parsed, dict) and all(key in parsed for key in ['transaction_id', 'date', 'description']):
                            return [parsed]
                        return parsed
=======
                        return json.loads(result)
>>>>>>> main
                except:
                    pass
            
            # Return as is if we couldn't parse it
            return result
        except Exception as e:
            print(f"Error parsing function result: {e}")
            return result
    
    async def _execute_function_call(self, function_name, args):
        """Execute a function call through the MCP session."""
        try:
            # Check if function name is empty or invalid
            if not function_name or function_name.strip() == "":
                print(f"\n⚠️ Warning: Empty function name received")
                # Return a response that won't trigger "I've completed that action for you"
                return {
                    "content": "No valid function specified",
                    "skip_response": True,
                    "error": True
                }
            
            # Check for non-banking queries using the intent detector
            if function_name == "answer_banking_question" and args and "question" in args:
                question = args["question"]
                
                # Check if the question is banking-related
                if not IntentDetector.is_banking_related(question):
                    return {
                        "answer": random.choice(RESPONSE_TEMPLATES["non_banking"]),
                        "skip_function_call": True
                    }
                
                # Check for ambiguous inputs that shouldn't trigger function calls
                if IntentDetector.is_greeting(question) or len(question.strip()) <= 3:
                    return {
                        "answer": random.choice(RESPONSE_TEMPLATES["greeting"]),
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
                    from_acc = str(mcp_args["from_account"]).lower()
                    for key, value in self.account_mappings.items():
                        if key in from_acc:
                            mcp_args["from_account"] = value
                            break
                
                # Map to_account if it's a name
                if "to_account" in mcp_args:
                    to_acc = str(mcp_args["to_account"]).lower()
                    for key, value in self.account_mappings.items():
                        if key in to_acc:
                            mcp_args["to_account"] = value
                            break
            
            # Map account names for get_transaction_history and get_account_balance
            if function_name in ["get_transaction_history", "get_account_balance"] and "account_number" in mcp_args:
                acc = str(mcp_args["account_number"]).lower()
                for key, value in self.account_mappings.items():
                    if key in acc:
                        mcp_args["account_number"] = value
                        break
            
            print(f"\n🔧 Executing function: {function_name} with args: {mcp_args}")
            
            # Check if we should skip the function call
            if "skip_function_call" in mcp_args and mcp_args["skip_function_call"]:
                return {"answer": random.choice(RESPONSE_TEMPLATES["non_banking"]), "sources": []}
                
            # Call the function through MCP
            result = await self.session.call_tool(function_name, mcp_args)
            
            # Format the result for logging
            result_str = self._format_result_for_logging(result)
            
            # Print the result for debugging
            print(f"\n🔧 Function Result ({function_name}):")
            print(result_str)
            
            return result
        except Exception as e:
            error_msg = f"Error executing function {function_name}: {str(e)}"
            print(f"\n❌ {error_msg}")
            return {"error": error_msg}
    
<<<<<<< HEAD
    def _format_result_for_logging(self, result):
        """Format a result object for logging."""
        try:
            if isinstance(result, dict):
                # Try to pretty print if it's a dict
            elif isinstance(result, list):
                # For lists of objects (like accounts)
                if result and hasattr(result[0], '__dict__'):
                    # Convert dataclass objects to dicts for better display
                    return json.dumps([item.__dict__ for item in result], indent=2)
                else:
                    return "\n".join(str(item) for item in result)
            else:
                # Handle string results that might be JSON
                try:
                    if isinstance(result, str) and (result.startswith('{') or result.startswith('[')):
                        parsed = json.loads(result)
                        return json.dumps(parsed, indent=2)
                    else:
                        return str(result)
                except:
                    return str(result)
        except Exception as e:
            print(f"Error formatting result for logging: {e}")
            return str(result)
    
    def build_prompt(self, user_input):
        """Build the prompt with conversation history."""
        # Get system instructions from config and format with user_id
        system_prompt = SYSTEM_INSTRUCTIONS.format(user_id=self.user_id)
=======
    def build_prompt(self, user_input):
        """Build the prompt with conversation history"""
        # Start with system instructions
        system_prompt = f"""
You are my RBC banking assistant. You can help me with both:
        # Add current user input
        full_prompt = f"{system_prompt}\n\n{history}\n\nUser: {user_input}\n\nAssistant:"
        return full_prompt
    
    async def send_message(self, user_input):
<<<<<<< HEAD
        """Send a message to the assistant and get a response."""
        # Add user message to history
        self.conversation_history.append({"role": "user", "content": user_input})
        
        # Check for commands first
        command, arg = IntentDetector.detect_command(user_input)
        if command:
            if command == "exit":
                return random.choice(RESPONSE_TEMPLATES["farewell"])
            elif command == "clear":
                self.conversation_history = []
                return "Conversation history cleared."
            elif command == "user" and arg:
                self.user_id = arg
                return f"User ID changed to: {self.user_id}"
        
        # Check if this is a simple greeting
        if IntentDetector.is_greeting(user_input):
            response_text = random.choice(RESPONSE_TEMPLATES["greeting"])
=======
        """Send a message to the assistant and get a response"""
        # Add user message to history
        self.conversation_history.append({"role": "user", "content": user_input})
        
        # Check if this is a simple greeting
        greeting_patterns = ["hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening"]
        is_simple_greeting = user_input.lower().strip() in greeting_patterns or user_input.lower().strip() + "!" in greeting_patterns
        
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
>>>>>>> main
            print("\n🔁 Assistant:")
            print(response_text)
            self.conversation_history.append({"role": "assistant", "content": response_text})
            return response_text
        
<<<<<<< HEAD
        # For non-greetings, build the prompt with history
        try:
            # Create a model with the tools from config
            tool_config = [{
                "function_declarations": TOOL_DEFINITIONS
=======
        # For non-banking questions, use a special flag in the prompt
        if not is_transfer_request and "?" in user_input and not any(keyword in user_input.lower() for keyword in ["balance", "account", "money", "savings", "checking"]):
            # Add a flag to indicate this is likely a general question
            self.conversation_history.append({"role": "system", "content": "This appears to be a general question, not a banking operation. Use answer_banking_question for this."})
        
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
1. For account information and operations, use ONLY the appropriate banking tool:
   - For checking balances: ALWAYS use get_account_balance with account_number="ABC123" for Savings or "DEF456" for Checking
   - For listing accounts: ONLY use list_user_accounts when the user explicitly asks to see their accounts
   - For transfers: ALWAYS use transfer_funds with from_account, to_account, and amount
   - For transaction history: ALWAYS use get_transaction_history with account_number="ABC123" for Savings or "DEF456" for Checking

2. For general banking questions about RBC products and services, ALWAYS use answer_banking_question.

3. NEVER respond with "I'm working on your request" or similar phrases.

4. NEVER show function calls in your responses to the user.

5. NEVER list accounts unless explicitly asked. Do not call list_user_accounts for operations like transfers or checking balances.

6. Be helpful, concise, and professional in your responses.

7. CRITICAL: For simple greetings like "hi", "hello", "hey", etc., DO NOT USE ANY FUNCTIONS AT ALL. 
   Just respond with a friendly greeting text. Never call answer_banking_question for greetings.
   
8. CRITICAL: For topics unrelated to banking or RBC services, ALWAYS use answer_banking_question to respond.
   NEVER use transfer_funds or other banking operation functions for non-banking questions.
   
9. For transfers, ALWAYS extract the account numbers directly:
   - "transfer $50 from checking to savings" → use transfer_funds with from_account="DEF456", to_account="ABC123", amount="50"
   - Do NOT call list_user_accounts first

10. For transaction history, ALWAYS use get_transaction_history directly:
    - "show me transactions for my savings" → use get_transaction_history with account_number="ABC123"
    - Do NOT call list_user_accounts first
    
11. ONLY use transfer_funds when the user explicitly asks to transfer money between accounts.
    For any other questions, including general questions about banking, use answer_banking_question.
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
>>>>>>> main
            }]
            
            # Create a model with the tools
            model = genai.GenerativeModel(
<<<<<<< HEAD
                model_name=MODEL_CONFIG["model_name"],
                generation_config=genai.GenerationConfig(
                    temperature=MODEL_CONFIG["temperature"]
                ),
                tools=tool_config,
                tool_config={"function_calling_config": MODEL_CONFIG["tool_calling_config"]}
            )
            
            # For very short, ambiguous inputs, respond conversationally without calling functions
            if len(user_input.strip()) <= 3 and not user_input.strip().isdigit():
                response_text = random.choice(RESPONSE_TEMPLATES["greeting"])
                print("\n🔁 Assistant:")
                print(response_text)
                self.conversation_history.append({"role": "assistant", "content": response_text})
                return response_text
            
            # Handle direct account queries
            if "balance" in user_input.lower() or "transaction" in user_input.lower() or "history" in user_input.lower():
                account_number = None
                if "savings" in user_input.lower() or "saving" in user_input.lower():
                    account_number = "2345678901"
                elif "checking" in user_input.lower() or "chequing" in user_input.lower():
                    account_number = "1234567890"
                elif "credit" in user_input.lower():
                    account_number = "3456789012"
            
            # Generate content with system instructions from config
            system_instructions = SYSTEM_INSTRUCTIONS.format(user_id=self.user_id)
            response = await asyncio.to_thread(
                model.generate_content,
                [system_instructions, user_input]
            )
                    
            # Process and print response
            assistant_response = await self._process_response(response)
            
            # Clean up the response by removing generic messages
            assistant_response = self._clean_response(assistant_response)
            
=======
                model_name='gemini-1.5-pro',
                generation_config=genai.GenerationConfig(
                    temperature=0
                ),
                tools=tool_config,
                tool_config={"function_calling_config": {"mode": "ANY"}}
            )
            
            # Generate content with system instructions
            response = await asyncio.to_thread(
                model.generate_content,
                [system_instructions, prompt]
            )
            
            # Process and print response
            assistant_response = await self._process_response(response)
>>>>>>> main
            print("\n🔁 Assistant:")
            print(assistant_response)
            
            # Add assistant response to history
            self.conversation_history.append({"role": "assistant", "content": assistant_response})
            
            return assistant_response
            
        except Exception as e:
<<<<<<< HEAD
            error_msg = random.choice(RESPONSE_TEMPLATES["error"]).format(error=str(e))
            print(f"\n❌ {error_msg}")
            return error_msg
    
    def _clean_response(self, response):
        """Clean up the response by removing generic messages."""
        # List of generic phrases to remove
        generic_phrases = [
            "I've completed that action for you.",
            "I've processed your request.",
            "I've completed the transfer for you."
        ]
        
        # Remove each generic phrase
        cleaned_response = response
        for phrase in generic_phrases:
            cleaned_response = cleaned_response.replace(phrase, "").strip()
        
        # Remove any double newlines that might have been created
        cleaned_response = cleaned_response.replace("\n\n\n", "\n\n")
        
        return cleaned_response
    
    async def run_interactive(self):
        """Run the assistant in interactive mode."""
=======
            error_msg = f"Error: {str(e)}"
            print(f"\n❌ {error_msg}")
            return error_msg
    
    async def run_interactive(self):
        """Run the assistant in interactive mode"""
>>>>>>> main
        try:
            await self.initialize_session()
            
            print("\n🏦 RBC Banking Assistant")
            print("Type 'exit' to quit, 'clear' to clear conversation history")
            print("Type 'user <id>' to change user ID (current: " + self.user_id + ")")
            
            while True:
                try:
                    user_input = input("\n💬 You: ")
                    
<<<<<<< HEAD
                    # Check for exit command
                    command, _ = IntentDetector.detect_command(user_input)
                    if command == "exit":
                        print(random.choice(RESPONSE_TEMPLATES["farewell"]))
                        break
                    
                    # Process the message
                    response = await self.send_message(user_input)
                    
                    # If the response indicates exit, break the loop
                    if command == "exit":
                        break
                        
=======
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
>>>>>>> main
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
<<<<<<< HEAD
    """Main entry point for the interactive banking assistant."""
=======
>>>>>>> main
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
