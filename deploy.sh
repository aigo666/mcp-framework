#!/bin/bash

# 显示彩色输出的函数
print_green() {
    echo -e "\033[0;32m$1\033[0m"
}

print_yellow() {
    echo -e "\033[0;33m$1\033[0m"
}

print_red() {
    echo -e "\033[0;31m$1\033[0m"
}

# 检查Docker是否已安装
if ! [ -x "$(command -v docker)" ]; then
    print_red "错误: Docker未安装。请先安装Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# 检查Docker Compose是否已安装
if ! [ -x "$(command -v docker-compose)" ]; then
    print_red "错误: Docker Compose未安装。请先安装Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

# 检查是否存在.env文件，如果不存在则创建
if [ ! -f .env ]; then
    print_yellow "未找到.env文件，正在创建默认配置..."
    cat > .env << EOL
# MCP服务器配置
MCP_SERVER_PORT=8000
MCP_SERVER_HOST=0.0.0.0
DEBUG=true

# MaxKB配置（可选，如果不使用可以留空）
MAXKB_HOST=http://host.docker.internal:8080
MAXKB_CHAT_ID=
MAXKB_APPLICATION_ID=
MAXKB_AUTHORIZATION=

# 本地文件挂载配置
# 修改HOST_MOUNT_SOURCE为您需要让MCP服务器访问的本地目录路径
HOST_MOUNT_SOURCE=/tmp
HOST_MOUNT_TARGET=/host_files
EOL
    print_green ".env文件已创建，请根据需要修改配置。"
    
    # 提示用户设置HOST_MOUNT_SOURCE
    print_yellow "提示: 您可能需要编辑.env文件，设置HOST_MOUNT_SOURCE为您希望MCP服务器能够访问的目录。"
    print_yellow "例如: Mac/Linux用户可设置为 HOST_MOUNT_SOURCE=/Users/username/Documents"
    print_yellow "     Windows用户可设置为 HOST_MOUNT_SOURCE=C:/Users/username/Documents"
fi

# 构建并启动Docker容器
print_green "正在构建并启动MCP服务器..."
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# 检查服务是否成功启动
sleep 5
if [ "$(docker-compose ps -q mcp-server)" ]; then
    if [ "$(docker inspect --format='{{.State.Running}}' $(docker-compose ps -q mcp-server))" = "true" ]; then
        print_green "MCP服务器已成功启动！"
        print_green "服务地址: http://localhost:$(grep MCP_SERVER_PORT .env | cut -d '=' -f2)/sse"
        print_green "您现在可以在Claude Desktop或Cursor中配置MCP服务器。"
        print_green "查看DEPLOY.md了解详细配置步骤。"
    else
        print_red "MCP服务器启动失败，请检查日志:"
        print_yellow "docker-compose logs -f"
    fi
else
    print_red "MCP服务器启动失败，请检查日志:"
    print_yellow "docker-compose logs -f"
fi 