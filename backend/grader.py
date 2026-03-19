#!/usr/bin/env python3
"""
DictationPro AI - 自动批改模块
编辑距离算法、错误类型识别、容错处理
"""

from typing import Dict, List, Tuple
import re


class AutoGrader:
    """自动批改器"""
    
    # 常见拼写错误映射（用于容错）
    COMMON_MISTAKES = {
        'ph': 'f',  # phone -> fone
        'gh': '',   # though -> tho
        'tion': 'shun',
        'sion': 'zhun',
        'ck': 'k',
        'qu': 'kw',
        'x': 'ks',
        'y': 'i',   # happy -> happi
        'ie': 'ei', # receive -> recieve
        'ei': 'ie', # believe -> beleive
    }
    
    # 双写字母容错
    DOUBLE_LETTERS = {
        'tt': 't', 'dd': 'd', 'gg': 'g', 'bb': 'b',
        'nn': 'n', 'mm': 'm', 'll': 'l', 'ss': 's',
        'pp': 'p', 'cc': 'c', 'rr': 'r',
    }
    
    def grade(self, expected_words: List[str], student_answers: List[str]) -> Dict:
        """
        批改听写
        
        Args:
            expected_words: 正确答案列表
            student_answers: 学生答案列表
        
        Returns:
            批改结果 {
                score: 总分 (0-100),
                correct_rate: 正确率,
                correct_count: 正确数量,
                mistakes: [{
                    word: 单词,
                    expected: 正确答案,
                    got: 学生答案,
                    type: 错误类型,
                    distance: 编辑距离
                }]
            }
        """
        if len(expected_words) == 0:
            return {
                'score': 0,
                'correct_rate': 0,
                'correct_count': 0,
                'total_count': 0,
                'mistakes': []
            }
        
        correct_count = 0
        mistakes = []
        
        for i, expected in enumerate(expected_words):
            got = student_answers[i] if i < len(student_answers) else ''
            
            # 标准化处理
            expected_norm = self._normalize(expected)
            got_norm = self._normalize(got)
            
            # 判断是否正确
            is_correct, error_type, distance = self._check_answer(expected_norm, got_norm)
            
            if is_correct:
                correct_count += 1
            else:
                mistakes.append({
                    'word': expected,
                    'expected': expected,
                    'got': got,
                    'type': error_type,
                    'distance': distance,
                    'index': i
                })
        
        total_count = len(expected_words)
        correct_rate = round((correct_count / total_count) * 100, 1) if total_count > 0 else 0
        score = correct_rate  # 默认分数=正确率
        
        # 根据错误类型调整分数（轻微错误扣分少）
        for mistake in mistakes:
            if mistake['type'] == 'minor':
                score += 2  # 轻微错误只扣 1 分（因为正确率扣了 100/n 分）
            elif mistake['type'] == 'spacing':
                score += 1
        
        score = max(0, min(100, round(score, 1)))
        
        return {
            'score': score,
            'correct_rate': correct_rate,
            'correct_count': correct_count,
            'total_count': total_count,
            'mistakes': mistakes
        }
    
    def _normalize(self, text: str) -> str:
        """标准化文本"""
        if not text:
            return ''
        
        # 转小写
        text = text.lower()
        
        # 去除首尾空格
        text = text.strip()
        
        # 去除多余空格（中间保留一个）
        text = re.sub(r'\s+', ' ', text)
        
        # 去除标点符号
        text = re.sub(r'[^\w\s]', '', text)
        
        return text
    
    def _check_answer(self, expected: str, got: str) -> Tuple[bool, str, int]:
        """
        检查答案
        
        Returns:
            (是否正确，错误类型，编辑距离)
            错误类型：'correct', 'minor', 'spacing', 'major'
        """
        if not expected and not got:
            return (True, 'correct', 0)
        
        if not got:
            return (False, 'major', len(expected))
        
        # 完全匹配
        if expected == got:
            return (True, 'correct', 0)
        
        # 计算编辑距离
        distance = self._levenshtein_distance(expected, got)
        
        # 空格差异（容错）
        if expected.replace(' ', '') == got.replace(' ', ''):
            return (True, 'spacing', 1)
        
        # 轻微错误：编辑距离 = 1 且单词长度 > 8
        # 只对长单词容错（8 个字母以上允许 1 个错误）
        if distance == 1 and len(expected) > 8:
            return (True, 'minor', distance)
        
        # 其他情况：重大错误
        return (False, 'major', distance)
    
    def _is_common_mistake(self, expected: str, got: str) -> bool:
        """检查是否为常见拼写错误模式"""
        # 双写字母错误 (necessary vs neccessary)
        if len(expected) - len(got) == 1:
            # 检查是否少了一个字母
            for i in range(len(expected) - 1):
                if expected[i] == expected[i+1]:
                    test = expected[:i+1] + expected[i+2:]
                    if test == got:
                        return True
        elif len(got) - len(expected) == 1:
            # 检查是否多了一个字母
            for i in range(len(got) - 1):
                if got[i] == got[i+1]:
                    test = got[:i+1] + got[i+2:]
                    if test == expected:
                        return True
        
        return False
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """计算编辑距离（Levenshtein Distance）"""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                # 计算插入、删除、替换的最小代价
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def get_error_analysis(self, mistakes: List[Dict]) -> Dict:
        """
        分析错误类型
        
        Returns:
            {
                'by_type': {错误类型：数量},
                'by_word': {单词：错误次数},
                'suggestions': [建议]
            }
        """
        by_type = {}
        by_word = {}
        
        for mistake in mistakes:
            # 按类型统计
            error_type = mistake.get('type', 'unknown')
            by_type[error_type] = by_type.get(error_type, 0) + 1
            
            # 按单词统计
            word = mistake.get('word', '')
            by_word[word] = by_word.get(word, 0) + 1
        
        # 生成建议
        suggestions = []
        
        if by_type.get('major', 0) > 3:
            suggestions.append('较多单词拼写错误，建议加强基础词汇记忆')
        
        if by_type.get('minor', 0) > 5:
            suggestions.append('轻微错误较多，注意细节和拼写规范')
        
        if len(by_word) > 10:
            suggestions.append('错误单词较多，建议重点复习高频错题')
        
        # 找出最常错的单词
        if by_word:
            top_errors = sorted(by_word.items(), key=lambda x: x[1], reverse=True)[:3]
            if top_errors:
                words = ', '.join([w for w, c in top_errors])
                suggestions.append(f'重点复习：{words}')
        
        return {
            'by_type': by_type,
            'by_word': by_word,
            'suggestions': suggestions
        }


# 全局批改器实例
auto_grader = AutoGrader()


if __name__ == '__main__':
    # 测试
    expected = ['apple', 'banana', 'strawberry', 'communication', 'necessary']
    student = ['apple', 'bananna', 'strawbery', 'communication', 'neccessary']
    
    result = auto_grader.grade(expected, student)
    
    print("批改结果:")
    print(f"分数：{result['score']}")
    print(f"正确率：{result['correct_rate']}%")
    print(f"正确：{result['correct_count']}/{result['total_count']}")
    print("\n错误详情:")
    for mistake in result['mistakes']:
        print(f"  - {mistake['word']}: 期望'{mistake['expected']}', 得到'{mistake['got']}', 类型={mistake['type']}")
    
    print("\n错误分析:")
    analysis = auto_grader.get_error_analysis(result['mistakes'])
    print(f"  按类型：{analysis['by_type']}")
    print(f"  按单词：{analysis['by_word']}")
    print(f"  建议：{analysis['suggestions']}")
