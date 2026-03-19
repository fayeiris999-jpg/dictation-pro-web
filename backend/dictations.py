#!/usr/bin/env python3
"""
DictationPro AI - 听写任务管理模块
创建、存储、管理听写任务
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import secrets


class DictationManager:
    """听写任务管理"""
    
    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir or os.path.join(os.path.dirname(__file__), 'data')
        self.dictations_file = os.path.join(self.data_dir, 'dictations.json')
        self._ensure_data_dir()
    
    def _ensure_data_dir(self):
        """确保数据目录存在"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        if not os.path.exists(self.dictations_file):
            self._save_dictations([])
    
    def _load_dictations(self) -> List[Dict]:
        """加载听写任务"""
        try:
            with open(self.dictations_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    def _save_dictations(self, dictations: List[Dict]):
        """保存听写任务"""
        with open(self.dictations_file, 'w', encoding='utf-8') as f:
            json.dump(dictations, f, ensure_ascii=False, indent=2)
    
    def create_dictation(self, title: str, class_name: str, teacher_id: str,
                         words: List[Dict] = None, word_list_text: str = None,
                         audio_url: str = None, duration: int = None) -> Dict:
        """
        创建听写任务
        
        Args:
            title: 听写标题
            class_name: 班级名称
            teacher_id: 教师 ID
            words: 词表 [{english: '', chinese: '', hint: ''}]
            word_list_text: 词表文本（每行一个单词）
            audio_url: 音频 URL
            duration: 预计时长（秒）
        
        Returns:
            创建结果
        """
        dictations = self._load_dictations()
        
        # 解析词表
        if words is None:
            words = self._parse_word_list(word_list_text or '')
        
        dictation_id = f"dict_{secrets.token_hex(8)}"
        
        dictation = {
            'id': dictation_id,
            'title': title,
            'class_name': class_name,
            'teacher_id': teacher_id,
            'words': words,
            'word_count': len(words),
            'audio_url': audio_url,
            'duration': duration or len(words) * 10,  # 默认每个词 10 秒
            'status': 'active',  # active, archived
            'created_at': datetime.now().isoformat(),
            'student_attempts': []  # 学生作答记录
        }
        
        dictations.append(dictation)
        self._save_dictations(dictations)
        
        return {
            'success': True,
            'dictation_id': dictation_id,
            'word_count': len(words)
        }
    
    def _parse_word_list(self, text: str) -> List[Dict]:
        """解析词表文本"""
        words = []
        lines = text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 支持多种格式：
            # 1. "apple 苹果"
            # 2. "apple, 苹果"
            # 3. "apple | 苹果"
            # 4. "apple" (只有英文)
            
            parts = None
            for sep in ['\t', '|', ',', '  ', ' ']:
                if sep in line:
                    parts = line.split(sep, 1)
                    break
            
            if parts and len(parts) >= 1:
                english = parts[0].strip().lower()
                chinese = parts[1].strip() if len(parts) > 1 else ''
                
                if english:
                    words.append({
                        'english': english,
                        'chinese': chinese,
                        'hint': ''
                    })
            else:
                # 只有英文单词
                english = line.strip().lower()
                if english:
                    words.append({
                        'english': english,
                        'chinese': '',
                        'hint': ''
                    })
        
        return words
    
    def get_dictation(self, dictation_id: str) -> Optional[Dict]:
        """获取听写任务详情"""
        dictations = self._load_dictations()
        for d in dictations:
            if d['id'] == dictation_id:
                return d
        return None
    
    def get_dictations_by_class(self, class_name: str) -> List[Dict]:
        """获取班级的听写任务列表"""
        dictations = self._load_dictations()
        return [d for d in dictations if d['class_name'] == class_name and d['status'] == 'active']
    
    def get_dictations_by_teacher(self, teacher_id: str) -> List[Dict]:
        """获取教师的听写任务列表"""
        dictations = self._load_dictations()
        return [d for d in dictations if d['teacher_id'] == teacher_id]
    
    def submit_attempt(self, dictation_id: str, student_id: str, username: str,
                       answers: List[str], score: int, correct_rate: float,
                       mistakes: List[Dict]) -> Dict:
        """
        提交听写作答
        
        Args:
            dictation_id: 听写 ID
            student_id: 学生 ID
            username: 用户名
            answers: 学生答案列表
            score: 得分 (0-100)
            correct_rate: 正确率 (0-100)
            mistakes: 错误详情 [{word: '', expected: '', got: '', type: ''}]
        
        Returns:
            提交结果
        """
        dictations = self._load_dictations()
        
        for d in dictations:
            if d['id'] == dictation_id:
                attempt = {
                    'student_id': student_id,
                    'username': username,
                    'answers': answers,
                    'score': score,
                    'correct_rate': correct_rate,
                    'mistakes': mistakes,
                    'submitted_at': datetime.now().isoformat()
                }
                
                d['student_attempts'].append(attempt)
                self._save_dictations(dictations)
                
                return {
                    'success': True,
                    'attempt_id': f"attempt_{secrets.token_hex(8)}",
                    'score': score,
                    'correct_rate': correct_rate
                }
        
        return {'success': False, 'error': '听写任务不存在'}
    
    def get_student_attempts(self, dictation_id: str, student_id: str) -> List[Dict]:
        """获取学生在某个听写的作答记录"""
        dictation = self.get_dictation(dictation_id)
        if not dictation:
            return []
        
        return [a for a in dictation['student_attempts'] if a['student_id'] == student_id]
    
    def get_class_attempts(self, dictation_id: str) -> List[Dict]:
        """获取班级所有学生的作答记录"""
        dictation = self.get_dictation(dictation_id)
        if not dictation:
            return []
        
        return dictation['student_attempts']
    
    def archive_dictation(self, dictation_id: str) -> Dict:
        """归档听写任务"""
        dictations = self._load_dictations()
        
        for d in dictations:
            if d['id'] == dictation_id:
                d['status'] = 'archived'
                self._save_dictations(dictations)
                return {'success': True}
        
        return {'success': False, 'error': '听写任务不存在'}
    
    def delete_dictation(self, dictation_id: str) -> Dict:
        """删除听写任务"""
        dictations = self._load_dictations()
        dictations = [d for d in dictations if d['id'] != dictation_id]
        self._save_dictations(dictations)
        return {'success': True}


# 全局听写管理器实例
dictation_manager = DictationManager()


if __name__ == '__main__':
    # 测试
    print("测试创建听写...")
    result = dictation_manager.create_dictation(
        title='Unit 1 Vocabulary',
        class_name='25 级 IB IELTS 听力',
        teacher_id='user_123',
        word_list_text='''
        apple 苹果
        banana 香蕉
        orange 橙子
        grape 葡萄
        strawberry 草莓
        '''
    )
    print(f"创建结果：{result}")
    
    print("\n获取班级听写列表...")
    dictations = dictation_manager.get_dictations_by_class('25 级 IB IELTS 听力')
    print(f"听写数量：{len(dictations)}")
    if dictations:
        print(f"第一个听写：{dictations[0]['title']} - {dictations[0]['word_count']}词")
