from typing import Dict, Type, List
import mcp.types as types
import os

# 工具基类
class BaseTool:
    """所有工具的基类"""
    name: str = ""
    description: str = ""
    input_schema: dict = {}
    
    @classmethod
    def get_tool_definition(cls) -> types.Tool:
        """获取工具定义"""
        return types.Tool(
            name=cls.name,
            description=cls.description,
            inputSchema=cls.input_schema
        )
    
    async def execute(self, arguments: dict) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """执行工具逻辑，需要在子类中实现"""
        raise NotImplementedError("Tool implementation must override execute method")
    
    def process_file_path(self, file_path: str) -> str:
        """
        处理文件路径，支持挂载目录的转换
        
        如果路径以HOST_MOUNT_SOURCE环境变量开头，则将其转换为容器内的路径
        """
        host_mount_source = os.environ.get('HOST_MOUNT_SOURCE', '')
        host_mount_target = os.environ.get('HOST_MOUNT_TARGET', '/host_files')
        
        # 如果路径以挂载源目录开头，则替换为挂载目标目录
        if host_mount_source and file_path.startswith(host_mount_source):
            return file_path.replace(host_mount_source, host_mount_target, 1)
        
        return file_path


# 工具注册器
class ToolRegistry:
    """工具注册器，用于管理所有可用工具"""
    _tools: Dict[str, Type[BaseTool]] = {}
    
    @classmethod
    def register(cls, tool_class: Type[BaseTool]) -> Type[BaseTool]:
        """注册工具"""
        cls._tools[tool_class.name] = tool_class
        return tool_class
    
    @classmethod
    def get_tool(cls, name: str) -> Type[BaseTool]:
        """获取工具类"""
        if name not in cls._tools:
            raise ValueError(f"Unknown tool: {name}")
        return cls._tools[name]
    
    @classmethod
    def list_tools(cls) -> List[types.Tool]:
        """列出所有可用工具"""
        return [tool_class.get_tool_definition() for tool_class in cls._tools.values()]
    
    @classmethod
    def has_tool(cls, name: str) -> bool:
        """检查工具是否存在"""
        return name in cls._tools 