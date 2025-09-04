FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 为 mysqlclient / psycopg2 提供编译依赖（可按需裁剪）
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libpq-dev default-libmysqlclient-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt ./
RUN python -m pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# =============== 测试阶段：构建即运行单元测试（失败则构建失败） ===============
FROM base AS test
COPY . .
ENV DJANGO_SETTINGS_MODULE=server.settings_test
RUN python manage.py test -v 2

# =============== 运行阶段 ===============
FROM base AS runtime
COPY . .
ENV DJANGO_SETTINGS_MODULE=server.settings
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
