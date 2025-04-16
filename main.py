#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
量化研究报告复现机器人
基于LLM的能力，自动复现量化领域的研究报告
"""

import os
import sys
import argparse
import json
from datetime import datetime
import traceback

# 添加项目根目录到系统路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from src.models.llm_manager import LLMManager
from src.backtest.backtest_engine import BacktestEngine
from src.reports.report_processor import ReportProcessor
from src.utils.factor_utils import FactorUtils

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="量化研究报告复现机器人")
    
    # 必选参数
    parser.add_argument("--report", required=True, help="研究报告文件路径")
    
    # 可选参数
    parser.add_argument("--model", default=None, help="使用的LLM模型名称")
    parser.add_argument("--start_date", default=None, help="回测开始日期 (YYYY-MM-DD)")
    parser.add_argument("--end_date", default=None, help="回测结束日期 (YYYY-MM-DD)")
    parser.add_argument("--output", default=None, help="输出目录")
    parser.add_argument("--extract_only", action="store_true", help="仅提取因子逻辑，不进行回测")
    
    return parser.parse_args()

def process_report(args):
    """
    处理研究报告并生成因子逻辑
    """
    print("=== 开始处理研究报告 ===")
    
    # 初始化报告处理器
    report_processor = ReportProcessor()
    
    # 加载报告
    print(f"正在加载报告文件: {args.report}")
    content = report_processor.load_report(args.report)
    
    # 预处理报告内容
    content = report_processor.preprocess_report(content)
    
    # 提取报告元数据
    metadata = report_processor.extract_metadata(content)
    print(f"报告标题: {metadata['title']}")
    print(f"报告日期: {metadata['date']}")
    print(f"报告作者: {metadata['author']}")
    
    # 保存处理后的报告
    processed_report_path = report_processor.save_processed_report(content, metadata)
    print(f"处理后的报告已保存至: {processed_report_path}")
    
    # 初始化LLM管理器
    llm_manager = LLMManager(model=args.model) if args.model else LLMManager()
    print(f"使用的LLM模型: {llm_manager.model}")
    
    # 使用LLM提取因子逻辑
    print("正在提取因子逻辑...")
    factor_logic = llm_manager.extract_factor_logic(content)
    
    # 保存因子逻辑
    factor_name = metadata.get("title", "unknown").replace(" ", "_")[:20]
    factor_file = FactorUtils.save_factor_logic(factor_logic, factor_name)
    print(f"因子逻辑已保存至: {factor_file}")
    
    return factor_file, factor_logic, metadata

def run_backtest(factor_logic, args, metadata):
    """
    运行回测
    """
    print("\n=== 开始回测过程 ===")
    
    # 初始化LLM管理器和回测引擎
    llm_manager = LLMManager(model=args.model) if args.model else LLMManager()
    backtest_engine = BacktestEngine(
        start_date=args.start_date,
        end_date=args.end_date
    )
    
    # 生成回测代码
    print("正在生成回测代码...")
    backtest_code = llm_manager.generate_backtest_code(factor_logic)
    
    # 保存回测代码
    code_dir = os.path.join(project_root, "data", "backtest_code")
    os.makedirs(code_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    code_file = os.path.join(code_dir, f"backtest_{timestamp}.py")
    
    with open(code_file, 'w', encoding='utf-8') as f:
        f.write(backtest_code)
    print(f"回测代码已保存至: {code_file}")
    
    # 运行回测
    print("正在执行回测...")
    result = backtest_engine.run_backtest(backtest_code)
    
    if result:
        # 计算性能指标
        performance = backtest_engine.calculate_performance(result)
        
        # 保存回测结果
        factor_name = metadata.get("title", "unknown").replace(" ", "_")[:20]
        result_file = backtest_engine.save_result(performance, factor_name)
        print(f"回测结果已保存至: {result_file}")
        
        # 输出关键指标
        print("\n=== 回测结果 ===")
        print(f"总收益率: {performance['total_return']:.4f}")
        print(f"年化收益率: {performance['annualized_return']:.4f}")
        print(f"夏普比率: {performance['sharpe_ratio']:.4f}")
        print(f"最大回撤: {performance['max_drawdown']:.4f}")
        
        return performance
    else:
        print("回测执行失败")
        return None

def main():
    """主函数"""
    
    # 解析命令行参数
    args = parse_args()
    
    try:
        # 处理研究报告
        factor_file, factor_logic, metadata = process_report(args)
        
        # 执行回测
        if not args.extract_only:
            performance = run_backtest(factor_logic, args, metadata)
            
            if performance:
                print("\n研究报告复现完成!")
            else:
                print("\n研究报告复现失败，请检查日志和报告内容。")
        else:
            print("\n因子逻辑提取完成!")
            
    except Exception as e:
        print(f"程序执行出错: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 