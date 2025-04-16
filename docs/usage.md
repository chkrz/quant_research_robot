# 量化研究报告复现机器人使用说明

## 环境准备

1. 确保已安装Python 3.8或更高版本
2. 安装Poetry（包管理工具）

```bash
# 安装Poetry
curl -sSL https://install.python-poetry.org | python3 -
```

3. 安装项目依赖

```bash
# 进入项目目录
cd quant_research_robot

# 使用Poetry安装依赖
poetry install
```

4. 配置环境变量，创建`.env`文件（参考`.env.example`）

```bash
# 复制示例配置文件
cp .env.example .env

# 编辑配置文件，填入您的API密钥
poetry run nano .env
```

## 基本用法

### 处理研究报告并回测

```bash
# 使用Python运行
poetry run python main.py --report path/to/your/report.pdf

# 或使用配置好的脚本
poetry run quant-robot --report path/to/your/report.pdf
```

### 仅提取因子逻辑，不进行回测

```bash
poetry run quant-robot --report path/to/your/report.pdf --extract_only
```

### 指定回测时间范围

```bash
poetry run quant-robot --report path/to/your/report.pdf --start_date 2020-01-01 --end_date 2023-12-31
```

### 使用特定LLM模型

```bash
poetry run quant-robot --report path/to/your/report.pdf --model gpt-4-turbo
```

## 开发环境

进入Poetry的虚拟环境进行开发：

```bash
# 激活虚拟环境
poetry shell

# 然后可以直接运行命令，无需poetry run前缀
python main.py --report path/to/your/report.pdf
```

## 添加新的依赖

```bash
# 添加新的生产依赖
poetry add package-name

# 添加开发依赖
poetry add --group dev package-name
```

## 输出内容

程序运行后，会在`data`目录中生成以下文件：

1. `factors/` - 保存提取的因子逻辑
2. `backtest_code/` - 保存生成的回测代码
3. `results/` - 保存回测结果

## 回测结果

回测结果包含以下主要指标：

- 总收益率(total_return)
- 年化收益率(annualized_return)
- 夏普比率(sharpe_ratio)
- 最大回撤(max_drawdown)
- 分档收益率(monthly_returns)

## 示例

假设您有一篇研究报告`momentum_research.pdf`，通过以下命令处理：

```bash
poetry run quant-robot --report data/reports/momentum_research.pdf --model gpt-4 --start_date 2018-01-01 --end_date 2022-12-31
```

程序会执行以下步骤：

1. 加载并预处理研究报告
2. 使用GPT-4模型提取报告中的因子逻辑
3. 保存因子逻辑到`data/factors/`目录
4. 生成回测代码并保存到`data/backtest_code/`目录
5. 使用vnpy执行回测（回测区间为2018年至2022年）
6. 计算性能指标并保存结果到`data/results/`目录

## 注意事项

1. 需要安装vnpy及其依赖库（已包含在Poetry依赖中）
2. PDF和Word文档需要安装额外的依赖库（可通过`poetry add pdfplumber python-docx`安装）
3. 不同的研究报告格式和内容可能会影响因子提取效果
4. 部分高级因子可能需要更复杂的回测代码，请检查生成的代码 