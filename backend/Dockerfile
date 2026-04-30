# syntax=docker/dockerfile:1

FROM python:3.12-slim

# ---------- Environment ----------
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ---------- Working directory ----------
WORKDIR /app

# ---------- System dependencies ----------
RUN apt-get update && apt-get install -y curl --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# ---------- Install Python dependencies ----------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---------- Create non-root user ----------
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# ---------- Copy application code ----------
COPY --chown=appuser:appgroup . .

#----------- Grant directory Permissions -----------
RUN chown -R appuser:appgroup /app

# Optional: create writable directory for exports (if your worker writes files)
RUN mkdir -p /data/exports && chown -R appuser:appgroup /data

# ---------- Switch to non-root user ----------
USER appuser

# ---------- Expose port ----------
EXPOSE 8000

# ---------- Default command (API) ----------
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
