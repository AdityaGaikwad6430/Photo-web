# Stage 1 - Build dependencies
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2 - Final runtime image
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY . .
USER appuser
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]


