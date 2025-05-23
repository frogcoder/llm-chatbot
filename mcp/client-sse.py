# client_gemini.py
import os, asyncio
import sys
from mcp import ClientSession
from mcp.client.sse import sse_client
from google import genai
from dotenv import load_dotenv

load_dotenv("../.env")
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

async def chat_with_banking_assistant(prompt):
    """Function to chat with the banking assistant using a custom prompt"""
    async with sse_client("http://127.0.0.1:8050/sse") as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            response = await client.aio.models.generate_content(
                model="gemini-1.5-pro",
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    temperature=0,
                    tools=[session],
                ),
            )
            print("\n🔁 Gemini response:")
            print(response.text)
            return response.text

async def main():
    # Default prompt if none provided
    default_prompt = """
You are my RBC banking assistant. You can help me with both:
1. Banking operations like checking balances and making transfers
2. Answering questions about RBC's products and services using your knowledge base

First, tell me what accounts I have (user_abc123).
Then, what's the balance in my Checking account?
Also, can you explain RBC's investment options for beginners?
"""
    
    # Get prompt from command line arguments or use default
    prompt = sys.argv[1] if len(sys.argv) > 1 else default_prompt
    await chat_with_banking_assistant(prompt)

if __name__ == "__main__":
    asyncio.run(main())
