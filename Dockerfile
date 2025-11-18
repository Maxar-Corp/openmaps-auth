FROM smallstep/step-cli:latest AS stepcli


FROM python:3.10-slim AS builder

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# System dependencies needed to build Python packages (psycopg2, cryptography, gevent, etc.)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .



# Runtime image
FROM python:3.10-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=openmaps_auth.settings.prod \
    PORT=8000

WORKDIR /app

# Minimal runtime system dependencies (PostgreSQL client libs for psycopg2-binary)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Install Smallstep CLI from official step-cli image
COPY --from=stepcli /usr/local/bin/step /usr/bin/step

# Copy installed Python packages and application code from the builder image
COPY --from=builder /usr/local/lib/python3.10 /usr/local/lib/python3.10
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app

# Create non-root user
RUN addgroup --system openmaps \
    && adduser --system --ingroup openmaps openmaps \
    && chown -R openmaps:openmaps /app

USER openmaps

EXPOSE 8000

# Gunicorn with gevent workers; DB migrations should be run via a separate Job, not here
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--worker-class", "gevent", "openmaps_auth.wsgi:application"]

