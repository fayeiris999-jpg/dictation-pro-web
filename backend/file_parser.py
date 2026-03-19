#!/usr/bin/env python3
"""
文件解析模块 - 支持 Word/PDF/图片 提取英文、中文、同义替换
"""

import os
import re
import base64
from typing import List, Dict

# 尝试导入第三方库
try:
    import docx
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

try:
    from pdfminer.high_level import extract_text
    HAS_PDFMINER = True
except ImportError:
    HAS_PDFMINER = False

try:
    import pytesseract
    from PIL import Image
    import io
    HAS_OCR = True
except ImportError:
    HAS_OCR = False


class FileParser:
    """文件解析器"""
    
    def __init__(self):
        pass
    
    def parse_file(self, file_data: str, file_type: str) -> Dict:
        """
        解析文件内容
        
        Args:
            file_data: Base64 编码的文件内容或文件路径
            file_type: 文件类型 (word/pdf/image)
        
        Returns:
            {
                'success': bool,
                'words': List[{'english': str, 'chinese': str, 'synonym': str}],
                'error': str (可选)
            }
        """
        try:
            if file_type == 'word':
                return self._parse_word(file_data)
            elif file_type == 'pdf':
                return self._parse_pdf(file_data)
            elif file_type == 'image':
                return self._parse_image(file_data)
            else:
                return {'success': False, 'error': f'不支持的文件类型：{file_type}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _parse_word(self, file_data: str) -> Dict:
        """解析 Word 文档"""
        if not HAS_DOCX:
            return {'success': False, 'error': '未安装 python-docx 库，请运行：pip install python-docx'}
        
        try:
            # 解码 Base64
            file_bytes = base64.b64decode(file_data)
            
            # 保存到临时文件
            temp_path = '/tmp/temp.docx'
            with open(temp_path, 'wb') as f:
                f.write(file_bytes)
            
            # 读取 Word 文档
            doc = docx.Document(temp_path)
            text = '\n'.join([para.text for para in doc.paragraphs])
            
            # 清理临时文件
            os.remove(temp_path)
            
            # 解析文本
            words = self._parse_text(text)
            
            return {'success': True, 'words': words}
        except Exception as e:
            return {'success': False, 'error': f'Word 解析失败：{str(e)}'}
    
    def _parse_pdf(self, file_data: str) -> Dict:
        """解析 PDF 文档"""
        if not HAS_PDFMINER:
            return {'success': False, 'error': '未安装 pdfminer，请运行：pip install pdfminer.six'}
        
        try:
            # 解码 Base64
            file_bytes = base64.b64decode(file_data)
            
            # 保存到临时文件
            temp_path = '/tmp/temp.pdf'
            with open(temp_path, 'wb') as f:
                f.write(file_bytes)
            
            # 提取文本
            text = extract_text(temp_path)
            
            # 清理临时文件
            os.remove(temp_path)
            
            # 解析文本
            words = self._parse_text(text)
            
            return {'success': True, 'words': words}
        except Exception as e:
            return {'success': False, 'error': f'PDF 解析失败：{str(e)}'}
    
    def _parse_image(self, file_data: str) -> Dict:
        """解析图片（OCR）"""
        if not HAS_OCR:
            return {'success': False, 'error': '未安装 OCR 库，请运行：pip install pytesseract pillow'}
        
        try:
            # 解码 Base64
            file_bytes = base64.b64decode(file_data)
            
            # 使用 Tesseract OCR（支持中英文）
            image = Image.open(io.BytesIO(file_bytes))
            
            # 配置 Tesseract（需要安装 tesseract-ocr）
            # 中文 + 英文
            text = pytesseract.image_to_string(image, lang='chi_sim+eng')
            
            # 解析文本
            words = self._parse_text(text)
            
            return {'success': True, 'words': words}
        except Exception as e:
            return {'success': False, 'error': f'图片 OCR 失败：{str(e)}'}
    
    def _parse_text(self, text: str) -> List[Dict]:
        """
        解析文本为单词列表
        
        支持的格式：
        1. 表格格式：英文 | 中文 | 同义词
        2. 列表格式：英文 - 中文 - 同义词
        3. 简单格式：英文 - 中文
        """
        words = []
        lines = text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 跳过表头
            if any(header in line.lower() for header in ['word', 'english', 'chinese', 'synonym', '英文', '中文', '同义']):
                continue
            
            word = self._parse_line(line)
            if word:
                words.append(word)
        
        return words
    
    def _parse_line(self, line: str) -> Dict:
        """解析单行文本"""
        
        # 尝试多种分隔符
        separators = ['|', '\t', '-', '–', '—', ',', '，']
        
        for sep in separators:
            if sep in line:
                parts = [p.strip() for p in line.split(sep)]
                
                if len(parts) >= 2:
                    word = {
                        'english': parts[0],
                        'chinese': parts[1] if len(parts) > 1 else '',
                        'synonym': parts[2] if len(parts) > 2 else ''
                    }
                    
                    # 验证英文部分是否包含字母
                    if re.search(r'[a-zA-Z]', word['english']):
                        return word
        
        # 尝试正则匹配
        # 格式：英文单词 + 中文释义
        match = re.search(r'([a-zA-Z\s]+)\s*[-–—|]\s*([\u4e00-\u9fa5]+)', line)
        if match:
            return {
                'english': match.group(1).strip(),
                'chinese': match.group(2).strip(),
                'synonym': ''
            }
        
        return None


# 全局实例
file_parser = FileParser()


if __name__ == '__main__':
    # 测试
    print("文件解析模块测试")
    print(f"Word 支持：{HAS_DOCX}")
    print(f"PDF 支持：{HAS_PDFMINER}")
    print(f"OCR 支持：{HAS_OCR}")
