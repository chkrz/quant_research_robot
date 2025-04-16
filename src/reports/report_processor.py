import os
import sys
import json
import re
import pandas as pd
from datetime import datetime

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config.config import REPORTS_PATH

class ReportProcessor:
    """
    研究报告处理类，负责研究报告的读取和预处理
    """
    
    def __init__(self):
        """
        初始化报告处理器
        """
        # 确保报告目录存在
        os.makedirs(REPORTS_PATH, exist_ok=True)
    
    def load_report(self, report_path):
        """
        加载研究报告
        
        Args:
            report_path: 报告文件路径
            
        Returns:
            报告内容文本
        """
        if not os.path.exists(report_path):
            raise FileNotFoundError(f"报告文件不存在: {report_path}")
        
        # 根据文件类型读取报告
        file_ext = os.path.splitext(report_path)[1].lower()
        
        if file_ext == '.txt' or file_ext == '.md':
            # 文本文件
            with open(report_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
        elif file_ext == '.pdf':
            # PDF文件 (需要安装pdfplumber库)
            try:
                import pdfplumber
                with pdfplumber.open(report_path) as pdf:
                    content = "\n".join([page.extract_text() for page in pdf.pages])
            except ImportError:
                raise ImportError("请安装pdfplumber库以处理PDF文件: pip install pdfplumber")
        
        elif file_ext in ['.docx', '.doc']:
            # Word文件 (需要安装python-docx库)
            try:
                import docx
                doc = docx.Document(report_path)
                content = "\n".join([para.text for para in doc.paragraphs])
            except ImportError:
                raise ImportError("请安装python-docx库以处理Word文件: pip install python-docx")
        
        else:
            raise ValueError(f"不支持的文件类型: {file_ext}")
        
        return content
    
    def preprocess_report(self, content):
        """
        预处理报告内容
        
        Args:
            content: 报告内容
            
        Returns:
            预处理后的内容
        """
        # 移除多余空行
        content = re.sub(r'\n\s*\n', '\n\n', content)
        
        # 移除页眉页脚
        content = re.sub(r'第\d+页\s+共\d+页', '', content)
        
        # 移除特殊字符
        content = re.sub(r'[^\w\s\.,;:!?，。；：！？《》【】\(\)\[\]\{\}]', '', content)
        
        return content
    
    def extract_metadata(self, content):
        """
        提取报告元数据
        
        Args:
            content: 报告内容
            
        Returns:
            元数据字典
        """
        # 尝试提取标题
        title_match = re.search(r'^(.+?)\n', content)
        title = title_match.group(1).strip() if title_match else "未知标题"
        
        # 尝试提取日期
        date_pattern = r'(\d{4}[年/-]\d{1,2}[月/-]\d{1,2}日?|\d{4}\.\d{1,2}\.\d{1,2})'
        date_match = re.search(date_pattern, content[:1000])  # 只在前1000个字符中查找
        date = date_match.group(1) if date_match else None
        
        # 尝试提取作者
        author_match = re.search(r'(?:作者|研究员)[：:]\s*(.+?)(?:\n|$)', content[:1000])
        author = author_match.group(1).strip() if author_match else "未知作者"
        
        metadata = {
            "title": title,
            "date": date,
            "author": author,
            "processed_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return metadata
    
    def save_processed_report(self, content, metadata, output_dir=None):
        """
        保存处理后的报告
        
        Args:
            content: 处理后的报告内容
            metadata: 报告元数据
            output_dir: 输出目录
            
        Returns:
            保存的文件路径
        """
        if output_dir is None:
            output_dir = os.path.join(REPORTS_PATH, "processed")
        
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成文件名
        safe_title = re.sub(r'[^\w]', '_', metadata["title"])[:30]
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{safe_title}_{timestamp}.json"
        output_path = os.path.join(output_dir, filename)
        
        # 保存报告和元数据
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                "metadata": metadata,
                "content": content
            }, f, ensure_ascii=False, indent=2)
        
        return output_path 