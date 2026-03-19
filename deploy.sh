#!/bin/bash
# DictationPro v8.0 生产环境部署脚本
# 使用方式：./deploy.sh

set -e

echo "🚀 DictationPro v8.0 部署开始..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 项目路径
PROJECT_DIR="/Users/airisagentswarm/.openclaw/workspace/dictation-pro-web"
BACKEND_DIR="$PROJECT_DIR/backend"
VENV_DIR="$PROJECT_DIR/../.venv"

# 进入项目目录
cd "$PROJECT_DIR"

echo "📁 项目目录：$PROJECT_DIR"

# Step 1: 检查 Python 环境
echo -e "\n${YELLOW}Step 1: 检查 Python 环境${NC}"
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${RED}✗ 虚拟环境不存在${NC}"
    echo "创建虚拟环境..."
    python3 -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"
echo -e "${GREEN}✓ 虚拟环境已激活${NC}"

# Step 2: 安装依赖
echo -e "\n${YELLOW}Step 2: 安装依赖${NC}"
cd "$BACKEND_DIR"
if [ -f "requirements.txt" ]; then
    uv pip install -q -r requirements.txt
    echo -e "${GREEN}✓ 依赖已安装${NC}"
else
    echo -e "${RED}✗ requirements.txt 不存在${NC}"
    exit 1
fi

# Step 3: 检查配置文件
echo -e "\n${YELLOW}Step 3: 检查配置文件${NC}"
if [ ! -f ".env" ]; then
    echo "创建 .env 配置文件..."
    cat > .env << EOF
# DictationPro 环境配置
PORT=3000

# Azure TTS（可选）
AZURE_TTS_KEY=
AZURE_TTS_REGION=eastus

# AI 绘画（可选）
NANOBANANA_API_KEY=
NANOBANANA_URL=https://api.nanobanana.pro/v1

# 通义千问（可选）
DASHSCOPE_API_KEY=

# 飞书 API（可选）
FEISHU_APP_ID=
FEISHU_APP_SECRET=
FEISHU_APP_TOKEN=IA4ZbHqLuaD5fZsz4ctc8TeKnBd
FEISHU_TABLE_ID=tblqzJCZQHEanMZZ
EOF
    echo -e "${YELLOW}⚠️  请编辑 .env 文件配置 API 密钥${NC}"
else
    echo -e "${GREEN}✓ .env 已存在${NC}"
fi

# Step 4: 停止旧服务
echo -e "\n${YELLOW}Step 4: 停止旧服务${NC}"
pkill -f "python.*server.py" 2>/dev/null || true
echo -e "${GREEN}✓ 旧服务已停止${NC}"

# Step 5: 启动新服务
echo -e "\n${YELLOW}Step 5: 启动新服务${NC}"
cd "$BACKEND_DIR"
nohup python server.py > server.log 2>&1 &
SERVER_PID=$!
echo "服务进程 ID: $SERVER_PID"

# 等待服务启动
sleep 3

# Step 6: 验证服务
echo -e "\n${YELLOW}Step 6: 验证服务${NC}"
if curl -s http://localhost:3000/api/health | grep -q "ok"; then
    echo -e "${GREEN}✓ 服务启动成功${NC}"
    echo ""
    echo "======================================"
    echo -e "${GREEN}🎉 部署完成！${NC}"
    echo "======================================"
    echo ""
    echo "访问地址:"
    echo "  学生端：http://localhost:3000/student-v8.html"
    echo "  教师端：http://localhost:3000/teacher-v8-full.html"
    echo "  AI 记忆：http://localhost:3000/ai-memory.html"
    echo ""
    echo "服务日志：tail -f $BACKEND_DIR/server.log"
    echo "停止服务：pkill -f 'python.*server.py'"
    echo ""
else
    echo -e "${RED}✗ 服务启动失败${NC}"
    echo "查看日志：tail $BACKEND_DIR/server.log"
    exit 1
fi
