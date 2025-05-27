# Use an official Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY backend/requirements.txt .
# RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
# RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY backend/ .

# Expose the FastAPI default port
EXPOSE 7000

# Run the FastAPI app
CMD ["python", "app/main.py"]
