/**
 * DictationPro AI - 后端 API 服务
 * 提供音频生成、自动批改、飞书同步等功能
 */

const express = require('express')
const cors = require('cors')
const dotenv = require('dotenv')
const path = require('path')

// 加载环境变量
dotenv.config()

const app = express()
const PORT = process.env.PORT || 3000

// 中间件
app.use(cors())
app.use(express.json({ limit: '10mb' }))
app.use(express.static(path.join(__dirname, '../public')))

// ========== 工具函数 ==========

// 编辑距离算法 (Levenshtein Distance)
function levenshteinDistance(s1, s2) {
  const m = s1.length
  const n = s2.length
  const dp = Array(m + 1).fill(null).map(() => Array(n + 1).fill(0))
  
  for (let i = 0; i <= m; i++) dp[i][0] = i
  for (let j = 0; j <= n; j++) dp[0][j] = j
  
  for (let i = 1; i <= m; i++) {
    for (let j = 1; j <= n; j++) {
      if (s1[i - 1] === s2[j - 1]) {
        dp[i][j] = dp[i - 1][j - 1]
      } else {
        dp[i][j] = Math.min(
          dp[i - 1][j] + 1,     // 删除
          dp[i][j - 1] + 1,     // 插入
          dp[i - 1][j - 1] + 1  // 替换
        )
      }
    }
  }
  
  return dp[m][n]
}

// 标准化文本
function normalizeText(text) {
  return text
    .toLowerCase()
    .replace(/[.,!?;:]/g, '')
    .replace(/\s+/g, ' ')
    .trim()
}

// 单词对比（支持容错）
function compareWords(student, standard, tolerance = 0.1) {
  if (student === standard) return true
  
  const distance = levenshteinDistance(student, standard)
  const maxLen = Math.max(student.length, standard.length)
  
  if (maxLen === 0) return true
  
  const similarity = 1 - distance / maxLen
  return similarity >= (1 - tolerance)
}

// 识别错误类型
function identifyErrorType(student, standard) {
  if (!student || student.length === 0) return 'omission'
  if (student.toLowerCase() === standard.toLowerCase()) return 'case_error'
  
  const s1 = student.toLowerCase()
  const s2 = standard.toLowerCase()
  
  if (s1.split('').sort().join('') === s2.split('').sort().join('')) {
    return 'order_error'
  }
  
  return 'spelling_error'
}

// 生成反馈
function generateFeedback(score, corrections) {
  if (score >= 90) {
    return '太棒了！继续保持！🎉'
  } else if (score >= 70) {
    const commonErrors = analyzeCommonErrors(corrections)
    return `不错！注意${commonErrors}的拼写哦~`
  } else {
    return '加油！建议多练习几遍，你可以的！💪'
  }
}

// 分析常见错误
function analyzeCommonErrors(corrections) {
  const errorTypes = corrections.map(c => c.type)
  const spellingErrors = errorTypes.filter(t => t === 'spelling_error').length
  
  if (spellingErrors > corrections.length / 2) {
    return '拼写'
  }
  return '细节'
}

// ========== API 路由 ==========

/**
 * POST /api/audio/generate
 * 生成听写音频 (Azure TTS)
 */
app.post('/api/audio/generate', async (req, res) => {
  const { words, voice, speed, interval, repeats } = req.body
  
  try {
    // 构建 SSML
    const ssml = buildSSML(words, voice, speed, interval, repeats)
    
    // 调用 Azure TTS API
    const audioBuffer = await callAzureTTS(ssml)
    
    // 返回 Base64 音频
    res.json({
      success: true,
      audioUrl: `data:audio/mp3;base64,${audioBuffer.toString('base64')}`,
      duration: calculateDuration(words, speed, interval, repeats)
    })
  } catch (error) {
    console.error('音频生成失败:', error)
    
    // 如果 Azure 不可用，返回模拟音频（用于测试）
    if (process.env.AZURE_TTS_KEY === 'YOUR_AZURE_TTS_KEY' || !process.env.AZURE_TTS_KEY) {
      console.log('⚠️ 使用模拟音频（未配置 Azure TTS）')
      res.json({
        success: true,
        audioUrl: 'data:audio/mp3;base64,SUQzBAAAAAAAI1RTU0UAAAAPAAADTGF2ZjU4LjI5LjEwMAAAAAAAAAAAAAAA//tQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAWGluZwAAAA8AAAACAAADhAC7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7////////////////////////////////////////////////////////////AAAAAExhdmM1OC41NQAAAAAAAAAAAAAAACQCgAAAAAAAASXjLkYjAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA//tQZAAP8AAAaQAAAAgAAA0gAAABAAABpAAAACAAADSAAAAETEFNRTMuMTAwVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV',
        duration: 10,
        warning: '模拟音频 - 请配置 Azure TTS 密钥'
      })
      return
    }
    
    res.status(500).json({
      success: false,
      error: error.message
    })
  }
})

// 构建 SSML
function buildSSML(words, voice, speed, interval, repeats) {
  const wordList = words.map(w => w.english).join(', ')
  
  let ssml = `<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">`
  ssml += `<voice name="${voice}">`
  ssml += `<prosody rate="${speed}">`
  
  for (let i = 0; i < repeats; i++) {
    ssml += `<p>${wordList}</p>`
    if (i < repeats - 1) {
      ssml += `<break time="${interval}s" />`
    }
  }
  
  ssml += `</prosody></voice></speak>`
  return ssml
}

// 调用 Azure TTS API
async function callAzureTTS(ssml) {
  const axios = require('axios')
  const AccessToken = await getAzureToken()
  
  const response = await axios.post(
    `https://${process.env.AZURE_TTS_REGION}.tts.speech.microsoft.com/cognitiveservices/v1`,
    ssml,
    {
      headers: {
        'Ocp-Apim-Subscription-Key': process.env.AZURE_TTS_KEY,
        'Authorization': `Bearer ${AccessToken}`,
        'Content-Type': 'application/ssml+xml',
        'X-Microsoft-OutputFormat': 'audio-16khz-128kbitrate-mono-mp3',
        'User-Agent': 'DictationPro/1.0'
      },
      responseType: 'arraybuffer'
    }
  )
  
  return Buffer.from(response.data)
}

// 获取 Azure Token
async function getAzureToken() {
  const axios = require('axios')
  
  const response = await axios.post(
    `https://${process.env.AZURE_TTS_REGION}.api.cognitive.microsoft.com/sts/v1.0/issueToken`,
    null,
    {
      headers: {
        'Ocp-Apim-Subscription-Key': process.env.AZURE_TTS_KEY
      }
    }
  )
  
  return response.data
}

// 计算音频时长（估算）
function calculateDuration(words, speed, interval, repeats) {
  const totalChars = words.reduce((sum, w) => sum + w.english.length, 0)
  const baseDuration = totalChars / 15 * (1 / speed) // 假设每秒 15 个字符
  const totalDuration = baseDuration * repeats + (repeats - 1) * interval
  return Math.round(totalDuration)
}

/**
 * POST /api/correct
 * 自动批改听写
 */
app.post('/api/correct', async (req, res) => {
  const { studentAnswer, standardAnswer, tolerance = 0.1 } = req.body
  
  try {
    // 标准化答案
    const normalizedStudent = normalizeText(studentAnswer)
    const normalizedStandard = normalizeText(standardAnswer)
    
    // 分词对比
    const studentWords = normalizedStudent.split(/\s+/).filter(w => w)
    const standardWords = normalizedStandard.split(/\s+/).filter(w => w)
    
    // 逐词批改
    const corrections = []
    let correctCount = 0
    
    for (let i = 0; i < standardWords.length; i++) {
      const standard = standardWords[i]
      const student = studentWords[i] || ''
      
      const isCorrect = compareWords(student, standard, tolerance)
      
      if (isCorrect) {
        correctCount++
      } else {
        corrections.push({
          index: i,
          expected: standard,
          actual: student,
          type: identifyErrorType(student, standard)
        })
      }
    }
    
    // 计算得分
    const totalWords = standardWords.length
    const score = totalWords > 0 ? Math.round((correctCount / totalWords) * 100) : 0
    const correctRate = totalWords > 0 ? (correctCount / totalWords * 100).toFixed(1) : '0'
    
    // 生成批改报告
    const report = {
      score,
      correctRate,
      totalWords,
      correctCount,
      errorCount: corrections.length,
      corrections,
      feedback: generateFeedback(score, corrections)
    }
    
    res.json({
      success: true,
      report
    })
  } catch (error) {
    console.error('批改失败:', error)
    res.status(500).json({
      success: false,
      error: error.message
    })
  }
})

/**
 * POST /api/feishu/sync
 * 同步成绩到飞书多维表格
 */
app.post('/api/feishu/sync', async (req, res) => {
  const { studentName, dictationDate, className, content, score, correctRate, mistakes } = req.body
  
  try {
    const axios = require('axios')
    
    // 1. 获取 Access Token
    const tokenResponse = await axios.post(
      'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
      {
        app_id: process.env.FEISHU_APP_ID,
        app_secret: process.env.FEISHU_APP_SECRET
      }
    )
    
    const accessToken = tokenResponse.data.tenant_access_token
    
    // 2. 添加记录到飞书多维表格
    const appToken = process.env.FEISHU_APP_TOKEN || 'IA4ZbHqLuaD5fZsz4ctc8TeKnBd'
    const tableId = process.env.FEISHU_TABLE_ID || 'tblqzJCZQHEanMZZ'
    
    const recordResponse = await axios.post(
      `https://open.feishu.cn/open-apis/bitable/v1/apps/${appToken}/tables/${tableId}/records`,
      {
        fields: {
          Name: studentName,
          上课日期: new Date(dictationDate).getTime(),
          班级：className,
          课堂主要内容：content,
          课堂表现: `${score}分`,
          表扬学生: score >= 90 ? studentName : '',
          表扬原因: score >= 90 ? `听写正确率${correctRate}%` : '',
          提醒学生: score < 70 ? studentName : '',
          提醒原因: score < 70 ? `需要加强练习` : ''
        }
      },
      {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        }
      }
    )
    
    res.json({
      success: true,
      recordId: recordResponse.data.data.record_id,
      message: '成绩已同步到飞书'
    })
  } catch (error) {
    console.error('飞书同步失败:', error.response?.data || error.message)
    
    // 如果未配置飞书，返回成功但不实际同步（用于测试）
    if (!process.env.FEISHU_APP_ID || process.env.FEISHU_APP_ID === 'YOUR_FEISHU_APP_ID') {
      console.log('⚠️ 模拟飞书同步（未配置飞书 API）')
      res.json({
        success: true,
        recordId: 'mock_' + Date.now(),
        message: '模拟同步 - 请配置飞书 API',
        warning: '未配置飞书 API 凭证'
      })
      return
    }
    
    res.status(500).json({
      success: false,
      error: error.response?.data?.msg || error.message
    })
  }
})

/**
 * GET /api/health
 * 健康检查
 */
app.get('/api/health', (req, res) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    services: {
      azureTTS: process.env.AZURE_TTS_KEY ? 'configured' : 'not configured',
      feishu: process.env.FEISHU_APP_ID ? 'configured' : 'not configured'
    }
  })
})

// 启动服务器
app.listen(PORT, () => {
  console.log(`🚀 DictationPro Backend running on http://localhost:${PORT}`)
  console.log(`📊 Health check: http://localhost:${PORT}/api/health`)
})

module.exports = app
