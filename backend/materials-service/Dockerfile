# Materials Service Dockerfile
# - Uses Python slim image
# - Installs build deps for mysqlclient
# - Installs Python deps
# - Runs migrations then starts Django server

FROM python:3.11-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# 设置 Python 路径
ENV PYTHONPATH=/app:$PYTHONPATH

# System deps for mysqlclient
# RUN apt-get update \
#  && apt-get install -y --no-install-recommends \
#     build-essential \
#     default-libmysqlclient-dev \
#     pkg-config \
#  && rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps first for better cache
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

# Ensure media/static directories exist (can be mounted as volumes)
RUN mkdir -p /app/media /app/static

ENV DJANGO_SETTINGS_MODULE=server.settings \
    PORT=8000

ENV PYTHONUNBUFFERED 1

EXPOSE 8000

# Start: run migrations then app; PORT can be overridden via env
CMD ["gunicorn", "materials_service.wsgi:application", "--bind", "0.0.0.0:8000"]