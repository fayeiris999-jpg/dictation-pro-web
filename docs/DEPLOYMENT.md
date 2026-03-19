# DictationPro 部署文档

**版本:** v8.0  
**最后更新:** 2026-03-18  
**适用环境:** macOS / Linux

---

## 📋 目录

- [系统要求](#系统要求)
- [快速部署](#快速部署)
- [详细部署步骤](#详细部署步骤)
- [环境配置](#环境配置)
- [生产环境部署](#生产环境部署)
- [故障排查](#故障排查)

---

## 系统要求

### 最低配置
- **操作系统:** macOS 10.15+ / Ubuntu 18.04+
- **Python:** 3.9+
- **内存:** 2GB RAM
- **磁盘:** 500MB 可用空间

### 推荐配置
- **操作系统:** macOS 12+ / Ubuntu 20.04+
- **Python:** 3.12+
- **内存:** 4GB RAM
- **磁盘:** 2GB 可用空间

### 依赖服务（可选）
- **Azure TTS:** 语音合成服务
- **飞书 API:** 数据同步
- **NanoBanana:** AI 绘画服务

---

## 快速部署

### 一键启动（开发环境）

```bash
# 1. 进入项目目录
cd /Users/airisagentswarm/.openclaw/workspace/dictation-pro-web

# 2. 启动服务
./start.sh

# 3. 访问服务
# 学生端：http://localhost:3000/student-v8.html
# 教师端：http://localhost:3000/teacher-v8-full.html
# AI 记忆：http://localhost:3000/ai-memory.html
```

---

## 详细部署步骤

### Step 1: 克隆项目

```bash
# 如果项目已存在，跳过此步
cd /Users/airisagentswarm/.openclaw/workspace
```

### Step 2: 创建虚拟环境

```bash
# 进入后端目录
cd dictation-pro-web/backend

# 创建虚拟环境（使用 uv）
source ~/.openclaw/workspace/.venv/bin/activate

# 或使用 venv
python3 -m venv venv
source venv/bin/activate
```

### Step 3: 安装依赖

```bash
# 使用 uv 安装（推荐）
uv pip install python-dotenv requests python-docx pdfminer.six pytesseract pillow xlsxwriter reportlab

# 或使用 pip 安装
pip install python-dotenv requests python-docx pdfminer.six pytesseract pillow xlsxwriter reportlab
```

### Step 4: 配置环境变量

```bash
# 复制环境配置模板
cp .env.example .env

# 编辑 .env 文件
nano .env
# 或
vim .env
```

### Step 5: 启动服务

```bash
# 启动后端服务
python server.py

# 后台运行（生产环境）
nohup python server.py > server.log 2>&1 &

# 或使用 screen
screen -S dictationpro
python server.py
# Ctrl+A, D 脱离 screen
```

### Step 6: 验证部署

```bash
# 检查服务状态
curl http://localhost:3000/api/health

# 预期输出
# {"status": "ok", "timestamp": "...", "services": {...}}
```

---

## 环境配置

### .env 文件说明

```bash
# ========== 服务配置 ==========
PORT=3000

# ========== Azure TTS（可选） ==========
# 未配置时使用模拟音频
AZURE_TTS_KEY=your_azure_key
AZURE_TTS_REGION=eastus

# ========== AI 绘画（可选） ==========
# 未配置时使用占位图
NANOBANANA_API_KEY=sk-xxx
NANOBANANA_URL=https://api.nanobanana.pro/v1

# ========== 通义千问（可选） ==========
# 未配置时使用预定义模板
DASHSCOPE_API_KEY=sk-xxx

# ========== 飞书 API（可选） ==========
# 未配置时模拟同步
FEISHU_APP_ID=cli_xxx
FEISHU_APP_SECRET=xxx
FEISHU_APP_TOKEN=IA4ZbHqLuaD5fZsz4ctc8TeKnBd
FEISHU_TABLE_ID=tblqzJCZQHEanMZZ
```

### 获取 API Key

#### Azure TTS
1. 访问 [Azure Portal](https://portal.azure.com)
2. 创建 Speech Service
3. 获取 Key 和 Region

#### 通义千问
1. 访问 [DashScope](https://dashscope.console.aliyun.com)
2. 创建 API Key

#### NanoBanana
1. 访问 [NanoBanana](https://nanobanana.pro)
2. 获取 API Key

#### 飞书 API
1. 访问 [飞书开放平台](https://open.feishu.cn)
2. 创建应用
3. 获取 App ID 和 Secret
4. 授权多维表格权限

---

## 生产环境部署

### 使用 Gunicorn（推荐）

```bash
# 安装 Gunicorn
pip install gunicorn

# 启动服务
gunicorn -w 4 -b 0.0.0.0:3000 server:app

# 后台运行
nohup gunicorn -w 4 -b 0.0.0.0:3000 server:app > server.log 2>&1 &
```

### 使用 systemd（Linux）

```bash
# 创建服务文件
sudo nano /etc/systemd/system/dictationpro.service
```

**dictationpro.service:**
```ini
[Unit]
Description=DictationPro Backend Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/dictation-pro-web/backend
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn -w 4 -b 0.0.0.0:3000 server:app
Restart=always

[Install]
WantedBy=multi-user.target
```

**启动服务:**
```bash
# 重载 systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start dictationpro

# 设置开机自启
sudo systemctl enable dictationpro

# 查看状态
sudo systemctl status dictationpro

# 查看日志
sudo journalctl -u dictationpro -f
```

### 使用 Nginx 反向代理

```nginx
server {
    listen 80;
    server_name dictationpro.example.com;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static {
        alias /path/to/dictation-pro-web/backend/public;
        expires 30d;
    }
}
```

### 使用 Docker（推荐）

**Dockerfile:**
```dockerfile
FROM python:3.12-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-chi-sim \
    tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 暴露端口
EXPOSE 3000

# 启动命令
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:3000", "server:app"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  dictationpro:
    build: .
    ports:
      - "3000:3000"
    environment:
      - PORT=3000
      - AZURE_TTS_KEY=${AZURE_TTS_KEY}
      - NANOBANANA_API_KEY=${NANOBANANA_API_KEY}
      - DASHSCOPE_API_KEY=${DASHSCOPE_API_KEY}
      - FEISHU_APP_ID=${FEISHU_APP_ID}
      - FEISHU_APP_SECRET=${FEISHU_APP_SECRET}
    volumes:
      - ./data:/app/backend/data
    restart: always
```

**启动:**
```bash
docker-compose up -d
```

---

## 故障排查

### 问题 1: 服务无法启动

**症状:**
```
Error: Address already in use
```

**解决方案:**
```bash
# 查找占用端口的进程
lsof -i :3000

# 杀死进程
kill -9 <PID>

# 或修改端口
PORT=3001 python server.py
```

---

### 问题 2: 依赖安装失败

**症状:**
```
ERROR: Could not find a version that satisfies the requirement xxx
```

**解决方案:**
```bash
# 升级 pip
pip install --upgrade pip

# 使用 uv（推荐）
uv pip install <package>

# 或使用国内镜像
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple <package>
```

---

### 问题 3: OCR 无法识别中文

**症状:**
```
TesseractNotFoundError: tesseract is not installed
```

**解决方案:**
```bash
# macOS
brew install tesseract
brew install tesseract-lang

# Ubuntu
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-chi-sim

# 验证安装
tesseract --version
```

---

### 问题 4: PDF 导出失败

**症状:**
```
ImportError: No module named 'reportlab'
```

**解决方案:**
```bash
# 安装 reportlab
pip install reportlab

# 安装中文字体（可选）
# macOS 系统自带宋体，无需额外安装
```

---

### 问题 5: 飞书同步失败

**症状:**
```
Feishu API error: 234008
```

**解决方案:**
1. 检查飞书应用权限
2. 确保有多维表格写入权限
3. 检查 App Token 和 Table ID 是否正确

---

### 问题 6: AI 生成超时

**症状:**
```
TimeoutError: Request timed out
```

**解决方案:**
```bash
# 检查网络连接
ping api.nanobanana.pro

# 检查 API Key 是否有效
curl -H "Authorization: Bearer YOUR_KEY" https://api.nanobanana.pro/v1/models

# 增加超时时间（修改代码）
timeout=60
```

---

### 问题 7: 数据丢失

**症状:**
```
JSON 文件为空或损坏
```

**解决方案:**
```bash
# 备份数据
cp backend/data/scores.json backend/data/scores.json.bak

# 恢复数据
cp backend/data/scores.json.bak backend/data/scores.json

# 定期备份（crontab）
0 2 * * * cp /path/to/data/*.json /path/to/backup/
```

---

## 性能优化

### 数据库优化

当前使用 JSON 文件存储，适合小规模使用。

**数据量 > 10000 条时建议迁移到数据库:**

```bash
# 安装 SQLite（Python 自带）
# 或安装 PostgreSQL
pip install psycopg2-binary

# 修改后端代码使用数据库
# 参考：backend/stats.py 中的数据存储逻辑
```

### 缓存优化

```bash
# 安装 Redis
brew install redis  # macOS
sudo apt-get install redis-server  # Ubuntu

# 启动 Redis
redis-server

# 修改代码添加缓存
import redis
r = redis.Redis(host='localhost', port=6379)
```

### 并发优化

```bash
# 使用 Gunicorn 多 worker
gunicorn -w 4 -b 0.0.0.0:3000 server:app

# worker 数量建议：2-4 × CPU 核心数
```

---

## 监控与日志

### 日志配置

```python
# 在 server.py 中添加日志
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('server.log'),
        logging.StreamHandler()
    ]
)
```

### 健康检查

```bash
# 定期检查服务状态
curl http://localhost:3000/api/health

# 添加到 crontab
*/5 * * * * curl -s http://localhost:3000/api/health > /dev/null || echo "Service down!" | mail -s "Alert" admin@example.com
```

---

## 备份策略

### 数据备份

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/path/to/backup/$DATE"

mkdir -p $BACKUP_DIR

# 备份数据
cp backend/data/*.json $BACKUP_DIR/

# 备份配置
cp backend/.env $BACKUP_DIR/

# 压缩
tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR

# 删除旧备份（保留 30 天）
find /path/to/backup -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_DIR.tar.gz"
```

**添加到 crontab:**
```bash
0 3 * * * /path/to/backup.sh
```

---

## 升级指南

### 从 v7 升级到 v8

```bash
# 1. 备份数据
cp -r backend/data backend/data.bak

# 2. 拉取新代码
git pull origin main

# 3. 安装新依赖
pip install -r requirements.txt

# 4. 重启服务
pkill -f "python.*server.py"
python server.py

# 5. 验证
curl http://localhost:3000/api/health
```

---

## 技术支持

**文档:** `/Users/airisagentswarm/.openclaw/workspace/dictation-pro-web/docs/`  
**API 文档:** `/Users/airisagentswarm/.openclaw/workspace/dictation-pro-web/docs/API.md`  
**产品审查:** `/Users/airisagentswarm/.openclaw/workspace/dictation-pro-web/PRODUCT_REVIEW.md`

**联系方式:**
- 产品负责人：Usa ⚡️
- 邮箱：hello@dictationpro.ai

---

*最后更新：2026-03-18*  
*版本：v8.0*  
*维护者：Usa ⚡️*
