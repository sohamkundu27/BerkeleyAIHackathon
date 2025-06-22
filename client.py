# client.py
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_add_function():
    # Configure connection to your server
    server_params = StdioServerParameters(
        command="python",
        args=["server.py"]
    )

    try:
        # Connect to the server
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the connection
                await session.initialize()
                print("Connected to MCP server")

                # # List available tools
                # tools_response = await session.list_tools()
                # print(
                #     f"📋 Available tools: {[tool.name for tool in tools_response.tools]}")

                # Test the add function
                print("\n🧮 Testing add function...")
                await session.call_tool("move_arm", {"target": [0.85, -0.2, 1.2]})
                await session.call_tool("move_arm", {"target": [0.85, -0.2, 0.97]})
                await session.call_tool("close_gripper", {})
                await session.call_tool("move_arm", {"target": [0.85, -0.2, 1.2]})
                await session.call_tool("move_arm", {"target": [0.85, -0.6, 1.2]})
                await session.call_tool("move_arm", {"target": [0.85, -0.6, 0.97]})
                await session.call_tool("open_gripper", {})
                await session.call_tool("move_arm", {"target": [0.85, -0.6, 1.2]})
                await session.call_tool("move_arm", {"target": [0.7, 0.0, 1.2]})
                await session.call_tool("move_arm", {"target": [0.7, 0.0, 0.97]})
                await session.call_tool("close_gripper", {})
                await session.call_tool("move_arm", {"target": [0.7, 0.0, 1.2]})
                await session.call_tool("move_arm", {"target": [0.85, -0.6, 1.2]})
                await session.call_tool("move_arm", {"target": [0.85, -0.6, 1.03]})
                await session.call_tool("open_gripper", {})
                await session.call_tool("move_arm", {"target": [0.85, -0.2, 1.2]})
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("Starting MCP client...")
    asyncio.run(test_add_function())
