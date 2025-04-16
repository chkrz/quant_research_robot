import os
import sys
import json
import asyncio
from typing import Dict, Any, List, Optional

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.llms import generate_text, generate_dict, ClaudeSonnet37Model, O3MiniModel, DeepSeekModel

class ResearchProcessor:
    """
    研究报告处理器，负责提取因子逻辑并生成回测代码
    支持多轮执行和迭代改进
    """
    
    def __init__(self, model=ClaudeSonnet37Model):
        """
        初始化研究处理器
        
        Args:
            model: 使用的模型配置
        """
        self.model = model
        self.conversation_context = []
    
    async def extract_factor_logic(self, research_report: str) -> Dict[str, Any]:
        """
        提取研究报告中的因子逻辑
        
        Args:
            research_report: 研究报告文本
            
        Returns:
            包含因子逻辑的字典
        """
        system_message = "你是一个专业的量化金融分析师，精通因子挖掘和策略构建。"
        
        prompt = f"""
        请分析以下量化研究报告，并提取其中的因子逻辑。
        需要包括以下内容：
        1. 因子名称
        2. 因子定义和计算逻辑
        3. 因子参数
        4. 数据要求
        5. 选股逻辑
        
        研究报告：
        {research_report}
        """
        
        # 定义返回结果的模式
        schema = {
            "type": "object",
            "properties": {
                "factor_name": {"type": "string", "description": "因子名称"},
                "definition": {"type": "string", "description": "因子定义和计算逻辑"},
                "parameters": {"type": "array", "items": {"type": "object"}, "description": "因子参数列表"},
                "data_requirements": {"type": "array", "items": {"type": "string"}, "description": "所需数据列表"},
                "stock_selection": {"type": "string", "description": "选股逻辑"}
            },
            "required": ["factor_name", "definition", "parameters", "data_requirements", "stock_selection"]
        }
        
        # 使用上下文进行多轮对话
        factor_logic = await generate_dict(
            model=self.model,
            system=system_message,
            prompt=prompt,
            schema=schema,
            context=self.conversation_context
        )
        
        return factor_logic
    
    async def generate_backtest_code(self, factor_logic: Dict[str, Any]) -> str:
        """
        根据因子逻辑生成回测代码
        
        Args:
            factor_logic: 因子逻辑字典
            
        Returns:
            可执行的vnpy回测代码
        """
        system_message = "你是一个专业的量化策略师，精通Python和vnpy回测框架。"
        
        prompt = f"""
        请根据以下因子逻辑，编写一个基于vnpy的回测代码。
        代码需要包括：
        1. 因子计算
        2. 选股逻辑
        3. 回测设置
        4. 性能评估
        
        因子逻辑：
        {json.dumps(factor_logic, ensure_ascii=False, indent=2)}
        
        请确保代码可以直接运行，并且符合vnpy框架的接口规范。
        """
        
        # 使用上下文继续多轮对话
        backtest_code = await generate_text(
            model=self.model,
            system=system_message,
            prompt=prompt,
            context=self.conversation_context
        )
        
        return backtest_code
    
    async def refine_backtest_code(self, backtest_code: str, feedback: str) -> str:
        """
        根据反馈优化回测代码
        
        Args:
            backtest_code: 当前回测代码
            feedback: 用户反馈或错误信息
            
        Returns:
            优化后的回测代码
        """
        system_message = "你是一个专业的量化策略师，精通Python和vnpy回测框架。"
        
        prompt = f"""
        请根据以下反馈修改vnpy回测代码。
        
        当前代码：
        ```python
        {backtest_code}
        ```
        
        反馈或错误信息：
        {feedback}
        
        请修正代码中的问题，确保可以正常执行。
        """
        
        # 使用上下文继续多轮对话
        refined_code = await generate_text(
            model=self.model,
            system=system_message,
            prompt=prompt,
            context=self.conversation_context
        )
        
        return refined_code
    
    def clear_context(self):
        """
        清除对话上下文，开始新的处理流程
        """
        self.conversation_context = []

# 使用示例
async def main():
    processor = ResearchProcessor()
    
    # 示例研究报告
    research_report = """这里是研究报告内容..."""
    
    # 提取因子逻辑
    factor_logic = await processor.extract_factor_logic(research_report)
    print("因子逻辑:", factor_logic)
    
    # 生成回测代码
    backtest_code = await processor.generate_backtest_code(factor_logic)
    print("回测代码:", backtest_code)
    
    # 假设执行后收到错误反馈
    feedback = "代码在执行时出现ImportError，缺少相关库的导入"
    
    # 优化回测代码
    refined_code = await processor.refine_backtest_code(backtest_code, feedback)
    print("优化后的代码:", refined_code)

if __name__ == "__main__":
    asyncio.run(main()) 