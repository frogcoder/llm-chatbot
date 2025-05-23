# client_gemini.py
import os, asyncio
import sys
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
    
    def _process_response(self, response):
        """Process the response from Gemini, handling function calls"""
        try:
            # Check if the response has parts (structured response)
            if hasattr(response, 'parts'):
                result = []
                for part in response.parts:
                    # Handle text parts
                    if hasattr(part, 'text') and part.text:
                        result.append(part.text)
                    
                    # Handle function calls
                    if hasattr(part, 'function_call'):
                        func_call = part.function_call
                        function_name = func_call.name
                        
                        # Format function call for display
                        args_str = ""
                        if hasattr(func_call, 'args') and func_call.args:
                            # Convert args to a readable format
                            args_dict = {}
                            for key, value in func_call.args.items():
                                args_dict[key] = value
                            args_str = ", ".join(f"{k}={v}" for k, v in args_dict.items())
                        
                        # Add formatted function call to result
                        result.append(f"[Function Call: {function_name}({args_str})]")
                        
                        # Execute the function call through MCP
                        try:
                            # Call the function through the MCP session
                            asyncio.create_task(self._execute_function_call(function_name, func_call.args))
                        except Exception as e:
                            result.append(f"[Error executing function: {str(e)}]")
                
                return "\n".join(result)
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
            for key, value in args.items():
                mcp_args[key] = value
            
            # Call the function through MCP
            result = await self.session.call_tool(function_name, mcp_args)
            
            # Format the result
            if isinstance(result, dict):
                result_str = "\n".join(f"{k}: {v}" for k, v in result.items())
            elif isinstance(result, list):
                result_str = "\n".join(str(item) for item in result)
            else:
                result_str = str(result)
            
            # Print the result
            print(f"\n🔧 Function Result ({function_name}):")
            print(result_str)
            
            # Add to conversation history
            self.conversation_history.append({
                "role": "function",
                "name": function_name,
                "content": result_str
            })
            
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

Always use the appropriate tools when needed:
- Use banking tools for account operations
- Use the RAG system (answer_banking_question) for product/service questions
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
            
            # For now, let's use a direct approach with the function calling format
            # that Gemini expects
            
            # Define the tools directly in the format Gemini expects
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
                generation_config=genai.GenerationConfig(temperature=0),
                tools=tool_config
            )
            
            # Generate content
            response = await asyncio.to_thread(
                model.generate_content,
                prompt
            )
            
            # Process and print response
            assistant_response = self._process_response(response)
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
