# =========================================
# STAGE 1: BUILD
# Install dependencies in a full image
# =========================================
FROM python:3.11-slim AS builder

WORKDIR /app

# Copy requirements first (Docker caches this layer)
# If requirements.txt hasn't changed, this layer is reused
COPY requirements.txt .

# Install dependencies into a local folder
# --no-cache-dir = don't store pip cache (saves space)
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# =========================================
# STAGE 2: RUNTIME
# Tiny final image — only what's needed
# =========================================
FROM python:3.11-alpine

WORKDIR /app

# Copy installed packages from Stage 1
COPY --from=builder /install /usr/local

# Copy only the app source code
COPY app.py .

# Don't run as root — security best practice
RUN adduser -D appuser
USER appuser

EXPOSE 8080

# gunicorn = production-grade server (better than flask dev server)
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "app:app"]