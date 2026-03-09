# Reproduction Dockerfile to test Gemini installation
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install gemini-cli
RUN curl -L https://gemini.google.com/cli/install.sh | bash

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install fastapi uvicorn requests python-dotenv python-multipart redis # Core dependencies

# Copy the application code
COPY bin/ ./bin/
COPY core/ ./core/
COPY data/ ./data/
COPY .env .

# Expose the API port
EXPOSE 8000

CMD ["python", "bin/api_gateway.py"]
