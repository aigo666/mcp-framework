import asyncio

import pytest
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


@pytest.mark.asyncio
async def test_mcp_server_tools() -> None:
    """Test that we can connect to the server and list available tools."""
    async with stdio_client(
        StdioServerParameters(command="uv", args=["run", "mcp-simple-tool"])
    ) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            assert tools is not None, "Tools list should not be None"
            assert tools.tools, "Server should provide at least one tool"


@pytest.mark.asyncio
async def test_mcp_server_mood() -> None:
    """Test that the mood tool works correctly."""
    async with stdio_client(
        StdioServerParameters(command="uv", args=["run", "mcp-simple-tool"])
    ) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("mood", {"question": "How are you today?"})
            assert result is not None, "Mood response should not be None"
            assert "❤️" in str(result), "Mood response should contain a heart emoji"


if __name__ == "__main__":
    asyncio.run(test_mcp_server_tools())
    asyncio.run(test_mcp_server_mood()) 