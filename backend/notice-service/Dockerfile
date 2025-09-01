# 第一阶段：构建环境
FROM python:3.9-slim as builder

WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_DISABLE_PIP_VERSION_CHECK=on

# 安装系统依赖和构建工具
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制并安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# 第二阶段：生产环境
FROM python:3.9-slim

WORKDIR /app

# 从构建阶段复制 Python 依赖
COPY --from=builder /root/.local /root/.local
COPY --from=builder /app /app

# 确保使用的 Python 版本一致
RUN python --version

# 安装运行所需的系统依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PATH="/root/.local/bin:${PATH}"
ENV PORT 8000
ENV GUNICORN_CMD_ARGS "--timeout 120 --workers 4 --threads 2 --max-requests 1000 --max-requests-jitter 50 --capture-output --access-logfile - --error-logfile -"

# 添加健康检查脚本
COPY health_check.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/health_check.sh

# 创建日志目录
RUN mkdir -p /app/logs && chown nobody /app/logs

# 设置非root用户运行
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# 复制应用代码
COPY --chown=appuser:appuser . .

# 收集静态文件（在非root用户下执行）
RUN python manage.py collectstatic --noinput

# 暴露端口
EXPOSE $PORT

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=10s --retries=3 \
    CMD health_check.sh

# 启动命令
CMD ["gunicorn", "notice_project.wsgi:application", "--bind", "0.0.0.0:${PORT}", "--worker-class", "gthread"]