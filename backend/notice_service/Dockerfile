FROM python:3.11-slim-bullseye

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app:$PYTHONPATH \  
    DJANGO_SETTINGS_MODULE=service.settings \
    PORT=8000

# 设置工作目录
WORKDIR /app

# 使用阿里云镜像源加速安装
RUN sed -i 's|http://deb.debian.org/debian|https://mirrors.aliyun.com/debian|g' /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        default-libmysqlclient-dev \
        pkg-config \
        curl \
        netcat && \
    rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
#  -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制整个项目
COPY . .

# 创建必要的目录
RUN mkdir -p /app/media /app/static

# 设置 Python 路径（在安装依赖后）
ENV PYTHONPATH=/app:$PYTHONPATH

# 暴露端口
EXPOSE $PORT

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s \
    CMD curl -f http://localhost:$PORT/healthcheck/ || exit 1

# 启动命令
CMD ["sh", "-c", "python manage.py migrate && gunicorn service.wsgi:application --bind 0.0.0.0:${PORT:-8000}"]