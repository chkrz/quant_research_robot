import os
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()

# API密钥配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# 模型配置
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4")
MODEL_TEMPERATURE = float(os.getenv("MODEL_TEMPERATURE", "0.1"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "4096"))

# 回测配置
BACKTEST_START_DATE = os.getenv("BACKTEST_START_DATE", "2018-01-01")
BACKTEST_END_DATE = os.getenv("BACKTEST_END_DATE", "2023-12-31")
DEFAULT_CAPITAL = float(os.getenv("DEFAULT_CAPITAL", "1000000"))  # 默认回测资金

# 数据存储路径
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
REPORTS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src/reports")