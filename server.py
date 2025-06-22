# server.py
# getting inspector run use the following commang:
# npx @modelcontextprotocol/inspector \
#   uv \
#   run \
#   server.py
# Lastly click on the url with the authenticaiton key already on there

from mcp.server.fastmcp import FastMCP
from simulation import move_arm, open_gripper, close_gripper

# Create an MCP server
mcp = FastMCP("Demo")


# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


@mcp.tool()
def move_arm(target, target_orn=None):
    # set_arm(target_pos=target, target_orn=target_orn)
    return


@mcp.tool()
def open_gripper():
    # set_gripper(closed=False)
    return


@mcp.tool()
def close_gripper():
    try:
        close_gripper()
        return "Gripper closed successfully"
    except Exception as e:
        return f"Error closing gripper: {str(e)}"


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"


if __name__ == '__main__':
    mcp.run(transport='stdio')
