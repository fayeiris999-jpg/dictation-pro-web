# DictationPro API 文档

**版本:** v8.0  
**最后更新:** 2026-03-18  
**基础地址:** `http://localhost:3000`

---

## 📋 目录

- [健康检查](#健康检查)
- [音频生成](#音频生成)
- [自动批改](#自动批改)
- [文件解析](#文件解析)
- [用户认证](#用户认证)
- [成绩统计](#成绩统计)
- [数据导出](#数据导出)
- [AI 功能](#ai-功能)

---

## 健康检查

### GET `/api/health`

检查服务状态

**请求示例:**
```bash
curl http://localhost:3000/api/health
```

**响应示例:**
```json
{
  "status": "ok",
  "timestamp": "2026-03-18T06:53:30.996895",
  "services": {
    "azureTTS": "configured",
    "feishu": "configured"
  }
}
```

**状态码:**
- `200` - 服务正常
- `500` - 服务异常

---

## 音频生成

### POST `/api/audio/generate`

生成单词发音音频（支持 Azure TTS）

**请求体:**
```json
{
  "words": [
    {"english": "apple", "chinese": "苹果"},
    {"english": "banana", "chinese": "香蕉"}
  ],
  "voice": "zh-CN-XiaoxiaoNeural",
  "speed": 1.0,
  "interval": 3,
  "repeats": 2
}
```

**参数说明:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| words | array | ✅ | 单词列表 |
| voice | string | ❌ | TTS 语音（默认：zh-CN-XiaoxiaoNeural） |
| speed | number | ❌ | 语速（0.5-2.0，默认：1.0） |
| interval | number | ❌ | 单词间隔秒数（默认：3） |
| repeats | number | ❌ | 重复次数（默认：2） |

**响应示例:**
```json
{
  "success": true,
  "audioUrl": "data:audio/mp3;base64,SUQzBAAAA...",
  "duration": 45.5,
  "warning": "模拟音频 - 请配置 Azure TTS"
}
```

**状态码:**
- `200` - 生成成功
- `400` - 参数错误
- `500` - 生成失败

---

## 自动批改

### POST `/api/correct`

自动批改听写答案

**请求体:**
```json
{
  "studentAnswer": "aple, bananna, oringe",
  "standardAnswer": "apple, banana, orange",
  "tolerance": 0.1
}
```

**参数说明:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| studentAnswer | string | ✅ | 学生答案（逗号或空格分隔） |
| standardAnswer | string | ✅ | 标准答案 |
| tolerance | number | ❌ | 容错率（0-1，默认：0.1） |

**响应示例:**
```json
{
  "success": true,
  "report": {
    "score": 0,
    "correctRate": "0.0%",
    "totalWords": 3,
    "correctCount": 0,
    "errorCount": 3,
    "corrections": [
      {
        "index": 0,
        "expected": "apple",
        "actual": "aple",
        "type": "spelling_error"
      },
      {
        "index": 1,
        "expected": "banana",
        "actual": "bananna",
        "type": "spelling_error"
      },
      {
        "index": 2,
        "expected": "orange",
        "actual": "oringe",
        "type": "spelling_error"
      }
    ],
    "feedback": "加油！建议多练习几遍，你可以的！💪"
  }
}
```

**错误类型:**

| 类型 | 说明 | 示例 |
|------|------|------|
| `spelling_error` | 拼写错误 | `aple` → `apple` |
| `case_error` | 大小写错误 | `Apple` → `apple` |
| `order_error` | 词序错误 | `anple` → `apple` |
| `omission` | 遗漏 | `(空)` → `apple` |

---

## 文件解析

### POST `/api/file/parse`

解析上传的文件（Word/PDF/图片）

**请求体:**
```json
{
  "file": "base64 编码的文件内容",
  "type": "word"
}
```

**参数说明:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | string | ✅ | Base64 编码的文件内容 |
| type | string | ✅ | 文件类型：`word` / `pdf` / `image` |

**响应示例:**
```json
{
  "success": true,
  "words": [
    {
      "english": "apple",
      "chinese": "苹果",
      "synonym": "fruit"
    },
    {
      "english": "banana",
      "chinese": "香蕉",
      "synonym": ""
    }
  ]
}
```

**状态码:**
- `200` - 解析成功
- `400` - 参数错误
- `500` - 解析失败

---

## 用户认证

### POST `/api/auth/register`

用户注册

**请求体:**
```json
{
  "username": "teststudent",
  "password": "test123",
  "role": "student",
  "displayName": "测试学生",
  "className": "25 级 IB IELTS 听力"
}
```

**参数说明:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | ✅ | 用户名 |
| password | string | ✅ | 密码 |
| role | string | ✅ | 角色：`student` / `teacher` |
| displayName | string | ❌ | 显示名称 |
| className | string | ❌ | 班级名称（学生必填） |

**响应示例:**
```json
{
  "success": true,
  "user_id": "user_2845579a4a8d8bca",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

### POST `/api/auth/login`

用户登录

**请求体:**
```json
{
  "username": "teststudent",
  "password": "test123"
}
```

**响应示例:**
```json
{
  "success": true,
  "user": {
    "user_id": "user_2845579a4a8d8bca",
    "username": "teststudent",
    "role": "student",
    "display_name": "测试学生",
    "class_name": "25 级 IB IELTS 听力"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

## 成绩统计

### POST `/api/stats/add`

添加成绩记录

**请求体:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "dictationId": "dictation_123",
  "dictationTitle": "Unit 1 Vocabulary",
  "score": 85,
  "correctCount": 17,
  "totalWords": 20,
  "corrections": [...]
}
```

**响应示例:**
```json
{
  "success": true,
  "record_id": "score_1710759210.123"
}
```

---

### POST `/api/stats/user`

获取用户统计信息

**请求体:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**响应示例:**
```json
{
  "success": true,
  "stats": {
    "total_dictations": 10,
    "average_score": 85.5,
    "best_score": 95,
    "trend": "improving",
    "recent_scores": [
      {"score": 80, "created_at": "2026-03-15"},
      {"score": 85, "created_at": "2026-03-16"},
      {"score": 90, "created_at": "2026-03-17"}
    ],
    "error_types": {
      "apple": 3,
      "banana": 2
    }
  }
}
```

---

### POST `/api/stats/class`

获取班级统计信息

**请求体:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "classId": "25 级 IB IELTS 听力"
}
```

**响应示例:**
```json
{
  "success": true,
  "stats": {
    "total_students": 15,
    "average_score": 82.5,
    "highest_score": 95,
    "lowest_score": 65,
    "score_distribution": {
      "90-100": 5,
      "80-89": 8,
      "70-79": 4,
      "60-69": 2,
      "0-59": 1
    },
    "student_ranking": [
      {
        "username": "张三",
        "average_score": 95.0,
        "dictation_count": 10
      },
      {
        "username": "李四",
        "average_score": 88.5,
        "dictation_count": 8
      }
    ]
  }
}
```

---

## 数据导出

### POST `/api/export/excel`

导出用户错题本为 Excel

**请求体:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**响应示例:**
```json
{
  "success": true,
  "download_url": "/api/export/download/错题本_测试学生_20260318_062028.xlsx",
  "error_count": 15,
  "score_count": 10
}
```

---

### POST `/api/export/batch`

批量导出班级成绩

**请求体:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "class_name": "25 级 IB IELTS 听力",
  "start_date": "2026-03-01",
  "end_date": "2026-03-31"
}
```

**响应示例:**
```json
{
  "success": true,
  "download_url": "/api/export/download/班级成绩_25 级 IB IELTS 听力_20260318_062028.xlsx",
  "record_count": 150
}
```

---

### POST `/api/export/error-book`

导出错题本 PDF

**请求体:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user_id": "user_2845579a4a8d8bca"
}
```

**响应示例:**
```json
{
  "success": true,
  "download_url": "/api/export/download/错题本_测试学生_20260318_062028.pdf",
  "error_count": 15,
  "score_count": 10
}
```

---

### POST `/api/report/generate`

生成学习报告（周报/月报）

**请求体:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user_id": "user_2845579a4a8d8bca",
  "period": "weekly"
}
```

**参数说明:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| period | string | ❌ | 报告周期：`weekly` / `monthly` |

**响应示例:**
```json
{
  "success": true,
  "download_url": "/api/export/download/学习报告_测试学生_weekly_20260318_062028.pdf"
}
```

---

## AI 功能

### POST `/api/ai/memory-techniques`

生成 AI 单词记忆技巧

**请求体:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "words": [
    {"english": "apple", "chinese": "苹果"},
    {"english": "banana", "chinese": "香蕉"}
  ]
}
```

**响应示例:**
```json
{
  "success": true,
  "techniques": [
    {
      "word": "apple",
      "phonetic": "/ˈæp.əl/",
      "audio_tip": "发音类似'爱剖'，想象爱剖苹果吃",
      "shape_tip": "a-pp-le，像一个人 (a) 拿着两个苹果 (pp)",
      "example_sentences": [
        {"en": "I eat an apple every day.", "zh": "我每天吃一个苹果。"},
        {"en": "This apple is sweet.", "zh": "这个苹果很甜。"},
        {"en": "She peeled the apple.", "zh": "她削了苹果皮。"}
      ],
      "image_prompt": "A red shiny apple on a wooden table, photorealistic, 4k",
      "video_script": "【0-3 秒】镜头对准苹果特写...",
      "memory_story": "小明早上起来，拿起一个红红的 apple...",
      "fill_blank_text": "I eat an ____ every day.",
      "fill_blank_answers": ["apple"]
    }
  ]
}
```

---

### POST `/api/ai/generate-image`

生成单词图片（AI 绘画）

**请求体:**
```json
{
  "word": "apple",
  "image_prompt": "A red shiny apple on a wooden table, photorealistic, 4k"
}
```

**响应示例:**
```json
{
  "success": true,
  "image_url": "https://cdn.nanobanana.pro/images/xxx.png",
  "warning": "使用占位图 - 请配置 AI 绘画 API"
}
```

---

### POST `/api/ai/generate-audio`

生成单词发音（Azure TTS）

**请求体:**
```json
{
  "word": "apple",
  "text": "apple. This is an apple."
}
```

**响应示例:**
```json
{
  "success": true,
  "audio_url": "data:audio/mp3;base64,SUQzBAAAA...",
  "duration": 2.5,
  "warning": "模拟音频 - 请配置 Azure TTS"
}
```

---

### POST `/api/ai/generate-story`

生成英文故事（包含错词）

**请求体:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "words": [
    {"english": "apple", "chinese": "苹果"},
    {"english": "banana", "chinese": "香蕉"},
    {"english": "orange", "chinese": "橙子"}
  ],
  "level": "B1",
  "style": "fairy"
}
```

**参数说明:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| words | array | ✅ | 错词列表 |
| level | string | ❌ | 英语难度：`A1`/`A2`/`B1`/`B2`/`C1`/`C2` |
| style | string | ❌ | 故事风格：`fairy`/`suspense`/`horror`/`comedy`/`news`/`scifi` |

**响应示例:**
```json
{
  "success": true,
  "story": {
    "title": "The Magic Garden",
    "content_en": "Once upon a time, there was a magical garden where fruits could talk...",
    "content_zh": "从前，有一个神奇的花园，那里的水果会说话...",
    "word_count": 60,
    "level": "B1",
    "style": "fairy",
    "words_used": ["apple", "banana", "orange"]
  }
}
```

---

## 错误码说明

| 错误码 | 说明 |
|--------|------|
| `200` | 成功 |
| `400` | 请求参数错误 |
| `401` | 未授权（Token 无效或过期） |
| `404` | 资源不存在 |
| `500` | 服务器内部错误 |

---

## 认证说明

所有需要用户认证的接口都需要在请求体中包含 `token` 参数。

Token 通过 `/api/auth/login` 或 `/api/auth/register` 获取，格式为 JWT。

Token 有效期：7 天

---

## 速率限制

| 接口类型 | 限制 |
|----------|------|
| 普通 API | 100 次/分钟 |
| AI 生成 API | 10 次/分钟 |
| 文件上传 API | 5 次/分钟 |

---

*最后更新：2026-03-18*  
*维护者：Usa ⚡️*
