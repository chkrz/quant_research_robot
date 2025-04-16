import os
import sys
import importlib
import tempfile
import json
import pandas as pd
import numpy as np
from datetime import datetime

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config.config import (
    BACKTEST_START_DATE,
    BACKTEST_END_DATE,
    DEFAULT_CAPITAL,
    DATA_PATH
)

class BacktestEngine:
    """
    基于vnpy的回测引擎
    """
    
    def __init__(self, start_date=None, end_date=None, initial_capital=None):
        """
        初始化回测引擎
        
        Args:
            start_date: 回测开始日期
            end_date: 回测结束日期
            initial_capital: 初始资金
        """
        self.start_date = start_date or BACKTEST_START_DATE
        self.end_date = end_date or BACKTEST_END_DATE
        self.initial_capital = initial_capital or DEFAULT_CAPITAL
        
        # 确保数据目录存在
        os.makedirs(DATA_PATH, exist_ok=True)
        
    def run_backtest(self, strategy_code):
        """
        运行回测
        
        Args:
            strategy_code: 策略代码字符串
            
        Returns:
            回测结果
        """
        # 创建临时策略文件
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as f:
            strategy_file = f.name
            f.write(strategy_code)
        
        try:
            # 导入策略模块
            module_name = os.path.basename(strategy_file).replace('.py', '')
            spec = importlib.util.spec_from_file_location(module_name, strategy_file)
            strategy_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(strategy_module)
            
            # 执行回测
            if hasattr(strategy_module, 'run_strategy'):
                result = strategy_module.run_strategy(
                    start_date=self.start_date,
                    end_date=self.end_date,
                    initial_capital=self.initial_capital
                )
                return result
            else:
                raise AttributeError("策略文件中没有定义run_strategy函数")
        except Exception as e:
            print(f"回测执行错误: {e}")
            return None
        finally:
            # 清理临时文件
            if os.path.exists(strategy_file):
                os.remove(strategy_file)
    
    def calculate_performance(self, result):
        """
        计算策略性能指标
        
        Args:
            result: 回测结果
            
        Returns:
            性能指标字典
        """
        if not result or not isinstance(result, dict):
            return None
            
        # 提取回测数据
        daily_returns = result.get('daily_returns', [])
        if not daily_returns:
            return None
            
        # 转换为pandas Series
        if isinstance(daily_returns, list):
            daily_returns = pd.Series(daily_returns)
            
        # 计算性能指标
        total_return = daily_returns.sum()
        annualized_return = (1 + total_return) ** (252 / len(daily_returns)) - 1
        volatility = daily_returns.std() * np.sqrt(252)
        sharpe_ratio = annualized_return / volatility if volatility != 0 else 0
        max_drawdown = (daily_returns.cumsum() - daily_returns.cumsum().cummax()).min()
        
        # 计算分档收益率（按月）
        date_index = pd.date_range(self.start_date, self.end_date, freq='D')
        if len(date_index) >= len(daily_returns):
            daily_returns.index = date_index[:len(daily_returns)]
        else:
            daily_returns.index = pd.date_range(self.start_date, periods=len(daily_returns), freq='D')
            
        monthly_returns = daily_returns.resample('M').apply(lambda x: (1 + x).prod() - 1)
        
        # 构建性能报告
        performance = {
            'total_return': float(total_return),
            'annualized_return': float(annualized_return),
            'volatility': float(volatility),
            'sharpe_ratio': float(sharpe_ratio),
            'max_drawdown': float(max_drawdown),
            'monthly_returns': monthly_returns.to_dict()
        }
        
        return performance
        
    def save_result(self, performance, factor_name):
        """
        保存回测结果
        
        Args:
            performance: 性能指标
            factor_name: 因子名称
            
        Returns:
            保存的文件路径
        """
        if not performance:
            return None
            
        # 创建结果目录
        result_dir = os.path.join(DATA_PATH, 'results')
        os.makedirs(result_dir, exist_ok=True)
        
        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        result_file = os.path.join(result_dir, f"{factor_name}_{timestamp}.json")
        
        # 保存结果
        with open(result_file, 'w') as f:
            json.dump(performance, f, indent=4)
            
        return result_file 