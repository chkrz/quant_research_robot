import os
import sys
import json
import pandas as pd
import numpy as np
import re
from datetime import datetime

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config.config import DATA_PATH

class FactorUtils:
    """
    因子处理工具类
    """
    
    @staticmethod
    def save_factor_logic(factor_logic, factor_name=None):
        """
        保存因子逻辑
        
        Args:
            factor_logic: 因子逻辑（字符串或字典）
            factor_name: 因子名称
            
        Returns:
            保存的文件路径
        """
        # 确保存储目录存在
        factor_dir = os.path.join(DATA_PATH, "factors")
        os.makedirs(factor_dir, exist_ok=True)
        
        # 处理因子逻辑
        if isinstance(factor_logic, str):
            # 尝试解析JSON
            try:
                factor_data = json.loads(factor_logic)
            except json.JSONDecodeError:
                # 不是JSON格式，直接存储文本
                factor_data = {"factor_text": factor_logic}
        else:
            factor_data = factor_logic
            
        # 确定因子名称
        if not factor_name:
            if isinstance(factor_data, dict) and "factor_name" in factor_data:
                factor_name = factor_data["factor_name"]
            else:
                factor_name = "unknown_factor"
                
        # 安全的文件名
        safe_name = re.sub(r'[^\w]', '_', factor_name)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{safe_name}_{timestamp}.json"
        file_path = os.path.join(factor_dir, filename)
        
        # 保存因子逻辑
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(factor_data, f, ensure_ascii=False, indent=2)
            
        return file_path
        
    @staticmethod
    def load_factor_logic(factor_file):
        """
        加载因子逻辑
        
        Args:
            factor_file: 因子文件路径
            
        Returns:
            因子逻辑字典
        """
        if not os.path.exists(factor_file):
            raise FileNotFoundError(f"因子文件不存在: {factor_file}")
            
        with open(factor_file, 'r', encoding='utf-8') as f:
            factor_data = json.load(f)
            
        return factor_data
        
    @staticmethod
    def categorize_stocks(factor_values, num_groups=5):
        """
        根据因子值将股票分组
        
        Args:
            factor_values: 因子值DataFrame（索引为股票代码，列为因子名称）
            num_groups: 分组数量
            
        Returns:
            分组结果DataFrame
        """
        if not isinstance(factor_values, pd.DataFrame):
            raise TypeError("factor_values必须是pandas DataFrame类型")
            
        # 创建结果DataFrame
        result = pd.DataFrame(index=factor_values.index)
        
        # 对每个因子进行分组
        for col in factor_values.columns:
            # 计算分位数边界
            quantiles = [i/num_groups for i in range(1, num_groups)]
            bins = [-np.inf] + list(factor_values[col].quantile(quantiles)) + [np.inf]
            
            # 分组
            labels = list(range(1, num_groups + 1))
            result[f"{col}_group"] = pd.cut(factor_values[col], bins=bins, labels=labels)
            
        return result
        
    @staticmethod
    def calculate_group_returns(returns, grouping, group_col):
        """
        计算分组收益率
        
        Args:
            returns: 股票收益率DataFrame（索引为日期，列为股票代码）
            grouping: 分组DataFrame（索引为股票代码，列为分组列）
            group_col: 分组列名
            
        Returns:
            分组收益率DataFrame
        """
        if not isinstance(returns, pd.DataFrame) or not isinstance(grouping, pd.DataFrame):
            raise TypeError("returns和grouping必须是pandas DataFrame类型")
            
        # 确保分组列存在
        if group_col not in grouping.columns:
            raise ValueError(f"分组列{group_col}不存在")
            
        # 获取所有股票的分组
        stock_groups = grouping[group_col].dropna()
        
        # 初始化结果
        group_returns = pd.DataFrame(index=returns.index)
        
        # 计算每个分组的等权平均收益率
        for group in sorted(stock_groups.unique()):
            # 获取该分组的股票
            stocks_in_group = stock_groups[stock_groups == group].index
            
            # 计算分组收益率
            if len(stocks_in_group) > 0:
                # 提取这些股票的收益率，并计算等权平均
                group_return = returns[stocks_in_group].mean(axis=1)
                group_returns[f"Group_{group}"] = group_return
                
        # 计算多空组合
        if f"Group_{1}" in group_returns.columns and f"Group_{stock_groups.max()}" in group_returns.columns:
            group_returns["Long_Short"] = group_returns[f"Group_{1}"] - group_returns[f"Group_{stock_groups.max()}"]
            
        return group_returns 