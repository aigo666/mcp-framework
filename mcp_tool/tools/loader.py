"""
工具加载器模块，用于自动加载所有已注册的工具
"""
import importlib
import pkgutil
import inspect
import os
import sys
from typing import List, Type
from . import BaseTool, ToolRegistry

def load_tools() -> List[Type[BaseTool]]:
    """
    自动加载tools目录下的所有工具模块
    
    Returns:
        List[Type[BaseTool]]: 已加载的工具类列表
    """
    # 获取当前模块的路径
    package_path = os.path.dirname(__file__)
    
    # 获取所有子模块
    for _, name, is_pkg in pkgutil.iter_modules([package_path]):
        # 跳过__init__.py和loader.py
        if name in ['__init__', 'loader']:
            continue
        
        # 导入模块
        module_name = f"{__package__}.{name}"
        try:
            importlib.import_module(module_name)
        except ImportError as e:
            print(f"Warning: Failed to import module {module_name}: {e}")
    
    # 收集所有已注册的工具类
    tools = list(ToolRegistry._tools.values())
    
    return tools

def get_tool_instances() -> dict:
    """
    创建所有工具类的实例
    
    Returns:
        dict: 工具名称到工具实例的映射
    """
    tools = load_tools()
    tool_instances = {}
    
    for tool_class in tools:
        try:
            tool_instance = tool_class()
            tool_instances[tool_class.name] = tool_instance
        except Exception as e:
            print(f"Warning: Failed to instantiate tool {tool_class.name}: {e}")
    
    return tool_instances 