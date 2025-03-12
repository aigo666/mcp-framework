"""
MaxKB工具，用于请求MaxKB API并处理返回结果
"""

import httpx
import json
import os
import traceback
import mcp.types as types
from . import BaseTool, ToolRegistry
import logging
import asyncio
import socket

# 设置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 设置httpcore的超时
os.environ['HTTPCORE_TIMEOUT'] = '60'
os.environ['HTTPX_TIMEOUT'] = '60'

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
    
    def _check_env_variables(self):
        """检查必要的环境变量是否存在"""
        required_vars = [
            'MAXKB_HOST',
            'MAXKB_CHAT_ID',
            'MAXKB_APPLICATION_ID',
            'MAXKB_AUTHORIZATION'
        ]
        env_values = {}
        missing_vars = []
        for var in required_vars:
            value = os.getenv(var)
            if not value:
                missing_vars.append(var)
            else:
                env_values[var] = value
                
        if missing_vars:
            raise ValueError(f"缺少必要的环境变量: {', '.join(missing_vars)}")
            
        logger.debug(f"环境变量检查通过: {env_values}")
        return env_values
    
    async def execute(self, arguments: dict) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """执行API请求并处理返回结果"""
        try:
            # 等待服务器初始化完成
            logger.debug("等待服务器初始化...")
            await asyncio.sleep(2)
            
            logger.debug(f"收到请求参数: {arguments}")
            
            if "message" not in arguments:
                return [types.TextContent(
                    type="text",
                    text="错误: 缺少必要参数 'message'"
                )]
                
            # 检查环境变量
            env_vars = self._check_env_variables()
            
            # 准备请求参数
            url = f"{env_vars['MAXKB_HOST']}/api/application/chat_message/{env_vars['MAXKB_CHAT_ID']}"
            headers = {
                "accept": "application/json",
                "AUTHORIZATION": env_vars['MAXKB_AUTHORIZATION'],
                "Content-Type": "application/json"
            }
            data = {
                "message": arguments["message"],
                "re_chat": arguments.get("re_chat", False),
                "stream": arguments.get("stream", True)
            }
            
            logger.debug(f"准备发送请求到: {url}")
            logger.debug(f"请求头: {headers}")
            logger.debug(f"请求数据: {data}")
            
            try:
                # 发送请求
                logger.debug("开始创建HTTP客户端，超时设置为60秒...")
                limits = httpx.Limits(max_keepalive_connections=5, max_connections=10, keepalive_expiry=60.0)
                timeout = httpx.Timeout(
                    timeout=60.0,
                    connect=60.0,
                    read=60.0,
                    write=60.0,
                    pool=60.0
                )
                async with httpx.AsyncClient(
                    timeout=timeout,
                    limits=limits,
                    transport=httpx.AsyncHTTPTransport(
                        retries=1,
                        verify=False,
                        http1=True,
                        http2=False,
                        socket_options=[(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)]
                    )
                ) as client:
                    logger.debug("开始发送POST请求...")
                    try:
                        response = await client.post(url, headers=headers, json=data)
                        logger.debug(f"收到响应状态码: {response.status_code}")
                        logger.debug(f"响应头: {response.headers}")
                        
                        # 处理响应内容
                        content_parts = []
                        last_content = ""
                        received_data = []
                        
                        async for line in response.aiter_lines():
                            logger.debug(f"收到行: {line}")
                            if line.startswith('data: '):
                                try:
                                    # 解析JSON数据
                                    data = json.loads(line[6:])  # 去掉'data: '前缀
                                    logger.debug(f"解析到的数据: {data}")
                                    received_data.append(data)
                                    
                                    # 检查是否有非空的content
                                    if isinstance(data, dict):
                                        current_content = data.get("content", "")
                                        if current_content and current_content != last_content:
                                            last_content = current_content
                                            content_parts.append(current_content)
                                            logger.debug(f"添加新内容: {current_content}")
                                        
                                        # 检查reasoning_content
                                        reasoning_content = data.get("reasoning_content", "")
                                        if reasoning_content and reasoning_content != last_content:
                                            last_content = reasoning_content
                                            content_parts.append(reasoning_content)
                                            logger.debug(f"添加推理内容: {reasoning_content}")
                                            
                                except json.JSONDecodeError as e:
                                    logger.error(f"JSON解析错误: {e}, 行内容: {line}")
                                    continue  # 忽略无法解析的行
                        
                        # 拼接所有内容
                        result = ''.join(content_parts) if content_parts else ""
                        logger.debug(f"最终结果: {result}")
                        
                        if not result:
                            logger.warning("未获取到有效内容")
                            error_details = f"收到 {len(received_data)} 条数据"
                            if received_data:
                                error_details += "\n最后一条数据:\n" + json.dumps(received_data[-1], ensure_ascii=False, indent=2)
                            return [types.TextContent(
                                type="text",
                                text=f"请求错误: {error_details}"
                            )]
                        
                        return [types.TextContent(
                            type="text",
                            text=result
                        )]
                        
                    except httpx.TimeoutException as e:
                        logger.error(f"请求超时: {str(e)}")
                        logger.error(f"超时配置: {client.timeout}")
                        return [types.TextContent(
                            type="text",
                            text=f"请求超时(60秒): {str(e)}"
                        )]
                    except httpx.ConnectError as e:
                        logger.error(f"连接错误: {str(e)}")
                        logger.error(f"目标URL: {url}")
                        return [types.TextContent(
                            type="text",
                            text=f"连接错误({url}): {str(e)}"
                        )]
                    
                    try:
                        response.raise_for_status()
                    except httpx.HTTPStatusError as e:
                        logger.error(f"HTTP状态错误: {str(e)}")
                        logger.error(f"响应状态码: {e.response.status_code}")
                        logger.error(f"响应内容: {e.response.text}")
                        return [types.TextContent(
                            type="text",
                            text=f"HTTP状态错误: {str(e)}"
                        )]
                        
            except httpx.HTTPError as e:
                error_msg = f"HTTP请求错误: {str(e)}\n状态码: {getattr(e.response, 'status_code', 'N/A')}\n响应内容: {getattr(e.response, 'text', 'N/A')}"
                logger.error(error_msg)
                return [types.TextContent(
                    type="text",
                    text=error_msg
                )]
                
        except ValueError as e:
            error_msg = f"配置错误: {str(e)}"
            logger.error(error_msg)
            return [types.TextContent(
                type="text",
                text=error_msg
            )]
        except Exception as e:
            error_msg = f"处理错误: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            return [types.TextContent(
                type="text",
                text=error_msg
            )] 