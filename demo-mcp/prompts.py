from mcp.server.fastmcp.prompts.base import Message
from mcp.server.fastmcp import current_mcp as mcp

@mcp.prompt(
    name="escalate",
    description="Generate a handoff message for a human agent",
)
def prompt_escalate(user_message: str) -> list[Message]:
    """
    Stub: wrap user_message in an assistant/system prompt flow
    """
    return [
        Message.system("You've been escalated to a human agent."),
        Message.user(user_message),
    ]