from mcp.server.fastmcp import FastMCP

mcp = FastMCP(name='BankingDemo',
              host='127.0.0.1',
              port=8050,
             )

@mcp.tool()
def add(a: int, b: int) -> int:
    """
    Adds two numbers together.
    """
    return a + b

if __name__ == '__main__':
    transport = 'sse'
    if transport == 'stdio':
        print('Running server with stdio transport')
        mcp.run(transport='stdio')
    elif transport == 'sse':
        print('Running server with SSE transport')
        mcp.run(transport='sse')
    else:
        raise ValueError(f"Unknown transport: {transport}")