from mcp.server.fastmcp import current_mcp as mcp

@mcp.resource()
def auth_login(username: str, password: str) -> dict:
    """
    stub: check credentials → return { "ok": bool, "token": str }
    """
    return {
        "ok": False,
        "token": ""
    }

@mcp.resource()
def list_faqs() -> list[str]:
    """
    Stub: return list of FAQ IDs
    """
    return []

@mcp.resource()
def fetch_faq(faq_id: str) -> str:
    """
    Stub: return raw answer text
    """
    return ""