# Use a small but recent python base
FROM python:3.12-slim

# Prevent Python from writing pyc files and enable stdout/stderr buffering
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system deps for cryptography and MySQL client
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libssl-dev libffi-dev default-libmysqlclient-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create a simple non-root user (optional but safer)
RUN useradd -m appuser || true
USER appuser

EXPOSE 5000

# Use Gunicorn for production. Workers + bind to port 5000.
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app", "--timeout", "120"]
