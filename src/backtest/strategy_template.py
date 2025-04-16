#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
策略模板，用于LLM生成策略代码的参考
"""

from datetime import datetime
import pandas as pd
import numpy as np
from vnpy.trader.constant import Interval
from vnpy.trader.optimize import OptimizationSetting
from vnpy.app.cta_strategy import (
    CtaTemplate,
    StopOrder,
    TickData,
    BarData,
    TradeData,
    OrderData,
    BacktestingEngine
)

class FactorStrategy(CtaTemplate):
    """
    基于因子的策略模板
    """
    
    # 策略参数
    factor_name = "sample_factor"    # 因子名称
    lookback_period = 20             # 回溯期
    holding_period = 5               # 持仓期
    group_num = 5                    # 分组数量
    rebalance_days = 20              # 再平衡周期（天）
    
    # 变量
    bar_count = 0
    current_pos = 0
    last_rebalance_day = None
    history_data = []
    
    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """初始化"""
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        
        # 初始化数据缓存
        self.factor_values = []
        self.stock_groups = {}
        self.holding_stocks = []
        
    def on_init(self):
        """初始化"""
        self.write_log("策略初始化")
        self.load_bar(10)  # 加载10天数据用于初始化
        
    def on_start(self):
        """启动"""
        self.write_log("策略启动")
        
    def on_stop(self):
        """停止"""
        self.write_log("策略停止")
        
    def on_tick(self, tick: TickData):
        """收到行情Tick推送"""
        pass
        
    def on_bar(self, bar: BarData):
        """收到K线数据推送"""
        # 记录K线数据
        self.history_data.append(bar)
        if len(self.history_data) <= self.lookback_period:
            return
            
        # 控制数据长度
        if len(self.history_data) > self.lookback_period * 2:
            self.history_data.pop(0)
            
        # 计数器加1
        self.bar_count += 1
        
        # 每隔rebalance_days天进行一次再平衡
        if self.bar_count % self.rebalance_days == 0:
            self.calculate_factor()
            self.rebalance_portfolio()
            
    def calculate_factor(self):
        """计算因子值"""
        # 示例：计算动量因子
        close_prices = np.array([bar.close_price for bar in self.history_data])
        returns = np.diff(close_prices) / close_prices[:-1]
        
        # 计算N日累积收益率作为动量因子
        if len(returns) >= self.lookback_period:
            momentum = np.prod(1 + returns[-self.lookback_period:]) - 1
            self.factor_values.append(momentum)
        
    def rebalance_portfolio(self):
        """再平衡投资组合"""
        # 根据因子值决定仓位
        if not self.factor_values:
            return
            
        factor_value = self.factor_values[-1]
        
        # 简单策略：因子值为正，做多；为负，做空
        target_pos = 1 if factor_value > 0 else -1
        
        # 若持仓发生变化，则调整仓位
        if target_pos != self.current_pos:
            if self.current_pos > 0:
                self.sell(bar.close_price, abs(self.current_pos))
            elif self.current_pos < 0:
                self.cover(bar.close_price, abs(self.current_pos))
                
            if target_pos > 0:
                self.buy(bar.close_price, abs(target_pos))
            elif target_pos < 0:
                self.short(bar.close_price, abs(target_pos))
                
            self.current_pos = target_pos
            
    def on_order(self, order: OrderData):
        """收到委托变化推送"""
        pass
        
    def on_trade(self, trade: TradeData):
        """收到成交推送"""
        self.put_event()
        
    def on_stop_order(self, stop_order: StopOrder):
        """收到停止单推送"""
        pass

def run_strategy(start_date, end_date, initial_capital=1000000):
    """
    运行回测
    """
    # 创建回测引擎
    engine = BacktestingEngine()
    
    # 设置回测参数
    vt_symbol = "000001.XSHG"  # 使用上证指数作为示例
    engine.set_parameters(
        vt_symbol=vt_symbol,
        interval=Interval.DAILY,
        start=datetime.strptime(start_date, "%Y-%m-%d"),
        end=datetime.strptime(end_date, "%Y-%m-%d"),
        rate=0.0003,  # 手续费率
        slippage=0.2,  # 滑点
        size=1,        # 合约乘数
        pricetick=0.01,  # 价格最小变动
        capital=initial_capital
    )
    
    # 添加策略
    engine.add_strategy(FactorStrategy, {})
    
    # 运行回测
    engine.load_data()
    engine.run_backtesting()
    
    # 获取回测结果
    result = engine.calculate_result()
    stats = engine.calculate_statistics()
    
    # 处理结果
    daily_returns = result.daily_returns.to_dict()
    
    return {
        "daily_returns": daily_returns,
        "total_return": float(stats["total_return"]),
        "annual_return": float(stats["annual_return"]),
        "sharpe_ratio": float(stats["sharpe_ratio"]),
        "max_drawdown": float(stats["max_drawdown"])
    } 