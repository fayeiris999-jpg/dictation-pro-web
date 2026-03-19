// DictationPro AI - 统计图表组件
// 使用 Chart.js 进行数据可视化

const StatsCharts = {
  // 创建成绩趋势图（折线图）
  createTrendChart: (canvasId, data) => {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    
    return new Chart(ctx, {
      type: 'line',
      data: {
        labels: data.labels || [],
        datasets: [{
          label: '成绩',
          data: data.scores || [],
          borderColor: '#007AFF',
          backgroundColor: 'rgba(0, 122, 255, 0.1)',
          fill: true,
          tension: 0.4,
          pointRadius: 6,
          pointHoverRadius: 8,
          pointBackgroundColor: '#007AFF',
          pointBorderColor: '#fff',
          pointBorderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleColor: '#fff',
            bodyColor: '#fff',
            cornerRadius: 8,
            padding: 12
          }
        },
        scales: {
          y: {
            min: 0,
            max: 100,
            grid: { color: 'rgba(0, 0, 0, 0.05)' },
            ticks: { color: '#8E8E93' }
          },
          x: {
            grid: { display: false },
            ticks: { color: '#8E8E93' }
          }
        }
      }
    });
  },
  
  // 创建分数分布图（饼图）
  createDistributionChart: (canvasId, data) => {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    
    return new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['90-100分', '80-89分', '70-79分', '60-69分', '60分以下'],
        datasets: [{
          data: [
            data['90-100'] || 0,
            data['80-89'] || 0,
            data['70-79'] || 0,
            data['60-69'] || 0,
            data['0-59'] || 0
          ],
          backgroundColor: [
            '#34C759', // green
            '#007AFF', // blue
            '#FF9500', // orange
            '#FF3B30', // red
            '#8E8E93'  // gray
          ],
          borderWidth: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '60%',
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              color: '#3A3A3C',
              padding: 16,
              usePointStyle: true,
              pointStyle: 'circle'
            }
          }
        }
      }
    });
  },
  
  // 创建错误类型分布图（横向柱状图）
  createErrorChart: (canvasId, data) => {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    
    const words = data.map(d => d.word);
    const counts = data.map(d => d.count);
    
    return new Chart(ctx, {
      type: 'bar',
      data: {
        labels: words,
        datasets: [{
          label: '错误次数',
          data: counts,
          backgroundColor: 'rgba(255, 59, 48, 0.8)',
          borderRadius: 8
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          x: {
            beginAtZero: true,
            grid: { color: 'rgba(0, 0, 0, 0.05)' },
            ticks: { color: '#8E8E93', stepSize: 1 }
          },
          y: {
            grid: { display: false },
            ticks: { color: '#3A3A3C' }
          }
        }
      }
    });
  },
  
  // 创建班级排名图（柱状图）
  createRankingChart: (canvasId, data) => {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    
    const names = data.map(d => d.username);
    const scores = data.map(d => d.average_score);
    
    return new Chart(ctx, {
      type: 'bar',
      data: {
        labels: names,
        datasets: [{
          label: '平均分',
          data: scores,
          backgroundColor: scores.map(s => 
            s >= 90 ? '#34C759' :
            s >= 80 ? '#007AFF' :
            s >= 70 ? '#FF9500' :
            s >= 60 ? '#FF3B30' : '#8E8E93'
          ),
          borderRadius: 8
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          y: {
            min: 0,
            max: 100,
            grid: { color: 'rgba(0, 0, 0, 0.05)' },
            ticks: { color: '#8E8E93' }
          },
          x: {
            grid: { display: false },
            ticks: { color: '#3A3A3C', maxRotation: 45 }
          }
        }
      }
    });
  }
};

// 统计数据获取工具
const StatsAPI = {
  baseUrl: '/api/stats',
  
  // 获取用户统计
  getUserStats: async (token) => {
    try {
      const response = await fetch(`${StatsAPI.baseUrl}/user`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token })
      });
      return await response.json();
    } catch (error) {
      console.error('获取用户统计失败:', error);
      return { success: false, error: error.message };
    }
  },
  
  // 获取班级统计
  getClassStats: async (token, className, dictationTitle = null) => {
    try {
      const body = { token, className };
      if (dictationTitle) body.dictationTitle = dictationTitle;
      
      const response = await fetch(`${StatsAPI.baseUrl}/class`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
      return await response.json();
    } catch (error) {
      console.error('获取班级统计失败:', error);
      return { success: false, error: error.message };
    }
  },
  
  // 获取错题分析
  getErrorAnalysis: async (token) => {
    try {
      const response = await fetch(`${StatsAPI.baseUrl}/errors`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token })
      });
      return await response.json();
    } catch (error) {
      console.error('获取错题分析失败:', error);
      return { success: false, error: error.message };
    }
  },
  
  // 添加成绩
  addScore: async (token, scoreData) => {
    try {
      const response = await fetch(`${StatsAPI.baseUrl}/add`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, ...scoreData })
      });
      return await response.json();
    } catch (error) {
      console.error('添加成绩失败:', error);
      return { success: false, error: error.message };
    }
  }
};

// 导出
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { StatsCharts, StatsAPI };
}