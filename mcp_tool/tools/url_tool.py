import httpx
import mcp.types as types
from . import BaseTool, ToolRegistry

@ToolRegistry.register
class UrlTool(BaseTool):
    """URL获取工具，用于获取网站内容"""
    name = "url"
    description = "Fetches a website and returns its content"
    input_schema = {
        "type": "object",
        "required": ["url"],
        "properties": {
            "url": {
                "type": "string",
                "description": "URL to fetch",
            }
        },
    }
    
    async def execute(self, arguments: dict) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """获取网站内容"""
        if "url" not in arguments:
            return [types.TextContent(
                type="text",
                text="Error: Missing required argument 'url'"
            )]
            
        url = arguments["url"]
        headers = {
            "User-Agent": "MCP Test Server (github.com/modelcontextprotocol/python-sdk)"
        }
        try:
            timeout = httpx.Timeout(10.0, connect=5.0)
            async with httpx.AsyncClient(
                follow_redirects=True, 
                headers=headers,
                timeout=timeout
            ) as client:
                response = await client.get(url)
                response.raise_for_status()
                return [types.TextContent(type="text", text=response.text)]
        except httpx.TimeoutException:
            return [types.TextContent(
                type="text",
                text="Error: Request timed out while trying to fetch the website."
            )]
        except httpx.HTTPStatusError as e:
            return [types.TextContent(
                type="text",
                text=(f"Error: HTTP {e.response.status_code} "
                      "error while fetching the website.")
            )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error: Failed to fetch website: {str(e)}"
            )] 