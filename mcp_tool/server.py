import anyio
import click
import mcp.types as types
from mcp.server.lowlevel import Server
import os
import httpx
from starlette.responses import JSONResponse
from urllib.parse import parse_qs

# 导入工具注册器和工具加载器
from .tools import ToolRegistry
from .tools.loader import get_tool_instances

@click.command()
@click.option("--port", default=8000, help="Port to listen on for SSE")
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    help="Transport type",
)
def main(port: int, transport: str) -> int:
    app = Server("mcp-website-fetcher")
    
    # 加载所有工具实例
    tool_instances = get_tool_instances()

    @app.call_tool()
    async def fetch_tool( # type: ignore[unused-function]
        name: str, arguments: dict
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        if ToolRegistry.has_tool(name):
            tool_instance = tool_instances.get(name)
            if tool_instance:
                try:
                    return await tool_instance.execute(arguments)
                except Exception as e:
                    import traceback
                    error_details = traceback.format_exc()
                    return [types.TextContent(
                        type="text",
                        text=f"Error executing tool {name}: {str(e)}\n{error_details}"
                    )]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"Error: Tool instance for {name} not found"
                )]
        else:
            return [types.TextContent(
                type="text",
                text=f"Error: Unknown tool: {name}"
            )]

    @app.list_tools()
    async def list_tools() -> list[types.Tool]: # type: ignore[unused-function]
        return ToolRegistry.list_tools()

    if transport == "sse":
        from mcp.server.sse import SseServerTransport
        from starlette.applications import Starlette
        from starlette.routing import Mount, Route
        from starlette.middleware import Middleware
        from starlette.middleware.cors import CORSMiddleware

        sse = SseServerTransport("/messages/")

        # 鉴权函数
        async def verify_auth(request):
            """验证请求的鉴权信息"""
            # 获取鉴权地址，默认为 http://170.106.105.206:4000/users
            auth_url = os.environ.get("MCP_AUTH_URL", "http://170.106.105.206:4000/users")
            
            # 从URL查询参数中获取token
            query_params = parse_qs(request.scope.get("query_string", b"").decode())
            token = query_params.get("token", [None])[0]
            
            if not token:
                return False, "Token parameter is missing in URL"
            
            try:
                # 构建Authorization头
                auth_header = f"Bearer {token}"
                
                # 发送请求到鉴权服务
                async with httpx.AsyncClient() as client:
                    headers = {"Authorization": auth_header}
                    response = await client.get(auth_url, headers=headers, timeout=10.0)
                    
                    # 检查响应状态码
                    if response.status_code == 200:
                        return True, "Authentication successful"
                    else:
                        return False, f"Authentication failed with status code: {response.status_code}"
            except Exception as e:
                return False, f"Authentication error: {str(e)}"

        async def handle_sse(request):
            # 验证鉴权
            is_authenticated, message = await verify_auth(request)
            if not is_authenticated:
                return JSONResponse(
                    status_code=401,
                    content={"error": "Unauthorized", "message": message}
                )
            
            # 增加超时时间，以便处理大型文件
            request.scope["timeout"] = 300  # 设置为5分钟
            async with sse.connect_sse(
                request.scope, request.receive, request._send
            ) as streams:
                await app.run(
                    streams[0], streams[1], app.create_initialization_options()
                )

        # 添加CORS中间件以允许跨域请求
        middleware = [
            Middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_methods=["*"],
                allow_headers=["*"],
            )
        ]

        starlette_app = Starlette(
            debug=True,
            routes=[
                Route("/sse", endpoint=handle_sse),
                Mount("/messages/", app=sse.handle_post_message),
            ],
            middleware=middleware,
        )

        import uvicorn

        # 增加uvicorn的超时设置
        uvicorn.run(
            starlette_app, 
            host="0.0.0.0", 
            port=port,
            timeout_keep_alive=300,  # 增加保持连接的超时时间
        )
    else:
        from mcp.server.stdio import stdio_server

        async def arun():
            async with stdio_server() as streams:
                await app.run(
                    streams[0], streams[1], app.create_initialization_options()
                )

        anyio.run(arun)

    return 0
