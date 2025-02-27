FROM ubuntu:22.04

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    && rm -rf /var/lib/apt/lists/*
# Copy application files

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY *.py .env spaces.txt ./

# Expose port
EXPOSE 5000

# Run the application
CMD ["python3", "platform-ai-searchbot.py"]
