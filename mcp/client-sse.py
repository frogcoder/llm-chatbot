# client_gemini.py
import os, asyncio
import sys
from mcp import ClientSession
from mcp.client.sse import sse_client
from google import genai
from dotenv import load_dotenv

load_dotenv("../.env")
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class InteractiveBankingAssistant:
    def __init__(self):
        self.conversation_history = []
        self.user_id = "user_abc123"  # Default user ID
        self.session = None
        self.read_stream = None
        self.write_stream = None
    
    async def initialize_session(self):
        """Initialize the MCP session"""
        self.read_stream, self.write_stream = await sse_client("http://127.0.0.1:8050/sse").__aenter__()
        self.session = ClientSession(self.read_stream, self.write_stream)
        await self.session.__aenter__()
        await self.session.initialize()
        print("\n🔄 Connected to RBC Banking Assistant")
    
    async def close_session(self):
        """Close the MCP session"""
        if self.session:
            await self.session.__aexit__(None, None, None)
        if self.read_stream and self.write_stream:
            await sse_client("http://127.0.0.1:8050/sse").__aexit__(None, None, None)
    
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
        history = "\n\n".join([f"User: {msg['role'] == 'user' and msg['content']}" 
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
            response = await client.aio.models.generate_content(
                model="gemini-1.5-pro",
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    temperature=0,
                    tools=[self.session],
                ),
            )
            
            # Print and store response
            assistant_response = response.text
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
        await self.initialize_session()
        
        print("\n🏦 RBC Banking Assistant")
        print("Type 'exit' to quit, 'clear' to clear conversation history")
        print("Type 'user <id>' to change user ID (current: " + self.user_id + ")")
        
        try:
            while True:
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
                
        finally:
            await self.close_session()

async def main():
    assistant = InteractiveBankingAssistant()
    await assistant.run_interactive()

if __name__ == "__main__":
    asyncio.run(main())
