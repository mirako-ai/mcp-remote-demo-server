import asyncio
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
from fastmcp.client.auth import BearerAuth

transport = StreamableHttpTransport(
    "http://localhost:8080/mcp/",
    auth=BearerAuth("your auth token"),
    headers={"M-PROFILE-ID": "your profile ID"},
)
async def main():
    # Connection is established here
    async with Client(transport) as client:
        print(f"Client connected: {client.is_connected()}")

        # Make MCP calls within the context
        tools = await client.list_tools()
        print(f"Available tools: {tools}")

        # if any(tool.name == "get_available_lockers_from_zone" for tool in tools):
        #     result = await client.call_tool("get_available_lockers_from_zone", {"zone": "A"})
        #     print(f"Locker result: {result}")

    # Connection is closed automatically here
    print(f"Client connected: {client.is_connected()}")

if __name__ == "__main__":
    asyncio.run(main())