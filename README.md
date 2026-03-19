# DictationPro AI Web v6.0 ⚡️

> **智能听写系统网页版 | AI-Powered Dictation System**

让听写从 30 分钟缩短到 5 分钟，自动批改、自动登记、自动同步。

---

## 🎯 v6.0 新功能

| 功能 | 描述 | 状态 |
|------|------|------|
| **🎨 学生端 v6** | 三标签页、成绩趋势图、错题本、一键导出 | ✅ 完成 |
| **🎨 教师端 v6** | 班级统计、学生排名、分数分布图、创建听写 | ✅ 完成 |
| **📊 Chart.js 集成** | 折线图/饼图/柱状图，4 种统计图表 | ✅ 完成 |
| **🔐 用户登录系统** | JWT Token 认证，教师/学生角色区分 | ✅ 完成 |
| **📥 错题本导出** | PDF/Excel格式，含统计分析 + 学习建议 | ✅ 完成 |
| **🎵 音频生成 API** | 后端集成 Azure TTS，支持 SSML 控制 | ✅ 完成 |
| **✅ 自动批改 API** | 编辑距离算法，支持容错处理 | ✅ 完成 |
| **📊 飞书同步 API** | 自动同步成绩到飞书多维表格 | ✅ 完成 |
| **📸 OCR 识别** | Tesseract.js 前端 OCR，支持中英文 | ✅ 完成 |

---

## 🚀 快速启动

### 方式一：一键启动（推荐）

```bash
~/.openclaw/workspace/dictation-pro-web/start.sh
```

### 方式二：手动启动

```bash
cd ~/.openclaw/workspace/dictation-pro-web/backend

# 安装依赖
source ~/.openclaw/workspace/.venv/bin/activate
uv pip install -r requirements.txt

# 配置环境变量（可选）
cp .env.example .env
# 编辑 .env 填入 Azure TTS 和飞书 API 密钥

# 启动服务
python server.py
```

后端服务将在 `http://localhost:3000` 启动

### 2. 打开前端页面

**教师端:**
```
http://localhost:3000/teacher-v5.html
```

**学生端:**
```
http://localhost:3000/student-v5.html?type=standard  (普通听写)
http://localhost:3000/student-v5.html?type=ielts     (雅思同义替换)
```

---

## 📁 项目结构

```
dictation-pro-web/
├── backend/
│   ├── server.js           # Express 后端 API
│   ├── package.json        # 依赖配置
│   └── .env                # 环境变量
├── public/
│   ├── teacher-v5.html     # 教师端网页
│   └── student-v5.html     # 学生端网页
└── README.md               # 项目说明
```

---

## 🔌 API 接口

### 1. 生成音频

**POST** `/api/audio/generate`

```json
{
  "words": [
    { "english": "apple", "chinese": "苹果" },
    { "english": "banana", "chinese": "香蕉" }
  ],
  "voice": "en-US-JennyNeural",
  "speed": 0.9,
  "interval": 3,
  "repeats": 2
}
```

**响应:**
```json
{
  "success": true,
  "audioUrl": "data:audio/mp3;base64,...",
  "duration": 45
}
```

---

### 2. 自动批改

**POST** `/api/correct`

```json
{
  "studentAnswer": "aple, bananna",
  "standardAnswer": "apple, banana",
  "tolerance": 0.1
}
```

**响应:**
```json
{
  "success": true,
  "report": {
    "score": 50,
    "correctRate": "50.0",
    "totalWords": 2,
    "correctCount": 1,
    "errorCount": 1,
    "corrections": [
      {
        "index": 0,
        "expected": "apple",
        "actual": "aple",
        "type": "spelling_error"
      }
    ],
    "feedback": "不错！注意拼写的细节哦~"
  }
}
```

---

### 3. 飞书同步

**POST** `/api/feishu/sync`

```json
{
  "studentName": "张三",
  "dictationDate": "2026-03-17",
  "className": "25 级 IB IELTS 听力",
  "content": "Unit 1 Vocabulary",
  "score": 92,
  "correctRate": 92.0,
  "mistakes": ["necessary", "accommodate"]
}
```

**响应:**
```json
{
  "success": true,
  "recordId": "rec_xxx",
  "message": "成绩已同步到飞书"
}
```

---

### 4. 健康检查

**GET** `/api/health`

```json
{
  "status": "ok",
  "timestamp": "2026-03-17T10:30:00.000Z",
  "services": {
    "azureTTS": "configured",
    "feishu": "configured"
  }
}
```

---

## ⚙️ 环境配置

### Azure TTS（可选）

未配置时使用模拟音频（测试用）

```env
AZURE_TTS_KEY=your_azure_key
AZURE_TTS_REGION=eastus
```

[获取 Azure TTS 密钥](https://portal.azure.com/#create/Microsoft.CognitiveServicesSpeechServices)

---

### 飞书 API（可选）

未配置时模拟同步（测试用）

```env
FEISHU_APP_ID=your_app_id
FEISHU_APP_SECRET=your_app_secret
FEISHU_APP_TOKEN=IA4ZbHqLuaD5fZsz4ctc8TeKnBd
FEISHU_TABLE_ID=tblqzJCZQHEanMZZ
```

[飞书开发者文档](https://open.feishu.cn/document/ukTMukTMukTM/uEjNwUjLxYDM14SM2ATN)

---

## 🎨 功能演示

### 教师端功能

1. **OCR 智能识别** - 上传表格截图自动识别单词
2. **词表编辑** - 支持三列编辑（英文/中文/同义词）
3. **音频生成** - 一键生成听写音频（Azure TTS）
4. **班级设置** - 年级/项目/考试类型/技能级联选择
5. **成绩管理** - 查看所有学生听写成绩

### 学生端功能

1. **听写选择** - 选择老师发布的听写任务
2. **音频播放** - 在线播放听写音频
3. **答案输入** - 文本输入听写答案
4. **自动批改** - AI 智能判分，识别错误类型
5. **错题本** - 自动生成错题本，标注错误类型
6. **成绩同步** - 自动同步到飞书多维表格

---

## 📊 批改算法

### 错误类型识别

| 类型 | 描述 | 示例 |
|------|------|------|
| `spelling_error` | 拼写错误 | `aple` → `apple` |
| `case_error` | 大小写错误 | `Apple` → `apple` |
| `order_error` | 词序错误 | `anple` → `apple` |
| `omission` | 遗漏 | `(空)` → `apple` |

### 容错处理

- 编辑距离 ≤ 10% 视为正确
- 支持同义词判定（可扩展）
- 自动忽略标点符号

---

## 🛠️ 技术栈

### 后端
- **Node.js** + **Express** - Web 框架
- **Axios** - HTTP 客户端
- **CORS** - 跨域支持

### 前端
- **React 18** - UI 框架
- **TailwindCSS** - 样式系统
- **Tesseract.js 5** - OCR 识别

### AI 服务
- **Azure TTS** - 语音合成
- **飞书 Bitable API** - 数据同步

---

## 📈 开发计划

### v5.1 (2026-03-24 ~ 2026-03-31)
- [ ] 用户登录系统
- [ ] 听写历史记录
- [ ] 成绩统计分析
- [ ] 错题本导出

### v5.2 (2026-04-01 ~ 2026-04-15)
- [ ] 微信小程序集成
- [ ] 支付系统（会员版）
- [ ] 多教师协作
- [ ] 班级管理系统

### v6.0 (2026-04-16 ~ 2026-05-01)
- [ ] AI 作文批改
- [ ] 口语跟读评分
- [ ] 个性化推荐
- [ ] 学习报告生成

---

## 🐛 常见问题

### Q: 后端服务无法启动
**A:** 检查 Node.js 版本（建议 v18+），运行 `npm install` 安装依赖

### Q: 音频生成失败
**A:** 检查 Azure TTS 密钥配置，或查看控制台错误信息

### Q: 飞书同步失败
**A:** 检查飞书应用权限，确保有多维表格写入权限

### Q: OCR 识别不准确
**A:** 尝试上传更清晰的截图，白底黑字效果最佳

---

## 📞 技术支持

**产品负责人:** Usa ⚡️（优飒）  
**邮箱:** hello@dictationpro.ai  
**微信:** DictationProAI

---

## 📄 许可证

MIT License

---

*最后更新：2026-03-17*  
*版本：v5.0*  
*维护者：Usa ⚡️*
