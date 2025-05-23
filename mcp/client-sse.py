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
        self.user_id = "user_abc123"  # Default user ID
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
                for part in response.parts:
                    # Handle text parts
                    if hasattr(part, 'text') and part.text:
                        # Remove any function call syntax that might be in the text
                        text = part.text
                        text = re.sub(r'\[Function Call:.*?\]', '', text)
                        text = re.sub(r'^\s*Assistant:\s*', '', text)  # Remove "Assistant:" prefix
                        if text.strip():  # Only add non-empty text
                            result.append(text.strip())
                    
                    # Handle function calls
                    if hasattr(part, 'function_call'):
                        func_call = part.function_call
                        function_name = func_call.name
                        
                        # Execute the function call through MCP and wait for result
                        try:
                            # Call the function through the MCP session and await the result
                            function_result = await self._execute_function_call(function_name, func_call.args)
                            
                            # If we got a result from a banking function, format it nicely for the user
                            if function_name != "answer_banking_question":
                                # For account-related functions, format a nice response
                                if function_name == "get_account_balance":
                                    try:
                                        if isinstance(function_result, dict) and "balance" in function_result:
                                            result.append(f"Your {function_result.get('account_name', '')} account ({function_result.get('account_number', '')}) has a balance of {function_result.get('balance', '')} {function_result.get('currency', '')}.")
                                        else:
                                            result.append(f"I found your account information: {function_result}")
                                    except:
                                        result.append(f"I found your account information: {function_result}")
                                elif function_name == "list_user_accounts":
                                    try:
                                        if isinstance(function_result, list):
                                            result.append("Here are your accounts:")
                                            for account in function_result:
                                                result.append(f"- {account.get('account_name', 'Account')} ({account.get('account_number', '')})")
                                        else:
                                            result.append(f"I found your accounts: {function_result}")
                                    except:
                                        result.append(f"I found your accounts: {function_result}")
                                else:
                                    # Generic handling for other functions
                                    result.append(f"I've completed that action for you: {function_result}")
                            else:
                                # For RAG questions, extract the answer
                                try:
                                    if isinstance(function_result, dict) and "answer" in function_result:
                                        result.append(function_result["answer"])
                                    else:
                                        result.append(str(function_result))
                                except:
                                    result.append(str(function_result))
                        except Exception as e:
                            result.append(f"I'm sorry, I couldn't complete that action: {str(e)}")
                
                return "\n".join(result) if result else "I'm looking into that for you..."
            else:
                # Simple text response
                return response.text
        except Exception as e:
            return f"Error processing response: {str(e)}"
    
    async def _execute_function_call(self, function_name, args):
        """Execute a function call through the MCP session"""
        try:
            # Convert args from Gemini format to what MCP expects
            mcp_args = {}
            if args:  # Check if args is not None before iterating
                for key, value in args.items():
                    mcp_args[key] = value
            
            # Add user_id automatically if not provided
            if function_name != "answer_banking_question" and "user_id" not in mcp_args:
                mcp_args["user_id"] = self.user_id
            
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
- For account balances, use get_account_balance
- For listing accounts, use list_user_accounts
- For transfers, use transfer_funds
- For transaction history, use get_transaction_history
- For product/service questions, use answer_banking_question

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
        
        # Build the prompt with history
        prompt = self.build_prompt(user_input)
        
        try:
            # Send to Gemini
            model = genai.GenerativeModel('gemini-1.5-pro')
            
            # Define the tools directly in the format Gemini expects
            # Add more specific instructions to guide the model
            system_instructions = f"""
You are an RBC Banking Assistant helping user {self.user_id}.

IMPORTANT INSTRUCTIONS:
1. For account information (balances, transfers, etc.), ALWAYS use the appropriate banking tool:
   - Use get_account_balance to check balances
   - Use list_user_accounts to list accounts
   - Use transfer_funds for transfers
   - Use get_transaction_history for transaction history

2. For general banking questions about products and services, ALWAYS use answer_banking_question.

3. NEVER respond with "I'm working on your request" or similar phrases.

4. NEVER show function calls in your responses to the user.

5. If the user asks about account information, ALWAYS use the appropriate tool rather than saying you don't have access.

6. Be helpful, concise, and professional in your responses.
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
