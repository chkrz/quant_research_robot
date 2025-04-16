import asyncio
import json
import os
from litellm import acompletion
from dotenv import load_dotenv
from pydantic import BaseModel
import re

load_dotenv()

# Get API key and endpoint from environment variables
api_key = os.getenv("OPENAI_API_KEY")
api_base = os.getenv("OPENAI_ENDPOINT", "https://api.openai.com/v1")
deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
deepseek_api_base = os.getenv("DEEPSEEK_ENDPOINT", "https://ark.cn-beijing.volces.com/api/v3")
silicon_flow_api_key = os.getenv("SILICON_FLOW_API_KEY")
silicon_flow_api_base = os.getenv("SILICON_FLOW_ENDPOINT", "https://api.siliconflow.cn/v1")

# Configure o3-mini model
O3MiniModel = {
    "model": 'o3-mini',
    "api_key": api_key,
    "api_base": api_base,
    "max_tokens": 4000,
    "temperature": 1
}

O3MiniModelForEssay = {
    "model": 'o3-mini',
    "api_key": api_key,
    "api_base": api_base,
    "max_tokens": 32768,
    "temperature": 1
}


DeepSeekModel = {
    "model": "deepseek/deepseek-r1-250120",
    "api_key": deepseek_api_key,
    "api_base": deepseek_api_base,
    "max_tokens": 8192,
    "temperature": 0.8
}


DeepSeekModelForEssay = {
    "model": "deepseek/deepseek-r1-250120",
    "api_key": deepseek_api_key,
    "api_base": deepseek_api_base,
    "max_tokens": 16384,
    "temperature": 0.1
}

DSV3ModelLT = {
    "model": "deepseek/deepseek-v3-241226",
    "api_key": deepseek_api_key,
    "api_base": deepseek_api_base,
    "max_tokens": 2048,
    "temperature": 0.1
}

ClaudeSonnet37Model = {
    # "model": "bedrock/us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    "model": "bedrock/us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    "max_tokens": 8192,
    "temperature": 0.8,
    # fixme: when enable thinking, tool_choice error, likely tobe litllm bug or not the right way to use
    # "thinking": {"type": "enabled", "budget_tokens": 1024},
}


def fix_json_string(json_str):
    """
    修复 JSON 字符串中值部分出现未转义的双引号问题。
    例如将 ...海洋十年大会"国际合作"主题... 转换为 ...海洋十年大会\"国际合作\"主题...
    """
    # 首先，如果没有扩死的括号，补上试试
    if not json_str.startswith("{"):
        json_str = "{" + json_str
    if not json_str.endswith("}"):
        json_str = json_str + "}"
    # 这里的正则：
    # 1. (:\s*") 捕获冒号后紧跟的引号（value 的起始部分）
    # 2. ((?:.|\n)*?) 非贪婪捕获内部内容（允许换行）
    # 3. ("(?=\s*[,}\]])) 捕获紧跟的双引号，此双引号后面紧跟逗号、}或]（表示结束）
    pattern = re.compile(r'(:\s*")((?:.|\n)*?)("(?=\s*[,}\]]))')

    def replacer(match):
        prefix = match.group(1)  # 包含冒号和起始双引号
        content = match.group(2)  # 值字符串内部的内容
        suffix = match.group(3)  # 结尾的双引号

        # 对内部内容进行处理：将未转义的 " 替换为 \" ，这里用负向前瞻判断不在反斜杠后面
        fixed_content = re.sub(r'(?<!\\)"', r'\\"', content)
        return prefix + fixed_content + suffix

    return pattern.sub(replacer, json_str)


async def generate_text(*, model: dict, system: str | None = None, prompt: str,
                        context: list[dict[str, str]] | None = None,
                        with_reasoning: bool = False):
    """
    Generate a text response using litellm
    """
    """
    Generate a text response using litellm

    Args:
        model: Model configuration dictionary
        system: System prompt
        prompt: User prompt
        context: Context for the prompt
        with_reasoning: Whether to return reasoning along with the response
    """
    if model["model"].startswith("deepseek"):
        messages = [{"role": "user", "content": prompt}]
    else:
        messages = [{"role": "user", "content": prompt}]
    
    print('\033[32mPrompt: \n', messages[0]["content"], '\033[0m')
    
    if context is not None:
        if system and not context:
            messages.insert(0, {"role": "system", "content": f"{system}"})
        context.extend(messages)
        messages = context
    else:
        if system:
            messages.insert(0, {"role": "system", "content": f"{system}"})

    response = await acompletion(
        messages=messages,
        **model
    )
    
    content = response.choices[0].message.content.strip()
    message = response.choices[0].message
    reasoning = (message.get('provider_specific_fields') or {}).get('reasoning_content', '') if isinstance(message, dict) else ((getattr(message, 'provider_specific_fields') or {}).get('reasoning_content', '') if message else '')
    
    if with_reasoning:
        return reasoning, content
    return content


async def generate_dict(*, model: dict, system: str | None = None, prompt: str, 
                        schema: dict | BaseModel,
                        context: list[dict[str, str]] | None = None,
                        with_reasoning: bool = False,
                        max_retries: int = 3):
    """
    Generate a structured response using litellm

    Args:
        model: Model configuration dictionary
        system: System prompt
        prompt: User prompt
        schema: JSON schema for response validation
        context: Context for the prompt
        with_reasoning: Whether to return reasoning along with the response
        max_retries: Maximum number of retry attempts if JSON parsing fails
    """
    if isinstance(schema, dict):
        if model["model"].startswith("deepseek"):
            content = f"{prompt}\n\n您必须按照此模式以有效的JSON格式进行响应（注意字符串中的双引号需要转义）：\n{json.dumps(schema, indent=2, ensure_ascii=False)}"
        else:
            content = f"{prompt}\n\nYou must respond in valid JSON format according to this schema:\n{json.dumps(schema, indent=2, ensure_ascii=False)}"
    elif isinstance(schema, BaseModel):
        content = prompt
    else:
        raise ValueError(f"Invalid schema type: {type(schema)}")
    messages = [{"role": "user", "content": content}]
    print('\033[32mPrompt: \n', messages[0]["content"], '\033[0m')
    if context is not None:
        if system and not context:
            messages.insert(0, {"role": "system", "content": f"{system}"})
        context.extend(messages)
        messages = context
    else:
        if system:
            messages.insert(0, {"role": "system", "content": f"{system}"})

    support_json_schema = "DeepSeek-V3" not in model["model"]
    
    retry_count = 0
    while retry_count < max_retries:
        try:
            if isinstance(schema, BaseModel):
                response = await acompletion(
                    messages=messages,
                    response_format=schema,
                    **model
                )
            else:
                response = await acompletion(
                    messages=messages,
                    response_format={"type": "json_object"} if support_json_schema else None,
                    **model
                )
            json_content = response.choices[0].message.content.strip()
            if json_content.startswith("```json"):
                json_content = json_content[len("```json"):].strip()
            if json_content.endswith("```"):
                json_content = json_content[:-len("```")]
            message = response.choices[0].message
            # TODO: support claude litellm
            reasoning = (message.get('provider_specific_fields') or {}).get('reasoning_content', '') if isinstance(message, dict) else ((getattr(message, 'provider_specific_fields') or {}).get('reasoning_content', '') if message else '')
            
            parsed_json = json.loads(fix_json_string(json_content.strip()))
            
            if context:
                context.append({"role": "assistant", "content": json.dumps(parsed_json, indent=2, ensure_ascii=False)})
            
            if with_reasoning:
                return reasoning, parsed_json
            else:
                return parsed_json
                
        except Exception as e:
            retry_count += 1
            if retry_count >= max_retries:
                reasoning, parsed_json = None, None
                import pdb;
                pdb.set_trace()  # 为了防止完全浪费，你自己修好他然后赋值给parsed_json继续
                
                if with_reasoning:
                    return reasoning, parsed_json
                else:
                    return parsed_json
            
            print(f"\033[31mRetry {retry_count}/{max_retries}: JSON parsing failed: {e}\033[0m")
