# client_gemini.py
import os, asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client
from google import genai
from dotenv import load_dotenv

load_dotenv("../.env")
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

async def main():
    async with sse_client("http://127.0.0.1:8050/sse") as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            prompt = """
You are my bank assistant. Help me manage my accounts.
What accounts does user_abc123 have?
Can I transfer from Savings to Checking?
Transfer 100.50 from account ABC123 to DEF456.
"""
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

if __name__ == "__main__":
    asyncio.run(main())
