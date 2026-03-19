#!/bin/bash
# DictationPro AI - 快速启动脚本

echo "🚀 启动 DictationPro AI 后端服务..."

cd "$(dirname "$0")/backend"

# 激活虚拟环境
source ~/.openclaw/workspace/.venv/bin/activate

# 启动服务
python server.py
