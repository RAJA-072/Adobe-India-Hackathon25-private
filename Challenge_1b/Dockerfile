FROM --platform=linux/amd64 python:3.10-slim

# Set environment variables for optimal performance
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Create input and output directories
RUN mkdir -p /app/input /app/output

# Install system dependencies and Python packages in single layer
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && pip install --no-cache-dir pymupdf==1.23.24

# Copy the processing script
COPY process_collections.py .

# Copy collection data to input directory by default (can be overridden by volume mount)
COPY ["Collection 1", "./input/Collection 1"]
COPY ["Collection 2", "./input/Collection 2"] 
COPY ["Collection 3", "./input/Collection 3"]

# Run the script
CMD ["python", "process_collections.py"]
