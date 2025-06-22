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

                # List available tools
                tools_response = await session.list_tools()
                print(
                    f"📋 Available tools: {[tool.name for tool in tools_response.tools]}")

                # Test the add function
                print("\n🧮 Testing add function...")
                result = await session.call_tool("add", {"a": 100, "b": 50})
                print(f"Result of 100 + 50 = {result.content[0].text}")

                result = await session.call_tool("move_arm", {"target": [0.5, 0.5, 0.5]})
                print(f"Result of move_arm: {result.content[0].text}")

                await session.call_tool("open_gripper")
                await session.call_tool("close_gripper")
                await session.call_tool("open_gripper")
                await session.call_tool("close_gripper")


                print("\n✨ All tests completed successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("Starting MCP client...")
    asyncio.run(test_add_function())
