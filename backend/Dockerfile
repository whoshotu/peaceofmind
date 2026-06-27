# Use the official Python image as a base.
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (optional, for psycopg2)
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Install Python dependencies.
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source.
COPY backend/ ./

EXPOSE 8000

# Run the FastAPI server with Uvicorn.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
