#!/bin/bash
echo "🔧 设置本地K8s环境..."

# 1. 创建镜像拉取密钥
echo "请输入GitHub Personal Access Token (需要packages:read权限):"
read -s github_token

kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=YOUR_GITHUB_USERNAME \
  --docker-password="$github_token" \
  --namespace=default

# 2. 确保Ingress控制器已安装
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml

echo "✅ 本地环境设置完成！"