# 量化研究报告复现机器人(Quant Research Robot)

基于LLM的能力，自动复现量化领域的研究报告。

## 功能特点

- 使用litellm调用各种大语言模型
- 基于vnpy实现回测框架
- 输入研究报告，自动提取因子逻辑并进行策略回测
- 输出策略表现指标（分档收益率、夏普比率等）

## 环境准备

### 安装Poetry

如果你还没有安装Poetry，请按照[官方文档](https://python-poetry.org/docs/#installation)进行安装：

```bash
# 推荐的安装方式
curl -sSL https://install.python-poetry.org | python3 -
```

### 安装项目依赖

```bash
# 克隆项目
git clone https://github.com/yourusername/quant_research_robot.git
cd quant_research_robot

# 使用Poetry安装依赖
poetry install
```

### 配置环境变量

创建`.env`文件，配置必要的API密钥和参数：

```bash
# 复制示例配置文件
cp .env.example .env

# 编辑配置文件
poetry run nano .env
```

## 使用方法

### 使用Poetry运行

```bash
# 处理研究报告并回测
poetry run python main.py --report path/to/your/report.pdf

# 或使用配置好的脚本
poetry run quant-robot --report path/to/your/report.pdf
```

### 其他常用命令

```bash
# 仅提取因子逻辑，不进行回测
poetry run quant-robot --report path/to/your/report.pdf --extract_only

# 指定回测时间范围
poetry run quant-robot --report path/to/your/report.pdf --start_date 2020-01-01 --end_date 2023-12-31

# 指定使用的LLM模型
poetry run quant-robot --report path/to/your/report.pdf --model gpt-4
```

详细的使用说明请参考[使用文档](docs/usage.md)。