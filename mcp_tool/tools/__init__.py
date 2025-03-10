from typing import Dict, Type, List
import mcp.types as types

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