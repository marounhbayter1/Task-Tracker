# syntax=docker/dockerfile:1

# ---- Build stage: install Python dependencies ----
FROM python:3.11-slim AS builder

WORKDIR /build

COPY requirements.txt .

RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- Runtime stage: minimal image with app code only ----
FROM python:3.11-slim AS runtime

WORKDIR /app

# Non-root user for running the app
RUN useradd --create-home --shell /usr/sbin/nologin app

# Dependencies installed in the build stage
COPY --from=builder /install /usr/local

# Application code only (no tests, frontend, docs, or env files)
COPY app ./app

RUN chown -R app:app /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

USER app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
