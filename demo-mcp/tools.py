from mcp.server.fastmcp import current_mcp as mcp

@mcp.tool()
def classify_intent(message: str) -> str:
    """
    stub: should return one of ["transfer", "faq", "unknown"]
    """

    #TODO: call LLM / promp-engineering right here
    return "unknowkn"

@mcp.tool()
def transfer_money(from_id: str, to_id: str, amount: float) -> str:
    """
    stub: should return one of ["success", "failure"]
    As well as authentication and authorization + write to DB -> return True if successful
    """

    #TODO: call real auth + DB API
    return False