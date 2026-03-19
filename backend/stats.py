#!/usr/bin/env python3
"""
DictationPro AI - 成绩统计模块
提供学生/班级成绩统计分析
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
from collections import defaultdict

class StatsManager:
    """成绩统计管理"""
    
    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir or os.path.join(os.path.dirname(__file__), 'data')
        self.scores_file = os.path.join(self.data_dir, 'scores.json')
        self._ensure_data_dir()
    
    def _ensure_data_dir(self):
        """确保数据目录存在"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        # 初始化成绩文件
        if not os.path.exists(self.scores_file):
            self._save_scores([])
    
    def _load_scores(self) -> List[Dict]:
        """加载成绩数据"""
        try:
            with open(self.scores_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    def _save_scores(self, scores: List[Dict]):
        """保存成绩数据"""
        with open(self.scores_file, 'w', encoding='utf-8') as f:
            json.dump(scores, f, ensure_ascii=False, indent=2)
    
    def add_score(self, user_id: str, username: str, class_name: str,
                  dictation_title: str, score: int, correct_rate: float,
                  total_words: int, correct_count: int, mistakes: List[str] = None) -> Dict:
        """添加成绩记录"""
        scores = self._load_scores()
        
        record = {
            'id': f"score_{datetime.now().timestamp()}",
            'user_id': user_id,
            'username': username,
            'class_name': class_name,
            'dictation_title': dictation_title,
            'score': score,
            'correct_rate': correct_rate,
            'total_words': total_words,
            'correct_count': correct_count,
            'mistakes': mistakes or [],
            'created_at': datetime.now().isoformat()
        }
        
        scores.append(record)
        self._save_scores(scores)
        
        return {'success': True, 'record_id': record['id']}
    
    def get_user_scores(self, user_id: str, limit: int = 50) -> List[Dict]:
        """获取用户成绩列表"""
        scores = self._load_scores()
        user_scores = [s for s in scores if s['user_id'] == user_id]
        user_scores.sort(key=lambda x: x['created_at'], reverse=True)
        return user_scores[:limit]
    
    def get_class_scores(self, class_name: str, dictation_title: str = None) -> List[Dict]:
        """获取班级成绩列表"""
        scores = self._load_scores()
        class_scores = [s for s in scores if s['class_name'] == class_name]
        if dictation_title:
            class_scores = [s for s in class_scores if s['dictation_title'] == dictation_title]
        class_scores.sort(key=lambda x: x['created_at'], reverse=True)
        return class_scores
    
    def get_user_stats(self, user_id: str) -> Dict:
        """获取用户统计信息"""
        scores = self.get_user_scores(user_id, limit=1000)
        
        if not scores:
            return {
                'total_dictations': 0,
                'average_score': 0,
                'best_score': 0,
                'trend': 'stable',
                'recent_scores': [],
                'error_types': {}
            }
        
        # 计算统计
        total_dictations = len(scores)
        average_score = sum(s['score'] for s in scores) / total_dictations
        best_score = max(s['score'] for s in scores)
        
        # 最近 10 次成绩（用于趋势图）
        recent_scores = scores[:10][::-1]  # 正序排列
        
        # 计算趋势（对比前 5 次和后 5 次）
        if len(scores) >= 10:
            first_half_avg = sum(s['score'] for s in scores[-5:]) / 5
            second_half_avg = sum(s['score'] for s in scores[-10:-5]) / 5
            if second_half_avg > first_half_avg + 5:
                trend = 'improving'
            elif second_half_avg < first_half_avg - 5:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'stable'
        
        # 错误类型统计
        error_types = defaultdict(int)
        for score in scores:
            mistakes = score.get('mistakes', [])
            for mistake in mistakes:
                error_types[mistake] = error_types[mistake] + 1
        
        return {
            'total_dictations': total_dictations,
            'average_score': round(average_score, 1),
            'best_score': best_score,
            'trend': trend,
            'recent_scores': recent_scores,
            'error_types': dict(error_types)
        }
    
    def get_class_stats(self, class_name: str, dictation_title: str = None) -> Dict:
        """获取班级统计信息"""
        scores = self.get_class_scores(class_name, dictation_title)
        
        if not scores:
            return {
                'total_students': 0,
                'average_score': 0,
                'highest_score': 0,
                'lowest_score': 0,
                'score_distribution': {},
                'student_ranking': []
            }
        
        # 按学生分组
        student_scores = defaultdict(list)
        for score in scores:
            student_scores[score['username']].append(score['score'])
        
        # 计算每个学生的平均分
        student_averages = []
        for username, scores_list in student_scores.items():
            avg = sum(scores_list) / len(scores_list)
            student_averages.append({
                'username': username,
                'average_score': round(avg, 1),
                'dictation_count': len(scores_list)
            })
        
        # 排名
        student_averages.sort(key=lambda x: x['average_score'], reverse=True)
        
        # 分数分布
        distribution = {'90-100': 0, '80-89': 0, '70-79': 0, '60-69': 0, '0-59': 0}
        for score in scores:
            if score['score'] >= 90:
                distribution['90-100'] += 1
            elif score['score'] >= 80:
                distribution['80-89'] += 1
            elif score['score'] >= 70:
                distribution['70-79'] += 1
            elif score['score'] >= 60:
                distribution['60-69'] += 1
            else:
                distribution['0-59'] += 1
        
        all_scores = [s['score'] for s in scores]
        
        return {
            'total_students': len(student_scores),
            'average_score': round(sum(all_scores) / len(all_scores), 1),
            'highest_score': max(all_scores),
            'lowest_score': min(all_scores),
            'score_distribution': distribution,
            'student_ranking': student_averages[:20]  # 前 20 名
        }
    
    def get_dictation_list(self, class_name: str = None) -> List[str]:
        """获取听写任务列表"""
        scores = self._load_scores()
        if class_name:
            scores = [s for s in scores if s['class_name'] == class_name]
        
        titles = list(set(s['dictation_title'] for s in scores))
        titles.sort(reverse=True)
        return titles
    
    def get_error_analysis(self, user_id: str, limit: int = 10) -> List[Dict]:
        """获取用户错题分析"""
        scores = self.get_user_scores(user_id, limit=100)
        
        # 统计错误单词
        word_errors = defaultdict(int)
        for score in scores:
            for mistake in score.get('mistakes', []):
                word_errors[mistake] += 1
        
        # 按错误次数排序
        error_list = [{'word': word, 'count': count} for word, count in word_errors.items()]
        error_list.sort(key=lambda x: x['count'], reverse=True)
        
        return error_list[:limit]


# 全局统计管理器实例
stats_manager = StatsManager()


if __name__ == '__main__':
    # 测试
    print("测试添加成绩...")
    result = stats_manager.add_score(
        user_id='user_123',
        username='student1',
        class_name='25 级 IB IELTS 听力',
        dictation_title='Unit 1 Vocabulary',
        score=85,
        correct_rate=85.0,
        total_words=20,
        correct_count=17,
        mistakes=['necessary', 'accommodate', 'embarrass']
    )
    print(f"添加结果：{result}")
    
    print("\n测试获取用户统计...")
    stats = stats_manager.get_user_stats('user_123')
    print(f"用户统计：{json.dumps(stats, indent=2, ensure_ascii=False)}")
