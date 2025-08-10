#!/bin/bash
set -e

if [ -z "$OPENAI_API_KEY" ]; then
  echo "错误：请设置环境变量 OPENAI_API_KEY"
  exit 1
fi

echo "开始构建镜像 metagpt-step4..."
docker build -t metagpt-step4 .

echo "停止旧容器（如果存在）..."
docker stop metagpt-container || true
docker rm metagpt-container || true

echo "启动新容器..."
docker run -d --name metagpt-container -p 5001:5000 -e OPENAI_API_KEY="$OPENAI_API_KEY" metagpt-step4

echo "部署完成！访问地址：http://localhost:5001"