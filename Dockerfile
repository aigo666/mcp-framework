# Use Python 3.10 slim image as base
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install build dependencies and curl for healthcheck
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Install the package in editable mode with proper path
RUN pip install --no-cache-dir -e .

# Expose the port
EXPOSE 8000

# Run the server with SSE transport
CMD ["python", "-m", "mcp_tool", "--transport", "sse", "--port", "8000"] 