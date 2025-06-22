# client.py
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import math


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
                apple_pos = [0.82, -0.3, 0.6849899910813102]
                bottle_pos = [0.7, 0.1, 0.8]
                box_pos = [1, 0.1, 0.7]
                banana_pos = [0.893, 0.313, 0.660]
                container_pos = [0.9, -0.75, 0.73]

                for obj_pos in [box_pos]:
                    orn = [0, math.pi, math.pi / 2]
                    dist_above = 0.3

                    above_obj = obj_pos.copy()
                    above_obj[2] += dist_above

                    result = await session.call_tool("move_arm", {"target": above_obj, "target_orn": orn})
                    print(f"move above object: {result.content[0].text}")

                    result = await session.call_tool("move_arm", {"target": obj_pos, "target_orn": orn})
                    print(f"move to object: {result.content[0].text}")

                    result = await session.call_tool("close_gripper", {})
                    print(f"close_gripper: {result.content[0].text}")

                    result = await session.call_tool("move_arm", {"target": above_obj})
                    print(f"lift object: {result.content[0].text}")

                    above_container = container_pos.copy()
                    above_container[2] += 0.3

                    result = await session.call_tool("move_arm", {"target": above_container})
                    print(f"move to container: {result.content[0].text}")

                    result = await session.call_tool("open_gripper", {})
                    print(f"open_gripper: {result.content[0].text}")

                    result = await session.call_tool("move_arm", {"target": above_container})
                    print(f"move to container: {result.content[0].text}")

                    result = await session.call_tool("move_arm", {"target": [0.85, -0.2, 0.9], "target_orn": orn})
                    print(f"reset arm position: {result.content[0].text}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("Starting MCP client...")
    asyncio.run(test_add_function())