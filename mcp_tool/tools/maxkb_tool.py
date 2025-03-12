"""
MaxKB工具，用于请求MaxKB API并处理返回结果
"""

import httpx
import json
import mcp.types as types
from . import BaseTool, ToolRegistry

@ToolRegistry.register
class MaxKbTool(BaseTool):
    """MaxKB API请求工具"""
    name = "maxkb"
    description = "请求MaxKB API并返回处理后的结果"
    input_schema = {
        "type": "object",
        "required": ["message"],
        "properties": {
            "message": {
                "type": "string",
                "description": "要发送的消息内容",
            },
            "re_chat": {
                "type": "boolean",
                "description": "是否重新开始对话",
                "default": False
            },
            "stream": {
                "type": "boolean",
                "description": "是否使用流式响应",
                "default": True
            }
        },
    }
    
    async def execute(self, arguments: dict) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """执行API请求并处理返回结果"""
        if "message" not in arguments:
            return [types.TextContent(
                type="text",
                text="错误: 缺少必要参数 'message'"
            )]
            
        try:
            # 准备请求参数
            url = "http://localhost:8080/api/application/chat_message/4a99a706-ff0f-11ef-be75-0242ac110002"
            headers = {
                "accept": "application/json",
                "AUTHORIZATION": "application-e689000edd89acb58572482651fa88e0",
                "Content-Type": "application/json"
            }
            data = {
                "message": arguments["message"],
                "re_chat": arguments.get("re_chat", False),
                "stream": arguments.get("stream", True)
            }
            
            # 发送请求
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=data)
                response.raise_for_status()
                
                # 处理响应内容
                content_parts = []
                
                # 按行处理响应
                for line in response.text.split('\n'):
                    if line.startswith('data: '):
                        try:
                            # 解析JSON数据
                            data = json.loads(line[6:])  # 去掉'data: '前缀
                            if "content" in data:
                                content = data["content"]
                                if content:  # 只添加非空内容
                                    content_parts.append(content)
                        except json.JSONDecodeError:
                            continue  # 忽略无法解析的行
                
                # 拼接所有内容
                result = ''.join(content_parts)
                
                return [types.TextContent(
                    type="text",
                    text=result if result else "未获取到有效内容"
                )]
                
        except httpx.HTTPError as e:
            return [types.TextContent(
                type="text",
                text=f"请求错误: {str(e)}"
            )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"处理错误: {str(e)}"
            )] 