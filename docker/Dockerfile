# DataOps Foundation - Production Docker Image
FROM python:3.11-slim

# Set metadata
LABEL maintainer="DataOps Foundation Team <dataops@company.com>"
LABEL description="Enterprise DataOps platform for modern data engineering"
LABEL version="1.0.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app
ENV DATAOPS_CONFIG_PATH=/app/config/config.yaml
ENV DATAOPS_LOG_LEVEL=INFO

# Create app user (security best practice)
RUN groupadd -r dataops && useradd -r -g dataops dataops

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    unixodbc-dev \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (for better Docker layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/
COPY main.py .
COPY examples/ ./examples/

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/temp /app/backup

# Set proper permissions
RUN chown -R dataops:dataops /app

# Switch to non-root user
USER dataops

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.path.insert(0, '/app/src'); from src.utils.config_manager import ConfigManager; config = ConfigManager(); print('healthy' if config.validate_config()['valid'] else exit(1))"

# Expose port (if web interface is added later)
EXPOSE 8080

# Default command
CMD ["python", "main.py", "--mode", "info"]
