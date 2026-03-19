#!/usr/bin/env python3
"""
DictationPro API 集成测试

运行测试:
    python -m pytest tests/test_api.py -v

前提条件:
    - 后端服务正在运行 (python server.py)
    - 测试数据库为空或使用测试数据
"""

import pytest
import requests
import json
import time

BASE_URL = 'http://localhost:3000'


class TestHealthCheck:
    """健康检查测试"""
    
    def test_health_endpoint(self):
        """测试健康检查端点"""
        response = requests.get(f'{BASE_URL}/api/health')
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['status'] == 'ok'
        assert 'timestamp' in data
        assert 'services' in data


class TestAuthAPI:
    """认证 API 测试"""
    
    def test_register_student(self):
        """测试学生注册"""
        payload = {
            'username': f'test_student_{int(time.time())}',
            'password': 'test123',
            'role': 'student',
            'displayName': '测试学生',
            'className': '25 级 IB IELTS 听力'
        }
        
        response = requests.post(
            f'{BASE_URL}/api/auth/register',
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'token' in data
    
    def test_register_teacher(self):
        """测试教师注册"""
        payload = {
            'username': f'test_teacher_{int(time.time())}',
            'password': 'test123',
            'role': 'teacher',
            'displayName': '测试教师'
        }
        
        response = requests.post(
            f'{BASE_URL}/api/auth/register',
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
    
    def test_login(self):
        """测试登录"""
        # 先注册
        username = f'test_login_{int(time.time())}'
        register_payload = {
            'username': username,
            'password': 'test123',
            'role': 'student'
        }
        
        requests.post(
            f'{BASE_URL}/api/auth/register',
            json=register_payload
        )
        
        # 再登录
        login_payload = {
            'username': username,
            'password': 'test123'
        }
        
        response = requests.post(
            f'{BASE_URL}/api/auth/login',
            json=login_payload
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'token' in data
        # 登录返回扁平结构，不是嵌套的 user 对象
        assert 'user_id' in data or 'user' in data


class TestCorrectAPI:
    """批改 API 测试"""
    
    def test_correct_perfect(self):
        """测试完全正确的批改"""
        payload = {
            'studentAnswer': 'apple, banana, orange',
            'standardAnswer': 'apple, banana, orange',
            'tolerance': 0.1
        }
        
        response = requests.post(
            f'{BASE_URL}/api/correct',
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['report']['score'] == 100
    
    def test_correct_errors(self):
        """测试错误答案的批改"""
        payload = {
            'studentAnswer': 'aple, bananna, oringe',
            'standardAnswer': 'apple, banana, orange',
            'tolerance': 0.1
        }
        
        response = requests.post(
            f'{BASE_URL}/api/correct',
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['report']['errorCount'] == 3


class TestAIStoryAPI:
    """AI 故事生成 API 测试"""
    
    def test_generate_story_fairy(self):
        """测试童话故事生成"""
        payload = {
            'words': [
                {'english': 'apple', 'chinese': '苹果'},
                {'english': 'banana', 'chinese': '香蕉'}
            ],
            'level': 'B1',
            'style': 'fairy'
        }
        
        response = requests.post(
            f'{BASE_URL}/api/ai/generate-story',
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'story' in data
        assert 'content_en' in data['story']
        assert 'content_zh' in data['story']
    
    def test_generate_story_suspense(self):
        """测试悬疑故事生成"""
        payload = {
            'words': [
                {'english': 'apple', 'chinese': '苹果'}
            ],
            'level': 'A2',
            'style': 'suspense'
        }
        
        response = requests.post(
            f'{BASE_URL}/api/ai/generate-story',
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['story']['style'] == 'suspense'
    
    def test_generate_story_all_styles(self):
        """测试所有故事风格"""
        styles = ['fairy', 'suspense', 'horror', 'comedy', 'news', 'scifi']
        
        for style in styles:
            payload = {
                'words': [{'english': 'apple', 'chinese': '苹果'}],
                'level': 'B1',
                'style': style
            }
            
            response = requests.post(
                f'{BASE_URL}/api/ai/generate-story',
                json=payload
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True


class TestMemoryTechniquesAPI:
    """记忆技巧 API 测试"""
    
    def test_generate_techniques(self):
        """测试记忆技巧生成"""
        payload = {
            'words': [
                {'english': 'apple', 'chinese': '苹果'},
                {'english': 'banana', 'chinese': '香蕉'}
            ]
        }
        
        response = requests.post(
            f'{BASE_URL}/api/ai/memory-techniques',
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert len(data['techniques']) >= 1
        
        # 检查必要字段
        technique = data['techniques'][0]
        assert 'word' in technique
        assert 'phonetic' in technique
        assert 'audio_tip' in technique
        assert 'shape_tip' in technique
        assert 'example_sentences' in technique


class TestStatsAPI:
    """统计 API 测试"""
    
    def test_add_and_get_score(self):
        """测试添加和获取成绩"""
        # 先注册
        username = f'test_stats_{int(time.time())}'
        register_payload = {
            'username': username,
            'password': 'test123',
            'role': 'student'
        }
        
        register_response = requests.post(
            f'{BASE_URL}/api/auth/register',
            json=register_payload
        )
        
        token = register_response.json()['token']
        
        # 添加成绩
        score_payload = {
            'token': token,
            'dictationId': 'test_dictation',
            'dictationTitle': 'Test Vocabulary',
            'score': 85,
            'correctCount': 17,
            'totalWords': 20
        }
        
        add_response = requests.post(
            f'{BASE_URL}/api/stats/add',
            json=score_payload
        )
        
        assert add_response.status_code == 200
        
        # 获取统计
        stats_response = requests.post(
            f'{BASE_URL}/api/stats/user',
            json={'token': token}
        )
        
        assert stats_response.status_code == 200
        data = stats_response.json()
        assert data['success'] is True
        assert data['stats']['total_dictations'] >= 1


class TestExportAPI:
    """导出 API 测试"""
    
    def test_export_excel(self):
        """测试 Excel 导出"""
        # 使用测试账户
        login_payload = {
            'username': 'teststudent',
            'password': 'test123'
        }
        
        login_response = requests.post(
            f'{BASE_URL}/api/auth/login',
            json=login_payload
        )
        
        if login_response.status_code == 200:
            token = login_response.json()['token']
            
            export_response = requests.post(
                f'{BASE_URL}/api/export/excel',
                json={'token': token}
            )
            
            # 如果没有数据，可能返回失败
            if export_response.status_code == 200:
                data = export_response.json()
                if data.get('success'):
                    assert 'download_url' in data


def run_tests():
    """运行所有测试"""
    pytest.main([__file__, '-v'])


if __name__ == '__main__':
    print("Starting API Integration Tests...")
    print(f"Testing base URL: {BASE_URL}")
    
    # 先检查服务是否运行
    try:
        response = requests.get(f'{BASE_URL}/api/health', timeout=5)
        if response.status_code == 200:
            print("✓ Backend service is running")
            run_tests()
        else:
            print("✗ Backend service returned unexpected status")
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to backend service")
        print("Please start the server: python server.py")
    except Exception as e:
        print(f"✗ Error: {e}")
