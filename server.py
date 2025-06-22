# server.py
# getting inspector run use the following commang:
# npx @modelcontextprotocol/inspector \
#   uv \
#   run \
#   server.py
# Lastly click on the url with the authenticaiton key already on there

from mcp.server.fastmcp import FastMCP
from robot_controller import RobotSim
import os
os.environ["DISPLAY"] = ":0"

# Create an MCP server
mcp = FastMCP("Demo")
sim = RobotSim()


# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


@mcp.tool()
def move_arm(target, target_orn=None):
    sim.move_arm(target, target_orn)
    return f"Arm moved to {target} with orientation {target_orn}"


@mcp.tool()
def open_gripper():
    sim.open_gripper()
    return "Gripper opened"


@mcp.tool()
def close_gripper():
    sim.close_gripper()
    return "Gripper closed"


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"


if __name__ == '__main__':
    mcp.run(transport='stdio')
