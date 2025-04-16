import litellm
from litellm import completion
import sys
import os

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config.config import (
    OPENAI_API_KEY, 
    ANTHROPIC_API_KEY, 
    GEMINI_API_KEY,
    DEFAULT_MODEL,
    MODEL_TEMPERATURE,
    MAX_TOKENS
)

class LLMManager:
    """
    LLM调用管理器，负责与不同的大语言模型进行交互
    """
    
    def __init__(self, model=DEFAULT_MODEL, temperature=MODEL_TEMPERATURE, max_tokens=MAX_TOKENS):
        """
        初始化LLM管理器
        
        Args:
            model: 使用的模型名称
            temperature: 生成文本的随机性
            max_tokens: 最大生成Token数
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # 设置API密钥
        os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
        os.environ["ANTHROPIC_API_KEY"] = ANTHROPIC_API_KEY
        os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY
        
        # 初始化litellm
        litellm.drop_params = True  # 丢弃不支持的参数
    
    def get_completion(self, prompt, system_message=None):
        """
        获取模型对提示的回复
        
        Args:
            prompt: 提交给模型的提示
            system_message: 系统消息（可选）
            
        Returns:
            模型生成的回复文本
        """
        messages = []
        
        if system_message:
            messages.append({"role": "system", "content": system_message})
            
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = completion(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"LLM调用错误: {e}")
            return None
    
    def extract_factor_logic(self, research_report):
        """
        提取研究报告中的因子逻辑
        
        Args:
            research_report: 研究报告文本
            
        Returns:
            包含因子逻辑的字典
        """
        prompt = f"""
        请分析以下量化研究报告，并提取其中的因子逻辑。
        需要包括以下内容：
        1. 因子名称
        2. 因子定义和计算逻辑
        3. 因子参数
        4. 数据要求
        5. 选股逻辑
        
        请使用JSON格式输出结果。
        
        研究报告：
        {research_report}
        """
        
        system_message = "你是一个专业的量化金融分析师，精通因子挖掘和策略构建。"
        
        response = self.get_completion(prompt, system_message)
        return response
    
    def generate_backtest_code(self, factor_logic):
        """
        根据因子逻辑生成回测代码
        
        Args:
            factor_logic: 因子逻辑
            
        Returns:
            可执行的回测代码
        """
        prompt = f"""
        请根据以下因子逻辑，编写一个基于vnpy的回测代码。
        代码需要包括：
        1. 因子计算
        2. 选股逻辑
        3. 回测设置
        4. 性能评估
        
        因子逻辑：
        {factor_logic}
        """
        
        system_message = "你是一个专业的量化策略师，精通Python和vnpy回测框架。"
        
        response = self.get_completion(prompt, system_message)
        return response