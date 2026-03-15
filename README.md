# DictationPro AI - Web 版 🚀

> 智能听写系统 - 10 分钟 MVP 上线！

---

## 🎯 立即使用

### 方法 1：本地打开（最快）

直接在浏览器打开：

```bash
open /Users/airisagentswarm/dictation-pro-web/index.html
```

或者双击 `index.html` 文件！

### 方法 2：本地服务器

```bash
cd /Users/airisagentswarm/dictation-pro-web
python3 -m http.server 8080
```

然后访问：http://localhost:8080

---

## 🌐 部署到 Vercel（免费上线）

### 步骤 1：安装 Vercel CLI

```bash
npm install -g vercel
```

### 步骤 2：部署

```bash
cd /Users/airisagentswarm/dictation-pro-web
vercel
```

### 步骤 3：获取上线链接

部署完成后，Vercel 会给你一个链接，例如：
```
https://dictation-pro-web.vercel.app
```

**完成！全球可访问！** 🎉

---

## ✨ 功能特性

### MVP 版本包含：

1. **🏠 首页** - 产品介绍 + 快速开始
2. **📝 创建听写**
   - 文本输入
   - 快速模板
   - 发音选择（美音/英音/中文）
   - 语速调节
   - 单词间隔设置
3. **🎧 听写执行**
   - 浏览器 TTS 发音
   - 进度控制
   - 答案输入
   - 导航（上一个/下一个）
4. **📊 自动批改**
   - 即时评分
   - 对错对比
   - 错题本生成
   - 可打印报告

---

## 🛠️ 技术栈

- **React 18** - 前端框架（CDN 加载）
- **Tailwind CSS** - 样式框架
- **Web Speech API** - 浏览器原生 TTS
- **Vercel** - 免费部署

**无需构建工具，无需 Node.js，单文件即可运行！**

---

## 📱 兼容性

- ✅ Chrome / Edge
- ✅ Safari
- ✅ Firefox
- ✅ 手机浏览器

---

## 🎨 自定义

### 修改主题色

编辑 `index.html`，找到 `<style>` 部分：

```css
body {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
```

修改颜色值即可。

### 添加更多模板

编辑 `index.html`，找到 `quickTemplates` 数组：

```javascript
const quickTemplates = [
  'apple, banana, orange, grape, strawberry',
  'necessary, accommodate, questionnaire, committee',
  'photosynthesis, ecosystem, biodiversity, evolution',
  // 添加你的模板...
];
```

---

## 🚀 下一步优化

### 待开发功能：

- [ ] 音频文件生成（Azure TTS）
- [ ] 用户数据保存（LocalStorage）
- [ ] 飞书同步
- [ ] 错题本持久化
- [ ] 分享功能
- [ ] 多语言支持

---

## 📞 联系方式

**产品负责人：** Usa ⚡️（优飒）

---

*创建时间：2026-03-15*  
*版本：v1.0 MVP*
