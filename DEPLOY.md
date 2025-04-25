# MCP框架本地Docker部署指南

本指南将帮助您使用Docker在本地部署支持图片处理的MCP服务器。

## 先决条件

- 已安装Docker和Docker Compose
- 基本的命令行操作知识

## 部署步骤

### 1. 准备环境变量文件

创建一个名为`.env`的文件在项目根目录中，内容如下：

```
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
# Mac/Linux示例: HOST_MOUNT_SOURCE=/Users/username/Documents
# Windows示例: HOST_MOUNT_SOURCE=C:/Users/username/Documents
HOST_MOUNT_SOURCE=/tmp
HOST_MOUNT_TARGET=/host_files
```

请根据您的实际情况修改`HOST_MOUNT_SOURCE`，指向您希望MCP服务器能够访问的本地目录。

### 2. 构建并启动Docker容器

在项目根目录中，运行以下命令：

```bash
# 构建Docker镜像并启动容器
docker-compose up -d
```

此命令会构建Docker镜像并在后台启动容器。

### 3. 验证服务是否正常运行

```bash
# 查看容器日志
docker-compose logs -f
```

如果看到如下类似输出，说明服务已成功启动：

```
mcp-server    | INFO:     Started server process [1]
mcp-server    | INFO:     Waiting for application startup.
mcp-server    | INFO:     Application startup complete.
mcp-server    | INFO:     Uvicorn running on http://0.0.0.0:8000
```

您也可以通过访问`http://localhost:8000/sse`验证服务是否正常运行。

### 4. 配置Claude或Cursor使用MCP服务器

#### 在Claude Desktop中配置

1. 打开Claude Desktop应用
2. 点击左下角头像，选择"Settings..."
3. 点击左侧"Developer"
4. 点击"Edit Config"
5. 输入以下配置：

```json
{
  "mcpServers": {
    "custom-mcp": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

#### 在Cursor中配置

1. 在Cursor中打开命令面板（Ctrl+Shift+P或Cmd+Shift+P）
2. 输入"MCP"并选择"MCP: Configure MCP Server"
3. 选择"Add New Server"
4. 选择"SSE Server"类型
5. 输入URL: `http://localhost:8000/sse`
6. 输入名称，如"custom-mcp"

### 5. 测试文件处理和图片支持

在Claude Desktop或Cursor中，尝试以下操作：

- 解析PDF文件：`请解析这个PDF文档：/path/to/your/document.pdf`
- 解析Word文档：`请解析这个Word文档：/path/to/your/document.docx`

如果一切正常，您应该能够看到文档内容以及其中包含的图片。

## 管理Docker容器

```bash
# 停止服务
docker-compose down

# 查看容器状态
docker-compose ps

# 重启服务
docker-compose restart
```

## 常见问题排查

### 1. 无法访问主机文件

确保您在`.env`文件中正确设置了`HOST_MOUNT_SOURCE`，指向您需要访问的目录。

### 2. 图片无法显示

检查服务器日志是否有错误信息。可能是Tesseract OCR依赖问题，可以尝试手动进入容器安装：

```bash
docker exec -it mcp-framework_mcp-server_1 bash
apt-get update && apt-get install -y tesseract-ocr tesseract-ocr-chi-sim tesseract-ocr-eng
```

### 3. MCP服务器无法启动

检查端口是否被占用：

```bash
lsof -i :8000
```

如果端口被占用，可以在`.env`文件中修改`MCP_SERVER_PORT`为其他值。 