#!/bin/bash

# 健康检查脚本
# 检查数据库连接和核心API访问

set -eo pipefail

# 检查数据库连接
python manage.py check --database default > /dev/null 2>&1 || exit 1

# 检查核心API端点
curl -sSfL --retry 3 --max-time 5 http://localhost:$PORT/health/ > /dev/null 2>&1 || exit 1

# 检查就绪端点
curl -sSfL --retry 3 --max-time 5 http://localhost:$PORT/ready/ > /dev/null 2>&1 || exit 1

exit 0