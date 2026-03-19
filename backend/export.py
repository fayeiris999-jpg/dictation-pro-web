#!/usr/bin/env python3
"""
DictationPro AI - 错题本导出模块
支持 PDF、Excel 格式导出
"""

import json
import os
import io
from datetime import datetime
from typing import Dict, List, Any

# 尝试导入可选依赖
try:
    import xlsxwriter
    XLSX_AVAILABLE = True
except ImportError:
    XLSX_AVAILABLE = False
    print("⚠️  xlsxwriter 未安装，Excel 导出功能不可用")
    print("   安装：pip install xlsxwriter")

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("⚠️  reportlab 未安装，PDF 导出功能不可用")
    print("   安装：pip install reportlab")

from stats import stats_manager


class ExportManager:
    """错题本导出管理"""
    
    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or os.path.join(os.path.dirname(__file__), 'exports')
        self._ensure_output_dir()
        
        # 注册中文字体（macOS 系统字体）
        if PDF_AVAILABLE:
            try:
                # 尝试注册 macOS 系统中文宋体
                font_path = '/System/Library/Fonts/Supplemental/Songti.ttc'
                if os.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont('Songti', font_path))
                    self.chinese_font = 'Songti'
                else:
                    # 备用字体
                    self.chinese_font = 'Helvetica'
            except:
                self.chinese_font = 'Helvetica'
        else:
            self.chinese_font = 'Helvetica'
    
    def _ensure_output_dir(self):
        """确保输出目录存在"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def export_to_excel(self, user_id: str, username: str, class_name: str = None) -> Dict:
        """导出错题本为 Excel"""
        if not XLSX_AVAILABLE:
            return {'success': False, 'error': 'xlsxwriter 未安装'}
        
        # 获取错题数据
        errors = stats_manager.get_error_analysis(user_id, limit=100)
        scores = stats_manager.get_user_scores(user_id, limit=100)
        
        if not errors:
            return {'success': False, 'error': '暂无错题数据'}
        
        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"错题本_{username}_{timestamp}.xlsx"
        filepath = os.path.join(self.output_dir, filename)
        
        # 创建 Excel 工作簿
        workbook = xlsxwriter.Workbook(filepath)
        
        # 工作表 1：错题汇总
        worksheet1 = workbook.add_worksheet('错题汇总')
        
        # 格式设置
        header_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#4472C4',
            'font_color': 'white',
            'border': 1
        })
        
        cell_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'text_wrap': True
        })
        
        error_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'bg_color': '#FFC7CE',
            'font_color': '#9C0006'
        })
        
        # 写入表头
        headers = ['序号', '错误单词', '错误次数', '最近错误时间', '相关听写']
        for col, header in enumerate(headers):
            worksheet1.write(0, col, header, header_format)
        
        # 写入数据
        for row, error in enumerate(errors, 1):
            worksheet1.write(row, 0, row, cell_format)
            worksheet1.write(row, 1, error['word'], error_format)
            worksheet1.write(row, 2, error['count'], cell_format)
            worksheet1.write(row, 3, '见听写记录', cell_format)
            worksheet1.write(row, 4, ', '.join(set(s['dictation_title'] for s in scores if error['word'] in s.get('mistakes', []))), cell_format)
        
        # 调整列宽
        worksheet1.set_column('A:A', 8)
        worksheet1.set_column('B:B', 20)
        worksheet1.set_column('C:C', 12)
        worksheet1.set_column('D:D', 18)
        worksheet1.set_column('E:E', 30)
        
        # 工作表 2：听写记录
        worksheet2 = workbook.add_worksheet('听写记录')
        
        headers2 = ['日期', '听写标题', '分数', '正确率', '总词数', '正确数', '错误单词']
        for col, header in enumerate(headers2):
            worksheet2.write(0, col, header, header_format)
        
        for row, score in enumerate(scores, 1):
            worksheet2.write(row, 0, score['created_at'][:10], cell_format)
            worksheet2.write(row, 1, score['dictation_title'], cell_format)
            worksheet2.write(row, 2, score['score'], cell_format)
            worksheet2.write(row, 3, f"{score['correct_rate']}%", cell_format)
            worksheet2.write(row, 4, score['total_words'], cell_format)
            worksheet2.write(row, 5, score['correct_count'], cell_format)
            worksheet2.write(row, 6, ', '.join(score.get('mistakes', [])), error_format)
        
        worksheet2.set_column('A:A', 12)
        worksheet2.set_column('B:B', 25)
        worksheet2.set_column('C:C', 8)
        worksheet2.set_column('D:D', 10)
        worksheet2.set_column('E:E', 8)
        worksheet2.set_column('F:F', 8)
        worksheet2.set_column('G:G', 30)
        
        # 工作表 3：统计分析
        worksheet3 = workbook.add_worksheet('统计分析')
        
        user_stats = stats_manager.get_user_stats(user_id)
        
        # 写入统计信息
        stats_data = [
            ['统计项', '数值'],
            ['总听写次数', user_stats['total_dictations']],
            ['平均分', user_stats['average_score']],
            ['最高分', user_stats['best_score']],
            ['趋势', user_stats['trend']],
            ['错题总数', len(errors)]
        ]
        
        for row, data in enumerate(stats_data):
            worksheet3.write(row, 0, data[0], header_format if row == 0 else cell_format)
            worksheet3.write(row, 1, data[1], header_format if row == 0 else cell_format)
        
        worksheet3.set_column('A:A', 15)
        worksheet3.set_column('B:B', 20)
        
        workbook.close()
        
        return {
            'success': True,
            'filepath': filepath,
            'filename': filename,
            'error_count': len(errors),
            'score_count': len(scores)
        }
    
    def export_to_pdf(self, user_id: str, username: str, class_name: str = None) -> Dict:
        """导出错题本为 PDF"""
        if not PDF_AVAILABLE:
            return {'success': False, 'error': 'reportlab 未安装'}
        
        # 获取错题数据
        errors = stats_manager.get_error_analysis(user_id, limit=50)
        scores = stats_manager.get_user_scores(user_id, limit=20)
        user_stats = stats_manager.get_user_stats(user_id)
        
        if not errors:
            return {'success': False, 'error': '暂无错题数据'}
        
        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"错题本_{username}_{timestamp}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        # 创建 PDF 文档
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # 样式
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1E3A8A'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName=self.chinese_font
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#007AFF'),
            spaceAfter=12,
            spaceBefore=12,
            fontName=self.chinese_font
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#3A3A3C'),
            fontName=self.chinese_font
        )
        
        # 内容列表
        content = []
        
        # 标题
        content.append(Paragraph('DictationPro AI 错题本', title_style))
        content.append(Paragraph(f'学生：{username} | 生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M")}', normal_style))
        content.append(Spacer(1, 20))
        
        # 统计概览
        content.append(Paragraph('📊 学习统计', heading_style))
        stats_table = Table([
            ['总听写次数', '平均分', '最高分', '学习趋势', '错题总数'],
            [user_stats['total_dictations'], 
             f"{user_stats['average_score']}分", 
             f"{user_stats['best_score']}分",
             '📈 进步' if user_stats['trend'] == 'improving' else '📉 退步' if user_stats['trend'] == 'declining' else '➡️ 稳定',
             len(errors)]
        ])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), self.chinese_font),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#E8F4FD')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#D1D1D6'))
        ]))
        content.append(stats_table)
        content.append(Spacer(1, 30))
        
        # 错题列表
        content.append(Paragraph('📝 错题汇总（按错误次数排序）', heading_style))
        
        error_data = [['序号', '错误单词', '错误次数', '掌握程度']]
        for i, error in enumerate(errors, 1):
            # 掌握程度：错误次数越多，掌握程度越低
            level = '⭐' if error['count'] == 1 else '⭐⭐' if error['count'] == 2 else '⭐⭐⭐' if error['count'] <= 4 else '⭐⭐⭐⭐'
            error_data.append([str(i), error['word'], str(error['count']), level])
        
        error_table = Table(error_data, colWidths=[1*cm, 4*cm, 2*cm, 2*cm])
        error_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF3B30')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), self.chinese_font),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FFF5F5')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#FF3B30')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#FFF5F5'), colors.white])
        ]))
        content.append(error_table)
        content.append(Spacer(1, 30))
        
        # 最近听写记录
        if scores:
            content.append(Paragraph('📋 最近听写记录', heading_style))
            
            score_data = [['日期', '听写标题', '分数', '正确率']]
            for score in scores[:10]:
                score_data.append([
                    score['created_at'][:10],
                    score['dictation_title'][:20] + '...' if len(score['dictation_title']) > 20 else score['dictation_title'],
                    f"{score['score']}分",
                    f"{score['correct_rate']}%"
                ])
            
            score_table = Table(score_data, colWidths=[2.5*cm, 8*cm, 2*cm, 2*cm])
            score_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#007AFF')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), self.chinese_font),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#D1D1D6')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#E8F4FD'), colors.white])
            ]))
            content.append(score_table)
        
        # 建议
        content.append(Spacer(1, 30))
        content.append(Paragraph('💡 学习建议', heading_style))
        
        suggestions = []
        if user_stats['average_score'] < 70:
            suggestions.append('• 建议每天增加 10 分钟单词拼写练习')
        if len(errors) > 20:
            suggestions.append('• 错题较多，建议重点复习高频错误单词')
        if user_stats['trend'] == 'declining':
            suggestions.append('• 成绩有下降趋势，建议回顾基础词汇')
        if user_stats['trend'] == 'improving':
            suggestions.append('• 成绩稳步提升，继续保持！🎉')
        
        if not suggestions:
            suggestions.append('• 表现优秀，继续保持当前的学习节奏！')
        
        for suggestion in suggestions:
            content.append(Paragraph(suggestion, normal_style))
        
        # 构建 PDF
        doc.build(content)
        
        return {
            'success': True,
            'filepath': filepath,
            'filename': filename,
            'error_count': len(errors),
            'score_count': len(scores)
        }
    
    def export_class_scores_batch(self, class_name: str, start_date: str = None, end_date: str = None) -> Dict:
        """批量导出班级成绩（Excel）"""
        if not XLSX_AVAILABLE:
            return {'success': False, 'error': 'xlsxwriter 未安装'}
        
        # 获取班级所有成绩
        all_scores = stats_manager._load_scores()
        class_scores = [s for s in all_scores if s['class_name'] == class_name]
        
        # 日期筛选
        if start_date:
            class_scores = [s for s in class_scores if s['created_at'] >= start_date]
        if end_date:
            class_scores = [s for s in class_scores if s['created_at'] <= end_date]
        
        if not class_scores:
            return {'success': False, 'error': '暂无成绩数据'}
        
        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"班级成绩_{class_name}_{timestamp}.xlsx"
        filepath = os.path.join(self.output_dir, filename)
        
        # 创建 Excel 工作簿
        workbook = xlsxwriter.Workbook(filepath)
        
        # 工作表 1：成绩汇总
        worksheet = workbook.add_worksheet('成绩汇总')
        
        # 格式
        header_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'bg_color': '#4472C4',
            'font_color': 'white',
            'border': 1
        })
        cell_format = workbook.add_format({'align': 'center', 'border': 1})
        
        # 表头
        headers = ['日期', '学生姓名', '听写标题', '分数', '正确率', '总词数', '正确数']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        # 数据
        for row, score in enumerate(class_scores, 1):
            worksheet.write(row, 0, score['created_at'][:10], cell_format)
            worksheet.write(row, 1, score['username'], cell_format)
            worksheet.write(row, 2, score['dictation_title'], cell_format)
            worksheet.write(row, 3, score['score'], cell_format)
            worksheet.write(row, 4, f"{score['correct_rate']}%", cell_format)
            worksheet.write(row, 5, score['total_words'], cell_format)
            worksheet.write(row, 6, score['correct_count'], cell_format)
        
        # 调整列宽
        worksheet.set_column(0, 0, 12)
        worksheet.set_column(1, 1, 15)
        worksheet.set_column(2, 2, 25)
        worksheet.set_column(3, 6, 10)
        
        workbook.close()
        
        return {
            'success': True,
            'filepath': filepath,
            'filename': filename,
            'record_count': len(class_scores)
        }
    
    def export_error_book_pdf(self, user_id: str, username: str) -> Dict:
        """导出错题本 PDF（简化版）"""
        return self.export_to_pdf(user_id, username)
    
    def generate_learning_report(self, user_id: str, username: str, period: str = 'weekly') -> Dict:
        """生成学习报告（PDF）"""
        if not PDF_AVAILABLE:
            return {'success': False, 'error': 'reportlab 未安装'}
        
        # 获取统计数据
        user_stats = stats_manager.get_user_stats(user_id)
        errors = stats_manager.get_error_analysis(user_id, limit=50)
        scores = stats_manager.get_user_scores(user_id, limit=50)
        
        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"学习报告_{username}_{period}_{timestamp}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        # 创建 PDF
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # 样式
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#0080DD'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName=self.chinese_font
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#171717'),
            spaceAfter=12,
            spaceBefore=12,
            fontName=self.chinese_font
        )
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#525252'),
            fontName=self.chinese_font
        )
        
        # 内容
        content = []
        
        # 标题
        period_name = '周报' if period == 'weekly' else '月报'
        content.append(Paragraph(f'DictationPro AI 学习{period_name}', title_style))
        content.append(Paragraph(f'学生：{username}', normal_style))
        content.append(Paragraph(f'生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M")}', normal_style))
        content.append(Spacer(1, 30))
        
        # 核心数据
        content.append(Paragraph('📊 核心数据', heading_style))
        
        stats_data = [
            ['总听写次数', f"{user_stats['total_dictations']} 次"],
            ['平均分', f"{user_stats['average_score']} 分"],
            ['最高分', f"{user_stats['best_score']} 分"],
            ['学习趋势', '📈 进步' if user_stats['trend'] == 'improving' else '📉 需努力' if user_stats['trend'] == 'declining' else '➡️ 稳定'],
            ['错题总数', f"{len(errors)} 个"]
        ]
        
        stats_table = Table(stats_data, colWidths=[5*cm, 8*cm])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F0F7FF')),
            ('BACKGROUND', (1, 0), (1, -1), colors.white),
            ('FONTNAME', (0, 0), (-1, -1), self.chinese_font),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#D1D1D6')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT')
        ]))
        content.append(stats_table)
        content.append(Spacer(1, 30))
        
        # 高频错题
        if errors:
            content.append(Paragraph('📝 高频错题 Top 10', heading_style))
            
            error_data = [['排名', '单词', '错误次数', '掌握程度']]
            for i, error in enumerate(errors[:10], 1):
                level = '⭐⭐⭐⭐' if error['count'] <= 2 else '⭐⭐⭐' if error['count'] <= 4 else '⭐⭐' if error['count'] <= 6 else '⭐'
                error_data.append([str(i), error['word'], str(error['count']), level])
            
            error_table = Table(error_data, colWidths=[1*cm, 5*cm, 2*cm, 3*cm])
            error_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF3B30')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, -1), self.chinese_font),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#D1D1D6')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#FFF5F5'), colors.white])
            ]))
            content.append(error_table)
            content.append(Spacer(1, 30))
        
        # 最近成绩
        if scores:
            content.append(Paragraph('📋 最近听写成绩', heading_style))
            
            score_data = [['日期', '标题', '分数', '正确率']]
            for score in scores[:10]:
                score_data.append([
                    score['created_at'][:10],
                    score['dictation_title'][:15] + '...' if len(score['dictation_title']) > 15 else score['dictation_title'],
                    f"{score['score']}分",
                    f"{score['correct_rate']}%"
                ])
            
            score_table = Table(score_data, colWidths=[2.5*cm, 7*cm, 2*cm, 2*cm])
            score_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0080DD')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, -1), self.chinese_font),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#D1D1D6')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#E8F4FD'), colors.white])
            ]))
            content.append(score_table)
            content.append(Spacer(1, 30))
        
        # 学习建议
        content.append(Paragraph('💡 个性化学习建议', heading_style))
        
        suggestions = []
        if user_stats['average_score'] >= 90:
            suggestions.append('✅ 表现优异！建议挑战更高难度的词汇。')
        elif user_stats['average_score'] >= 80:
            suggestions.append('👍 表现良好！继续巩固基础词汇。')
        elif user_stats['average_score'] >= 70:
            suggestions.append('💪 表现不错！建议每天增加 10 分钟拼写练习。')
        else:
            suggestions.append('📚 需要加强练习！建议从基础词汇开始，每天坚持听写。')
        
        if len(errors) > 30:
            suggestions.append('⚠️ 错题较多，建议重点复习高频错误单词。')
        
        if user_stats['trend'] == 'improving':
            suggestions.append('📈 成绩稳步提升，继续保持！')
        elif user_stats['trend'] == 'declining':
            suggestions.append('⚠️ 成绩有下降趋势，建议回顾近期错题。')
        
        for suggestion in suggestions:
            content.append(Paragraph(suggestion, normal_style))
        
        # 构建 PDF
        doc.build(content)
        
        return {
            'success': True,
            'filepath': filepath,
            'filename': filename,
            'period': period
        }


# 全局导出管理器实例
export_manager = ExportManager()


if __name__ == '__main__':
    # 测试
    print("测试 Excel 导出...")
    result = export_manager.export_to_excel('user_123', 'student1', '25 级 IB IELTS 听力')
    print(f"Excel 导出结果：{result}")
    
    print("\n测试 PDF 导出...")
    result = export_manager.export_to_pdf('user_123', 'student1', '25 级 IB IELTS 听力')
    print(f"PDF 导出结果：{result}")
