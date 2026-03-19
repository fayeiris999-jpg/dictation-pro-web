#!/usr/bin/env python3
"""
DictationPro AI - 后端 API 服务 (Python 版)
提供音频生成、自动批改、飞书同步、用户认证等功能
"""

import json
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import base64
from datetime import datetime

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

# 导入认证模块
from auth import user_manager

# 导入统计模块
from stats import stats_manager

# 导入导出模块
from export import export_manager

# 导入听写管理模块
from dictations import dictation_manager

# 导入自动批改模块
from grader import auto_grader

# 导入文件解析模块
from file_parser import file_parser

# 导入 AI 记忆技巧生成模块
from ai_memory import ai_generator

PORT = int(os.getenv('PORT', 3000))

# ========== 工具函数 ==========

def levenshtein_distance(s1, s2):
    """计算编辑距离"""
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = min(
                    dp[i-1][j] + 1,     # 删除
                    dp[i][j-1] + 1,     # 插入
                    dp[i-1][j-1] + 1    # 替换
                )
    
    return dp[m][n]

def normalize_text(text):
    """标准化文本"""
    return text.lower().replace('.', '').replace(',', '').replace('!', '').replace('?', '').replace(';', '').replace(':', '').strip()

def compare_words(student, standard, tolerance=0.1):
    """单词对比（支持容错）"""
    if student == standard:
        return True
    
    distance = levenshtein_distance(student, standard)
    max_len = max(len(student), len(standard))
    
    if max_len == 0:
        return True
    
    similarity = 1 - distance / max_len
    return similarity >= (1 - tolerance)

def identify_error_type(student, standard):
    """识别错误类型"""
    if not student or len(student) == 0:
        return 'omission'
    if student.lower() == standard.lower():
        return 'case_error'
    
    s1 = student.lower()
    s2 = standard.lower()
    
    if sorted(s1) == sorted(s2):
        return 'order_error'
    
    return 'spelling_error'

def generate_feedback(score, corrections):
    """生成反馈"""
    if score >= 90:
        return '太棒了！继续保持！🎉'
    elif score >= 70:
        return '不错！注意细节的拼写哦~'
    else:
        return '加油！建议多练习几遍，你可以的！💪'

def build_mock_audio():
    """生成模拟音频（用于测试）"""
    # 返回一个短的静音 MP3
    return "SUQzBAAAAAAAI1RTU0UAAAAPAAADTGF2ZjU4LjI5LjEwMAAAAAAAAAAAAAAA//tQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAWGluZwAAAA8AAAACAAADhAC7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7////////////////////////////////////////////////////////////AAAAAExhdmM1OC41NQAAAAAAAAAAAAAAACQCgAAAAAAAASXjLkYjAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA//tQZAAP8AAAaQAAAAgAAA0gAAABAAABpAAAACAAADSAAAAETEFNRTMuMTAwVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV"

def calculate_duration(words, speed, interval, repeats):
    """计算音频时长（估算）"""
    total_chars = sum(len(w.get('english', '')) for w in words)
    base_duration = total_chars / 15 * (1 / speed)
    total_duration = base_duration * repeats + (repeats - 1) * interval
    return round(total_duration)

# ========== API 处理 ==========

class APIHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        """处理 GET 请求"""
        parsed = urlparse(self.path)
        
        if parsed.path == '/api/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'status': 'ok',
                'timestamp': datetime.now().isoformat(),
                'services': {
                    'azureTTS': 'configured' if os.getenv('AZURE_TTS_KEY') else 'not configured',
                    'feishu': 'configured' if os.getenv('FEISHU_APP_ID') else 'not configured'
                }
            }
            self.wfile.write(json.dumps(response).encode())
            return
        
        if parsed.path.startswith('/api/export/download/'):
            self.handle_download_file(parsed)
            return
        
        if parsed.path == '/api/auth/me':
            self.handle_get_me(parsed)
            return
        
        # 静态文件服务
        if parsed.path.endswith('.html'):
            self.path = '/public' + parsed.path
            return SimpleHTTPRequestHandler.do_GET(self)
        
        self.send_error(404)
    
    def do_POST(self):
        """处理 POST 请求"""
        parsed = urlparse(self.path)
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        
        try:
            data = json.loads(body) if body else {}
        except:
            data = {}
        
        if parsed.path == '/api/audio/generate':
            self.handle_audio_generate(data)
        elif parsed.path == '/api/correct':
            self.handle_correct(data)
        elif parsed.path == '/api/feishu/sync':
            self.handle_feishu_sync(data)
        elif parsed.path == '/api/auth/register':
            self.handle_register(data)
        elif parsed.path == '/api/auth/login':
            self.handle_login(data)
        elif parsed.path == '/api/auth/logout':
            self.handle_logout(data)
        elif parsed.path == '/api/auth/classes':
            self.handle_list_classes(data)
        elif parsed.path == '/api/stats/add':
            self.handle_add_score(data)
        elif parsed.path == '/api/stats/user':
            self.handle_user_stats(data)
        elif parsed.path == '/api/stats/class':
            self.handle_class_stats(data)
        elif parsed.path == '/api/stats/errors':
            self.handle_error_analysis(data)
        elif parsed.path == '/api/stats/dictations':
            self.handle_dictation_list(data)
        elif parsed.path == '/api/export/excel':
            self.handle_export_excel(data)
        elif parsed.path == '/api/export/pdf':
            self.handle_export_pdf(data)
        elif parsed.path == '/api/dictation/create':
            self.handle_create_dictation(data)
        elif parsed.path == '/api/dictation/list':
            self.handle_list_dictations(data)
        elif parsed.path == '/api/dictation/get':
            self.handle_get_dictation(data)
        elif parsed.path == '/api/dictation/submit':
            self.handle_submit_attempt(data)
        elif parsed.path == '/api/dictation/attempts':
            self.handle_get_attempts(data)
        elif parsed.path == '/api/file/parse':
            self.handle_file_parse(data)
        elif parsed.path == '/api/export/batch':
            self.handle_batch_export(data)
        elif parsed.path == '/api/export/error-book':
            self.handle_error_book_export(data)
        elif parsed.path == '/api/report/generate':
            self.handle_learning_report(data)
        elif parsed.path == '/api/ai/memory-techniques':
            self.handle_memory_techniques(data)
        elif parsed.path == '/api/ai/fill-blank':
            self.handle_fill_blank_exercise(data)
        elif parsed.path == '/api/ai/generate-image':
            self.handle_generate_word_image(data)
        elif parsed.path == '/api/ai/generate-audio':
            self.handle_generate_word_audio(data)
        elif parsed.path == '/api/ai/generate-story':
            self.handle_generate_story(data)
        else:
            self.send_error(404)
    
    def handle_audio_generate(self, data):
        """生成音频"""
        words = data.get('words', [])
        voice = data.get('voice', 'en-US-JennyNeural')
        speed = data.get('speed', 0.9)
        interval = data.get('interval', 3)
        repeats = data.get('repeats', 2)
        
        # 检查是否配置 Azure TTS
        azure_key = os.getenv('AZURE_TTS_KEY')
        
        if azure_key and azure_key != 'YOUR_AZURE_TTS_KEY':
            # TODO: 实现 Azure TTS 调用
            print("⚠️ Azure TTS 已配置但未实现调用")
        
        # 返回模拟音频
        mock_audio = build_mock_audio()
        duration = calculate_duration(words, speed, interval, repeats)
        
        response = {
            'success': True,
            'audioUrl': f'data:audio/mp3;base64,{mock_audio}',
            'duration': duration,
            'warning': '模拟音频 - 请配置 Azure TTS 密钥' if not azure_key else None
        }
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def handle_correct(self, data):
        """自动批改"""
        student_answer = data.get('studentAnswer', '')
        standard_answer = data.get('standardAnswer', '')
        tolerance = data.get('tolerance', 0.1)
        
        # 标准化
        normalized_student = normalize_text(student_answer)
        normalized_standard = normalize_text(standard_answer)
        
        # 分词
        student_words = [w for w in normalized_student.split() if w]
        standard_words = [w for w in normalized_standard.split() if w]
        
        # 逐词批改
        corrections = []
        correct_count = 0
        
        for i in range(len(standard_words)):
            standard = standard_words[i]
            student = student_words[i] if i < len(student_words) else ''
            
            is_correct = compare_words(student, standard, tolerance)
            
            if is_correct:
                correct_count += 1
            else:
                corrections.append({
                    'index': i,
                    'expected': standard,
                    'actual': student,
                    'type': identify_error_type(student, standard)
                })
        
        # 计算得分
        total_words = len(standard_words)
        score = round((correct_count / total_words) * 100) if total_words > 0 else 0
        correct_rate = f"{(correct_count / total_words * 100):.1f}" if total_words > 0 else '0'
        
        report = {
            'score': score,
            'correctRate': correct_rate,
            'totalWords': total_words,
            'correctCount': correct_count,
            'errorCount': len(corrections),
            'corrections': corrections,
            'feedback': generate_feedback(score, corrections)
        }
        
        response = {
            'success': True,
            'report': report
        }
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def handle_feishu_sync(self, data):
        """飞书同步"""
        student_name = data.get('studentName', '')
        dictation_date = data.get('dictationDate', '')
        class_name = data.get('className', '')
        content = data.get('content', '')
        score = data.get('score', 0)
        correct_rate = data.get('correctRate', 0)
        mistakes = data.get('mistakes', [])
        
        # 检查是否配置飞书 API
        feishu_app_id = os.getenv('FEISHU_APP_ID')
        
        if feishu_app_id and feishu_app_id != 'YOUR_FEISHU_APP_ID':
            # TODO: 实现飞书 API 调用
            print("⚠️ 飞书 API 已配置但未实现调用")
        
        response = {
            'success': True,
            'recordId': f'mock_{datetime.now().timestamp()}',
            'message': '成绩已同步到飞书',
            'warning': '模拟同步 - 请配置飞书 API' if not feishu_app_id else None
        }
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    # ========== 认证相关处理 ==========
    
    def handle_register(self, data):
        """用户注册"""
        username = data.get('username', '')
        password = data.get('password', '')
        role = data.get('role', 'student')
        display_name = data.get('displayName', '')
        class_name = data.get('className', '')
        
        if not username or not password:
            response = {'success': False, 'error': '用户名和密码不能为空'}
            self._send_json(response)
            return
        
        result = user_manager.register(username, password, role, display_name, class_name)
        self._send_json(result)
    
    def handle_login(self, data):
        """用户登录"""
        username = data.get('username', '')
        password = data.get('password', '')
        
        if not username or not password:
            response = {'success': False, 'error': '用户名和密码不能为空'}
            self._send_json(response)
            return
        
        result = user_manager.login(username, password)
        self._send_json(result)
    
    def handle_get_me(self, parsed):
        """获取当前用户信息"""
        # 从 URL 参数获取 token
        params = parse_qs(parsed.query)
        token = params.get('token', [None])[0]
        
        if not token:
            # 尝试从 Authorization header 获取
            auth_header = self.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]
        
        if not token:
            response = {'success': False, 'error': '未提供 Token'}
            self._send_json(response, 401)
            return
        
        user = user_manager.verify_token(token)
        if user:
            response = {'success': True, 'user': user}
        else:
            response = {'success': False, 'error': 'Token 无效或已过期'}
            self._send_json(response, 401)
            return
        
        self._send_json(response)
    
    def handle_download_file(self, parsed):
        """下载导出文件"""
        # 提取文件名
        filename = parsed.path.replace('/api/export/download/', '')
        
        # 安全检查：防止目录遍历攻击
        if '..' in filename or filename.startswith('/'):
            self.send_error(400)
            return
        
        # 构建文件路径
        export_dir = export_manager.output_dir
        filepath = os.path.join(export_dir, filename)
        
        # 检查文件是否存在
        if not os.path.exists(filepath):
            response = {'success': False, 'error': '文件不存在'}
            self._send_json(response, 404)
            return
        
        # 确定 Content-Type
        if filename.endswith('.pdf'):
            content_type = 'application/pdf'
        elif filename.endswith('.xlsx'):
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        else:
            content_type = 'application/octet-stream'
        
        # 发送文件
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
        self.send_header('Content-Length', os.path.getsize(filepath))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        with open(filepath, 'rb') as f:
            self.wfile.write(f.read())
    
    def handle_logout(self, data):
        """用户登出（客户端删除 token 即可）"""
        response = {'success': True, 'message': '已登出'}
        self._send_json(response)
    
    def handle_list_classes(self, data):
        """获取班级列表"""
        classes = user_manager.list_all_classes()
        response = {'success': True, 'classes': classes}
        self._send_json(response)
    
    # ========== 统计相关处理 ==========
    
    def _get_token_from_request(self, parsed, data):
        """从请求中获取 Token"""
        token = parsed.query.split('token=')[-1] if 'token=' in parsed.query else None
        if not token:
            token = data.get('token')
        if not token:
            auth_header = self.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]
        return token
    
    def handle_add_score(self, data):
        """添加成绩记录"""
        token = data.get('token')
        user = user_manager.verify_token(token) if token else None
        
        if not user:
            response = {'success': False, 'error': '未授权'}
            self._send_json(response, 401)
            return
        
        result = stats_manager.add_score(
            user_id=user['user_id'],
            username=user['username'],
            class_name=user.get('class_name', '') or data.get('className', ''),
            dictation_title=data.get('dictationTitle', ''),
            score=data.get('score', 0),
            correct_rate=data.get('correctRate', 0),
            total_words=data.get('totalWords', 0),
            correct_count=data.get('correctCount', 0),
            mistakes=data.get('mistakes', [])
        )
        self._send_json(result)
    
    def handle_user_stats(self, data):
        """获取用户统计"""
        token = self._get_token_from_request(urlparse(self.path), data)
        user = user_manager.verify_token(token) if token else None
        
        if not user:
            response = {'success': False, 'error': '未授权'}
            self._send_json(response, 401)
            return
        
        stats = stats_manager.get_user_stats(user['user_id'])
        response = {'success': True, 'stats': stats}
        self._send_json(response)
    
    def handle_class_stats(self, data):
        """获取班级统计"""
        token = self._get_token_from_request(urlparse(self.path), data)
        user = user_manager.verify_token(token) if token else None
        
        if not user or user['role'] != 'teacher':
            response = {'success': False, 'error': '未授权或权限不足'}
            self._send_json(response, 401)
            return
        
        class_name = data.get('className', user.get('class_name'))
        dictation_title = data.get('dictationTitle')
        
        stats = stats_manager.get_class_stats(class_name, dictation_title)
        response = {'success': True, 'stats': stats}
        self._send_json(response)
    
    def handle_error_analysis(self, data):
        """获取错题分析"""
        token = self._get_token_from_request(urlparse(self.path), data)
        user = user_manager.verify_token(token) if token else None
        
        if not user:
            response = {'success': False, 'error': '未授权'}
            self._send_json(response, 401)
            return
        
        errors = stats_manager.get_error_analysis(user['user_id'])
        response = {'success': True, 'errors': errors}
        self._send_json(response)
    
    def handle_dictation_list(self, data):
        """获取听写任务列表"""
        token = self._get_token_from_request(urlparse(self.path), data)
        user = user_manager.verify_token(token) if token else None
        
        if not user:
            response = {'success': False, 'error': '未授权'}
            self._send_json(response, 401)
            return
        
        class_name = data.get('className', user.get('class_name'))
        titles = stats_manager.get_dictation_list(class_name)
        response = {'success': True, 'dictations': titles}
        self._send_json(response)
    
    # ========== 听写任务相关处理 ==========
    
    def handle_create_dictation(self, data):
        """创建听写任务"""
        token = data.get('token')
        user = user_manager.verify_token(token) if token else None
        
        if not user or user['role'] != 'teacher':
            response = {'success': False, 'error': '未授权或权限不足'}
            self._send_json(response, 401)
            return
        
        title = data.get('title', '')
        class_name = data.get('className', '')
        word_list = data.get('wordList', '')
        
        if not title or not class_name:
            response = {'success': False, 'error': '标题和班级不能为空'}
            self._send_json(response, 400)
            return
        
        result = dictation_manager.create_dictation(
            title=title,
            class_name=class_name,
            teacher_id=user['user_id'],
            word_list_text=word_list
        )
        
        self._send_json(result)
    
    def handle_list_dictations(self, data):
        """获取听写任务列表"""
        token = self._get_token_from_request(urlparse(self.path), data)
        user = user_manager.verify_token(token) if token else None
        
        if not user:
            response = {'success': False, 'error': '未授权'}
            self._send_json(response, 401)
            return
        
        class_name = data.get('className', user.get('class_name'))
        dictations = dictation_manager.get_dictations_by_class(class_name)
        
        # 简化返回数据
        simplified = [{
            'id': d['id'],
            'title': d['title'],
            'word_count': d['word_count'],
            'created_at': d['created_at'],
            'attempt_count': len(d['student_attempts'])
        } for d in dictations]
        
        response = {'success': True, 'dictations': simplified}
        self._send_json(response)
    
    def handle_get_dictation(self, data):
        """获取听写任务详情"""
        token = self._get_token_from_request(urlparse(self.path), data)
        user = user_manager.verify_token(token) if token else None
        
        if not user:
            response = {'success': False, 'error': '未授权'}
            self._send_json(response, 401)
            return
        
        dictation_id = data.get('dictationId', '')
        dictation = dictation_manager.get_dictation(dictation_id)
        
        if not dictation:
            response = {'success': False, 'error': '听写任务不存在'}
            self._send_json(response, 404)
            return
        
        # 对学生隐藏答案
        if user['role'] == 'student':
            words = [{'english': w['english'], 'chinese': w['chinese']} for w in dictation['words']]
        else:
            words = dictation['words']
        
        response = {
            'success': True,
            'dictation': {
                'id': dictation['id'],
                'title': dictation['title'],
                'words': words,
                'word_count': dictation['word_count'],
                'duration': dictation['duration']
            }
        }
        self._send_json(response)
    
    def handle_submit_attempt(self, data):
        """提交听写作答"""
        token = data.get('token')
        user = user_manager.verify_token(token) if token else None
        
        if not user or user['role'] != 'student':
            response = {'success': False, 'error': '未授权或权限不足'}
            self._send_json(response, 401)
            return
        
        dictation_id = data.get('dictationId', '')
        answers = data.get('answers', [])
        
        # 获取听写任务
        dictation = dictation_manager.get_dictation(dictation_id)
        if not dictation:
            response = {'success': False, 'error': '听写任务不存在'}
            self._send_json(response, 404)
            return
        
        # 提取正确答案
        expected_words = [w['english'] for w in dictation['words']]
        
        # 自动批改
        grade_result = auto_grader.grade(expected_words, answers)
        
        # 格式化错误详情
        mistakes = []
        for m in grade_result['mistakes']:
            mistakes.append({
                'word': m['word'],
                'expected': m['expected'],
                'got': m['got'],
                'error_type': m['type']
            })
        
        # 提交作答记录
        submit_result = dictation_manager.submit_attempt(
            dictation_id=dictation_id,
            student_id=user['user_id'],
            username=user['username'],
            answers=answers,
            score=grade_result['score'],
            correct_rate=grade_result['correct_rate'],
            mistakes=mistakes
        )
        
        # 同步到成绩统计
        if submit_result['success']:
            stats_manager.add_score(
                user_id=user['user_id'],
                username=user['username'],
                class_name=user.get('class_name', ''),
                dictation_title=dictation['title'],
                score=grade_result['score'],
                correct_rate=grade_result['correct_rate'],
                total_words=grade_result['total_count'],
                correct_count=grade_result['correct_count'],
                mistakes=[m['word'] for m in mistakes]
            )
        
        # 返回结果
        response = {
            'success': submit_result['success'],
            'score': grade_result['score'],
            'correct_rate': grade_result['correct_rate'],
            'correct_count': grade_result['correct_count'],
            'total_count': grade_result['total_count'],
            'mistakes': mistakes,
            'analysis': auto_grader.get_error_analysis(mistakes)
        }
        self._send_json(response)
    
    def handle_get_attempts(self, data):
        """获取作答记录"""
        token = self._get_token_from_request(urlparse(self.path), data)
        user = user_manager.verify_token(token) if token else None
        
        if not user:
            response = {'success': False, 'error': '未授权'}
            self._send_json(response, 401)
            return
        
        dictation_id = data.get('dictationId', '')
        
        if user['role'] == 'student':
            attempts = dictation_manager.get_student_attempts(dictation_id, user['user_id'])
        else:
            attempts = dictation_manager.get_class_attempts(dictation_id)
        
        response = {'success': True, 'attempts': attempts}
        self._send_json(response)
    
    def handle_export_excel(self, data):
        """导出 Excel 错题本"""
        token = data.get('token')
        user = user_manager.verify_token(token) if token else None
        
        if not user:
            response = {'success': False, 'error': '未授权'}
            self._send_json(response, 401)
            return
        
        result = export_manager.export_to_excel(
            user_id=user['user_id'],
            username=user['display_name'] or user['username'],
            class_name=user.get('class_name')
        )
        
        if result['success']:
            # 返回文件下载 URL
            filename = result['filename']
            result['download_url'] = f'/api/export/download/{filename}'
        
        self._send_json(result)
    
    def handle_export_pdf(self, data):
        """导出 PDF 错题本"""
        token = data.get('token')
        user = user_manager.verify_token(token) if token else None
        
        if not user:
            response = {'success': False, 'error': '未授权'}
            self._send_json(response, 401)
            return
        
        result = export_manager.export_to_pdf(
            user_id=user['user_id'],
            username=user['display_name'] or user['username'],
            class_name=user.get('class_name')
        )
        
        if result['success']:
            filename = result['filename']
            result['download_url'] = f'/api/export/download/{filename}'
        
        self._send_json(result)
    
    def handle_file_parse(self, data: dict):
        """解析上传的文件（Word/PDF/图片）"""
        file_data = data.get('file', '')
        file_type = data.get('type', 'image')
        
        if not file_data:
            self._send_json({'success': False, 'error': '未提供文件内容'}, 400)
            return
        
        # 调用文件解析器
        result = file_parser.parse_file(file_data, file_type)
        self._send_json(result)
    
    def handle_batch_export(self, data: dict):
        """批量导出成绩（Excel）"""
        token = data.get('token', '')
        class_name = data.get('class_name', '')
        start_date = data.get('start_date', '')
        end_date = data.get('end_date', '')
        
        user = user_manager.verify_token(token)
        if not user or user.get('role') != 'teacher':
            self._send_json({'success': False, 'error': '未授权'}, 401)
            return
        
        result = export_manager.export_class_scores_batch(
            class_name=class_name,
            start_date=start_date,
            end_date=end_date
        )
        
        if result['success']:
            filename = result['filename']
            result['download_url'] = f'/api/export/download/{filename}'
        
        self._send_json(result)
    
    def handle_error_book_export(self, data: dict):
        """导出错题本（PDF）"""
        token = data.get('token', '')
        user_id = data.get('user_id', '')
        
        user = user_manager.verify_token(token)
        if not user:
            self._send_json({'success': False, 'error': '未授权'}, 401)
            return
        
        result = export_manager.export_error_book_pdf(
            user_id=user['user_id'] if not user_id else user_id,
            username=user['display_name'] or user['username']
        )
        
        if result['success']:
            filename = result['filename']
            result['download_url'] = f'/api/export/download/{filename}'
        
        self._send_json(result)
    
    def handle_learning_report(self, data: dict):
        """生成学习报告（PDF）"""
        token = data.get('token', '')
        user_id = data.get('user_id', '')
        period = data.get('period', 'weekly')  # weekly/monthly
        
        user = user_manager.verify_token(token)
        if not user:
            self._send_json({'success': False, 'error': '未授权'}, 401)
            return
        
        result = export_manager.generate_learning_report(
            user_id=user['user_id'] if not user_id else user_id,
            username=user['display_name'] or user['username'],
            period=period
        )
        
        if result['success']:
            filename = result['filename']
            result['download_url'] = f'/api/export/download/{filename}'
        
        self._send_json(result)
    
    def handle_memory_techniques(self, data: dict):
        """生成 AI 单词记忆技巧"""
        token = data.get('token', '')
        words = data.get('words', [])
        
        # 验证登录（可选）
        user = user_manager.verify_token(token)
        
        if not words:
            self._send_json({'success': False, 'error': '请提供单词列表'}, 400)
            return
        
        # 调用 AI 生成器
        result = ai_generator.generate_memory_techniques(words)
        self._send_json(result)
    
    def handle_fill_blank_exercise(self, data: dict):
        """生成挖空练习"""
        token = data.get('token', '')
        words = data.get('words', [])
        difficulty = data.get('difficulty', 'medium')
        
        if not words:
            self._send_json({'success': False, 'error': '请提供单词列表'}, 400)
            return
        
        # 生成挖空练习
        result = ai_generator.generate_fill_blank_exercise(words, difficulty)
        self._send_json(result)
    
    def handle_generate_word_image(self, data: dict):
        """生成单词图片（AI 绘画）"""
        word = data.get('word', '')
        image_prompt = data.get('image_prompt', f'A {word}, photorealistic, 4k')
        
        if not word:
            self._send_json({'success': False, 'error': '请提供单词'}, 400)
            return
        
        result = ai_generator.generate_word_image(word, image_prompt)
        self._send_json(result)
    
    def handle_generate_word_audio(self, data: dict):
        """生成单词发音（Azure TTS）"""
        word = data.get('word', '')
        text = data.get('text', '')
        
        if not word:
            self._send_json({'success': False, 'error': '请提供单词'}, 400)
            return
        
        result = ai_generator.generate_word_audio(word, text)
        self._send_json(result)
    
    def handle_generate_story(self, data: dict):
        """生成英文故事（包含错词）"""
        token = data.get('token', '')
        words = data.get('words', [])
        level = data.get('level', 'B1')  # A1/A2/B1/B2/C1/C2
        style = data.get('style', 'story')  # suspense/horror/comedy/news/fairy/scifi
        
        if not words:
            self._send_json({'success': False, 'error': '请提供错词列表'}, 400)
            return
        
        result = ai_generator.generate_english_story(words, level, style)
        self._send_json(result)
    
    def _send_json(self, data: dict, status: int = 200):
        """发送 JSON 响应"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def do_OPTIONS(self):
        """处理 CORS 预检请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {args[0]}")

# ========== 启动服务器 ==========

if __name__ == '__main__':
    # 创建 public 目录的符号链接或复制文件
    import shutil
    public_dir = os.path.join(os.path.dirname(__file__), 'public')
    if not os.path.exists(public_dir):
        os.makedirs(public_dir)
    
    # 从上级目录复制 HTML 文件
    src_dir = os.path.dirname(os.path.dirname(__file__))
    for f in ['teacher-v5.html', 'student-v5.html']:
        src = os.path.join(src_dir, 'public', f)
        dst = os.path.join(public_dir, f)
        if os.path.exists(src) and not os.path.exists(dst):
            shutil.copy2(src, dst)
    
    server = HTTPServer(('localhost', PORT), APIHandler)
    print(f"🚀 DictationPro Backend (Python) running on http://localhost:{PORT}")
    print(f"📊 Health check: http://localhost:{PORT}/api/health")
    print(f"👨‍🏫 Teacher: http://localhost:{PORT}/teacher-v5.html")
    print(f"👨‍🎓 Student: http://localhost:{PORT}/student-v5.html")
    print("Press Ctrl+C to stop")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
        server.shutdown()
