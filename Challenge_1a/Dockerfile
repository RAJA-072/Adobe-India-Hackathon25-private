FROM --platform=linux/amd64 python:3.10-slim

# Set environment variables for optimal performance
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Create directories, install dependencies, and setup in single layer for optimal image size
RUN mkdir -p /app/input /app/output && \
    apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && pip install --no-cache-dir pymupdf==1.23.24

# Copy the processing script
COPY process_pdfs.py .

# Copy sample data as fallback (if no volume mounted)
COPY sample_dataset/pdfs ./input/

# Run the script
CMD ["python", "process_pdfs.py"] 