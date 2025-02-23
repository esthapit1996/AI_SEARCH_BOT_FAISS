# Build stage (using python:3.12-slim)
FROM python:3.12-slim as build

WORKDIR /app
COPY requirements.txt .

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends libmagic1 && \
    pip install --no-cache-dir -r requirements.txt && \
    rm -rf /var/lib/apt/lists/*


# Final stage (runtime stage using python:3.12-slim)
FROM python:3.12-slim

WORKDIR /app

# Copy only the necessary files from the build stage
COPY --from=build /app /app

# Clean up unnecessary files (e.g., build dependencies)
RUN rm -rf /root/.cache/pip /var/lib/apt/lists/*

# Copy application files
COPY *.py .
COPY .env .
COPY spaces.txt .

EXPOSE 5000
CMD ["python", "platform-ai-searchbot.py"]
