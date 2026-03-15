# DictationPro AI - 完整使用指南

> 智能听写系统 · ManageBac 集成版 ⚡️

---

## 📋 系统功能

### 核心功能
1. **学生信息登记** - 姓名 + 班级（年级/课程/考试类型/技能）
2. **听写创建** - 英文单词 + 中文释义
3. **答题界面** - 左侧英文输入，右侧中文释义输入
4. **自动批改** - 即时评分，详细反馈
5. **成绩存储** - LocalStorage 本地数据库
6. **数据导出** - JSON/CSV格式
7. **ManageBac 同步** - 一键导入成绩

---

## 🚀 快速开始

### 步骤 1：打开听写系统

```bash
# 方法 A：直接打开 HTML 文件
open /Users/airisagentswarm/dictation-pro-web/index-v2.html

# 方法 B：使用本地服务器
cd /Users/airisagentswarm/dictation-pro-web
python3 -m http.server 3000
# 访问 http://localhost:3000/index-v2.html
```

### 步骤 2：学生信息登记

1. 点击"开始听写"
2. 填写学生信息：
   - **姓名**：学生中文或英文姓名
   - **年级**：24 级 / 25 级 / 26 级
   - **课程类型**：AP / IB / A-Level
   - **考试类型**：托福 / 雅思 / SAT / 通用
   - **技能类型**：听力 / 阅读 / 口语 / 写作

3. 系统自动生成班级代码，例如：`25 级-AP-托福 - 听力`

### 步骤 3：创建听写

1. 选择快速模板或手动输入
2. 输入格式：`英文 - 中文，英文 - 中文`
   ```
   apple-苹果，banana-香蕉，orange-橙子
   ```
3. 配置音频设置（发音人、语速、间隔）
4. 点击"生成听写"

### 步骤 4：答题

1. 点击播放按钮听单词发音
2. **左侧输入框**：输入英文单词
3. **右侧输入框**：输入中文释义
4. 使用"上一个/下一个"导航
5. 完成后点击"提交"

### 步骤 5：查看成绩

1. 系统自动批改并显示分数
2. 查看详细批改结果（对错对比）
3. 错题本自动生成

### 步骤 6：保存成绩

1. 点击"保存成绩"按钮
2. 成绩自动存储到本地数据库
3. 数据保存在浏览器 LocalStorage

---

## 💾 数据库管理

### 查看数据库

打开浏览器控制台（F12），执行：

```javascript
// 查看所有记录
const db = JSON.parse(localStorage.getItem('dictationDatabase') || '[]');
console.table(db);

// 查看记录数量
console.log('共', db.length, '条记录');

// 查看某学生的所有成绩
const studentName = '张三';
const records = db.filter(r => r.name === studentName);
console.table(records);

// 查看某班级的所有成绩
const classInfo = '25 级-AP-托福 - 听力';
const classRecords = db.filter(r => r.classInfo === classInfo);
console.table(classRecords);
```

### 导出数据库

打开浏览器控制台，执行：

```javascript
// 导出为 JSON
const db = JSON.parse(localStorage.getItem('dictationDatabase') || '[]');
const jsonStr = JSON.stringify(db, null, 2);
const blob = new Blob([jsonStr], { type: 'application/json' });
const url = URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;
a.download = 'dictation-database-' + new Date().toISOString().split('T')[0] + '.json';
a.click();
console.log('✅ JSON 导出成功');

// 导出为 CSV
function convertToCSV(data) {
  const headers = ['日期', '姓名', '年级', '课程类型', '考试类型', '技能', '分数', '正确数', '总题数', '班级代码'];
  const rows = data.map(r => [
    r.date,
    r.name,
    r.grade + '级',
    r.program,
    r.testType,
    r.skill,
    r.score,
    r.correct,
    r.total,
    r.classInfo
  ]);
  return [headers.join(','), ...rows.map(row => row.map(cell => '"' + cell + '"').join(','))].join('\n');
}

const csvStr = convertToCSV(db);
const csvBlob = new Blob([csvStr], { type: 'text/csv' });
const csvUrl = URL.createObjectURL(csvBlob);
const csvA = document.createElement('a');
csvA.href = csvUrl;
csvA.download = 'dictation-database-' + new Date().toISOString().split('T')[0] + '.csv';
csvA.click();
console.log('✅ CSV 导出成功');
```

---

## 🔄 ManageBac 成绩同步

### 方法一：手动导入脚本（推荐）

#### 步骤 1：导出 CSV

按上面"导出数据库"的方法，导出 CSV 文件。

#### 步骤 2：打开 ManageBac

访问：https://sdgj.managebac.cn/teacher

登录到成绩页面（Gradebook）。

#### 步骤 3：运行导入脚本

1. 按 **F12** 打开浏览器控制台
2. 复制并粘贴以下代码：

```javascript
// ManageBac 成绩自动导入脚本
(function() {
  console.log('🚀 ManageBac 成绩导入工具启动...');
  
  // 提示用户复制 CSV 内容
  const csvText = prompt('请复制 CSV 文件内容并粘贴到这里:');
  
  if (!csvText) {
    console.log('❌ 已取消');
    return;
  }
  
  // 解析 CSV
  const lines = csvText.trim().split('\n');
  const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''));
  
  const records = lines.slice(1).map(line => {
    const values = line.match(/(".*?"|[^",\s]+)(?=\s*,|\s*$)/g) || [];
    const record = {};
    headers.forEach((header, i) => {
      record[header] = values[i] ? values[i].trim().replace(/"/g, '') : '';
    });
    return record;
  });
  
  console.log('📊 解析到', records.length, '条记录');
  
  // 逐条导入
  records.forEach((record, index) => {
    setTimeout(() => {
      importToManageBac(record, index + 1, records.length);
    }, index * 2000);
  });
  
  function importToManageBac(record, index, total) {
    console.log(`📝 导入第 ${index}/${total} 条：${record['姓名']} - ${record['分数']}分`);
    
    // 查找学生（根据 ManageBac 实际页面结构调整）
    const studentRow = document.querySelector(`tr[student-name*="${record['姓名']}"]`);
    
    if (studentRow) {
      const scoreInput = studentRow.querySelector('input[type="number"]');
      
      if (scoreInput) {
        scoreInput.value = record['分数'];
        scoreInput.dispatchEvent(new Event('input', { bubbles: true }));
        scoreInput.dispatchEvent(new Event('change', { bubbles: true }));
        
        console.log('✅ 导入成功:', record['姓名']);
      } else {
        console.warn('⚠️ 未找到成绩输入框:', record['姓名']);
      }
    } else {
      console.warn('⚠️ 未找到学生:', record['姓名']);
    }
    
    if (index === total) {
      setTimeout(() => {
        alert(`✅ 完成！已导入 ${total} 条成绩`);
      }, 3000);
    }
  }
})();
```

3. 按 **Enter** 执行
4. 粘贴 CSV 文件内容
5. 等待自动导入完成

---

### 方法二：使用同步工具（高级）

#### 安装依赖

```bash
cd /Users/airisagentswarm/dictation-pro-web
npm install playwright
```

#### 运行同步工具

```bash
node sync-to-managebac.js
```

工具会：
1. 自动打开浏览器
2. 导航到 ManageBac
3. 等待手动登录
4. 自动导入成绩

---

## 📊 数据库字段说明

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| id | number | 唯一标识 | 1710518400000 |
| name | string | 学生姓名 | 张三 |
| classInfo | string | 班级信息 | 25 级-AP-托福 - 听力 |
| grade | string | 年级 | 25 |
| program | string | 课程类型 | AP |
| testType | string | 考试类型 | TOEFL |
| skill | string | 技能类型 | Listening |
| score | number | 分数 | 92 |
| total | number | 总题数 | 20 |
| correct | number | 正确数 | 18 |
| date | string | 日期 | 2026-03-15 |
| timestamp | number | 时间戳 | 1710518400000 |

---

## 🛠️ 高级功能

### 数据筛选

```javascript
const db = JSON.parse(localStorage.getItem('dictationDatabase') || '[]');

// 按日期筛选
const today = new Date().toISOString().split('T')[0];
const todayRecords = db.filter(r => r.date === today);

// 按分数筛选（优秀 90+）
const excellent = db.filter(r => r.score >= 90);

// 按年级筛选
const grade25 = db.filter(r => r.grade === '25');

// 统计平均分
const avgScore = db.reduce((sum, r) => sum + r.score, 0) / db.length;
console.log('平均分:', avgScore.toFixed(2));
```

### 数据备份

```javascript
// 备份到文件
const db = JSON.parse(localStorage.getItem('dictationDatabase') || '[]');
const backup = {
  version: '1.0',
  backupDate: new Date().toISOString(),
  recordCount: db.length,
  data: db
};

const jsonStr = JSON.stringify(backup, null, 2);
const blob = new Blob([jsonStr], { type: 'application/json' });
const url = URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;
a.download = 'dictation-backup-' + new Date().toISOString().split('T')[0] + '.json';
a.click();
```

### 数据恢复

```javascript
// 从备份文件恢复
function restoreBackup(jsonStr) {
  const backup = JSON.parse(jsonStr);
  if (backup.data && Array.isArray(backup.data)) {
    localStorage.setItem('dictationDatabase', JSON.stringify(backup.data));
    console.log('✅ 恢复成功！共', backup.data.length, '条记录');
  } else {
    console.error('❌ 备份文件格式错误');
  }
}
```

---

## 🔧 故障排除

### 问题 1：成绩无法保存

**原因**：浏览器 LocalStorage 已满或禁用

**解决**：
1. 清理浏览器缓存
2. 检查浏览器设置是否允许 LocalStorage
3. 使用导出功能备份数据

### 问题 2：ManageBac 导入失败

**原因**：页面选择器不匹配

**解决**：
1. 打开 ManageBac 成绩页面
2. 按 F12 检查学生行的 HTML 结构
3. 修改导入脚本中的选择器：
   ```javascript
   // 根据实际情况调整
   const studentRow = document.querySelector('tr[data-student*="姓名"]');
   // 或
   const studentRow = document.querySelector('tr:contains("姓名")');
   ```

### 问题 3：数据丢失

**原因**：浏览器缓存被清理

**解决**：
1. 定期导出备份
2. 使用云存储（飞书多维表格）
3. 检查 LocalStorage 是否有数据：
   ```javascript
   console.log(localStorage.getItem('dictationDatabase'));
   ```

---

## 📁 项目文件

```
dictation-pro-web/
├── index-v2.html              # 主应用（学生信息 + 答题）
├── sync-to-managebac.js       # ManageBac 同步工具
├── CLAUDE.md                  # 设计配置
├── CLAUDE_DESIGN_SKILL.md     # Design Skill 文档
├── vercel.json                # Vercel 部署配置
├── README.md                  # 本文件
├── exports/                   # 导出数据目录
│   ├── dictation-*.json      # JSON 导出
│   └── dictation-*.csv       # CSV 导出
└── screenshots/               # 截图目录
    └── *.png                 # 截图文件
```

---

## 🚀 部署到 Vercel

```bash
# 安装 Vercel CLI
npm install -g vercel

# 部署
cd /Users/airisagentswarm/dictation-pro-web
vercel

# 获取公开链接
# https://dictation-pro-web.vercel.app
```

---

## 📞 技术支持

**产品负责人**：Usa ⚡️（优飒）

**更新日期**：2026-03-15

**版本**：v2.0 ManageBac 集成版

---

## 🎯 下一步优化

- [ ] 飞书多维表格云同步
- [ ] 批量导入学生名单
- [ ] 成绩趋势分析图表
- [ ] 家长端查看页面
- [ ] 错题本自动复习计划
