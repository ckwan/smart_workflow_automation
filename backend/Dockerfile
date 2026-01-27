# Use official Python image
FROM python:3.11

# Set working directory
WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code
COPY . .

ENV PYTHONPATH=/app

# Expose the port
EXPOSE 8002
