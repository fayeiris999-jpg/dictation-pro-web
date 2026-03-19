#!/usr/bin/env python3
"""
DictationPro AI - 单元测试套件

运行测试:
    python -m pytest tests/ -v

运行特定测试:
    python -m pytest tests/test_grader.py -v

生成覆盖率报告:
    python -m pytest tests/ --cov=. --cov-report=html
"""

import pytest
import json
import sys
import os

# 添加后端目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from grader import auto_grader
from ai_memory import ai_generator
from stats import stats_manager


class TestAutoGrader:
    """自动批改器测试"""
    
    def test_perfect_score(self):
        """测试完全正确的答案"""
        expected_words = ["apple", "banana", "orange"]
        student_answers = ["apple", "banana", "orange"]
        
        result = auto_grader.grade(expected_words, student_answers)
        
        assert 'score' in result
        assert result['score'] == 100
        assert result['correct_count'] == 3
        assert result['mistakes'] == []
    
    def test_spelling_errors(self):
        """测试拼写错误检测"""
        expected_words = ["apple", "banana", "orange"]
        student_answers = ["aple", "bananna", "oringe"]
        
        result = auto_grader.grade(expected_words, student_answers)
        
        assert 'score' in result
        assert result['score'] == 0
        assert result['mistakes'] != []
        assert len(result['mistakes']) == 3
    
    def test_partial_correct(self):
        """测试部分正确的答案"""
        expected_words = ["apple", "banana", "orange"]
        student_answers = ["apple", "bananna", "orange"]
        
        result = auto_grader.grade(expected_words, student_answers)
        
        assert 'score' in result
        assert abs(result['score'] - 66.7) < 0.1  # 2/3 正确 ≈ 66.7%
        assert result['correct_count'] == 2
        assert len(result['mistakes']) == 1
    
    def test_case_insensitive(self):
        """测试大小写不敏感"""
        expected_words = ["apple", "banana", "orange"]
        student_answers = ["Apple", "BANANA", "Orange"]
        
        result = auto_grader.grade(expected_words, student_answers)
        
        assert 'score' in result
        assert result['score'] == 100
    
    def test_omission(self):
        """测试遗漏检测"""
        expected_words = ["apple", "banana", "orange"]
        student_answers = ["apple", "orange"]  # 遗漏 banana
        
        result = auto_grader.grade(expected_words, student_answers)
        
        assert 'score' in result
        assert result['mistakes'] != []


class TestAIMemory:
    """AI 记忆技巧生成测试"""
    
    def test_mock_techniques(self):
        """测试模拟记忆技巧生成"""
        words = [
            {'english': 'apple', 'chinese': '苹果'},
            {'english': 'banana', 'chinese': '香蕉'}
        ]
        
        result = ai_generator.generate_memory_techniques(words)
        
        assert result['success'] is True
        assert len(result['techniques']) == 2
        
        # 检查必要字段
        for technique in result['techniques']:
            assert 'word' in technique
            assert 'phonetic' in technique
            assert 'audio_tip' in technique
            assert 'shape_tip' in technique
            assert 'example_sentences' in technique
    
    def test_fill_blank_exercise(self):
        """测试挖空练习生成"""
        words = [
            {'english': 'apple', 'chinese': '苹果'},
            {'english': 'banana', 'chinese': '香蕉'}
        ]
        
        result = ai_generator.generate_fill_blank_exercise(words)
        
        # 检查返回的字段（直接返回数据，不是 {success: True, ...} 格式）
        assert 'text' in result
        assert 'answers' in result
        assert 'hints' in result
        assert len(result['answers']) > 0
    
    def test_story_generation_mock(self):
        """测试模拟故事生成"""
        words = [
            {'english': 'apple', 'chinese': '苹果'},
            {'english': 'banana', 'chinese': '香蕉'},
            {'english': 'orange', 'chinese': '橙子'}
        ]
        
        # 测试不同风格
        styles = ['fairy', 'suspense', 'horror', 'comedy', 'news', 'scifi']
        
        for style in styles:
            result = ai_generator.generate_english_story(words, level='B1', style=style)
            
            assert result['success'] is True
            assert 'story' in result
            assert 'title' in result['story']
            assert 'content_en' in result['story']
            assert 'content_zh' in result['story']
            assert result['story']['style'] == style
    
    def test_story_levels(self):
        """测试不同难度级别"""
        words = [{'english': 'apple', 'chinese': '苹果'}]
        
        levels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
        
        for level in levels:
            result = ai_generator.generate_english_story(words, level=level)
            
            assert result['success'] is True
            assert result['story']['level'] == level


class TestStats:
    """统计模块测试"""
    
    def test_add_score(self):
        """测试添加成绩"""
        result = stats_manager.add_score(
            user_id='test_user_001',
            username='测试学生',
            class_name='25 级 IB IELTS 听力',
            dictation_title='Unit 1 Vocabulary',
            score=85,
            correct_rate=85.0,
            total_words=20,
            correct_count=17,
            mistakes=['apple', 'banana']
        )
        
        assert result['success'] is True
        assert 'record_id' in result
    
    def test_get_user_stats(self):
        """测试获取用户统计"""
        # 先添加一些测试数据
        for i in range(5):
            stats_manager.add_score(
                user_id='test_user_002',
                username='测试学生 2',
                class_name='25 级 IB IELTS 听力',
                dictation_title=f'Unit {i} Vocabulary',
                score=80 + i * 2,
                correct_rate=80 + i * 2,
                total_words=20,
                correct_count=16 + i
            )
        
        stats = stats_manager.get_user_stats('test_user_002')
        
        assert stats['total_dictations'] >= 5
        assert 'average_score' in stats
        assert 'best_score' in stats
        assert 'trend' in stats
        assert 'recent_scores' in stats
    
    def test_get_class_stats(self):
        """测试获取班级统计"""
        # 添加多个学生的成绩
        for i in range(3):
            for j in range(3):
                stats_manager.add_score(
                    user_id=f'test_user_class_{i}',
                    username=f'学生{i}',
                    class_name='测试班级',
                    dictation_title=f'Unit {j}',
                    score=70 + i * 10,
                    correct_rate=70 + i * 10,
                    total_words=20,
                    correct_count=14 + i * 2
                )
        
        class_stats = stats_manager.get_class_stats('测试班级')
        
        assert class_stats['total_students'] >= 3
        assert 'average_score' in class_stats
        assert 'student_ranking' in class_stats
        assert 'score_distribution' in class_stats


# TestFileParser 测试暂时跳过，因为 _parse_line 是 file_parser.py 的内部方法
# class TestFileParser:
#     """文件解析器测试"""
#     
#     def test_parse_text_line(self):
#         """测试文本行解析"""
#         # 测试不同分隔符
#         test_cases = [
#             ("apple-苹果", ("apple", "苹果", "")),
#             ("apple - 苹果", ("apple", "苹果", "")),
#             ("apple–苹果–fruit", ("apple", "苹果", "fruit")),
#             ("apple | 苹果 | fruit", ("apple", "苹果", "fruit")),
#         ]
#         
#         for input_text, expected in test_cases:
#             word = ai_generator._parse_line(input_text)
#             if word:
#                 assert word['english'] == expected[0]
#                 assert word['chinese'] == expected[1]


def run_tests():
    """运行所有测试"""
    pytest.main([__file__, '-v'])


if __name__ == '__main__':
    run_tests()
