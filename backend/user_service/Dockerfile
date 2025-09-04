# Materials Service Dockerfile
# - Uses Python slim image
# - Installs build deps for mysqlclient
# - Installs Python deps
# - Runs migrations then starts Django server

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

     # 更换为阿里云 Debian 源，加速依赖安装（适配slim镜像）
     RUN sed -i 's|http://deb.debian.org/debian|https://mirrors.aliyun.com/debian|g' /etc/apt/sources.list.d/debian.sources \
      && apt-get update \
      && apt-get install -y --no-install-recommends \
          build-essential \
          default-libmysqlclient-dev \
          pkg-config \
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

EXPOSE 8000

# Start: run migrations then app; PORT can be overridden via env
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:${PORT:-8000}"]
