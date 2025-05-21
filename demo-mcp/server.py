from mcp.server.fastmcp import FastMCP
import tools, resource, prompts 

mcp = FastMCP("BankingDemo")

if __name__ == "__main__":
    mcp.run(transport='stdio')