# GitHub Repository Enhancement Bot
# Professional Docker container for repository automation

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Configure Git
RUN git config --global user.name "GitHub Enhancement Bot" && \
    git config --global user.email "bot@codepulse.dev"

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Make bot executable
RUN chmod +x bot.py

# Create non-root user for security
RUN useradd -m -u 1000 botuser && \
    chown -R botuser:botuser /app
USER botuser

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import bot; print('Bot is healthy')" || exit 1

# Default command
ENTRYPOINT ["python", "bot.py"]
CMD ["--help"]