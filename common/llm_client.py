import os
from typing import List, Dict

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class BaseAgentsLLM:
    """LLM客户端，用于调用任何兼容OpenAi接口的服务"""

    def __init__(self, model: str = None, api_key: str = None, base_url: str = None, timeout: int = None, stream=False):
        """
        初始化客户端。优先使用传入参数，如果未提供，则从环境变量中加载
        """
        self.model = model or os.getenv("LLM_MODEL_ID")
        self.api_key = api_key or os.getenv("LLM_API_KEY")
        self.base_url = base_url or os.getenv("LLM_BASE_URL")
        self.timeout = int(timeout or os.getenv("LLM_TIMEOUT", 60))
        self.stream = stream

        if not all([self.model, self.api_key, self.base_url]):
            raise ValueError("模型ID、API密钥和服务地址必须被提供或在.env文件中定义。")

        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url, timeout=self.timeout)

    def think(self, messages: List[Dict[str, str]], temperature: float = 0.3) -> str:
        """
        调用大语言模型进行思考，并返回其响应。
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            stream=self.stream,
        )

        if not self.stream:
            return response.choices[0].message.content or ""

        parts = []
        for chunk in response:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta.content
            if delta:
                parts.append(delta)
                print(delta, end="", flush=True)
        print()
        return "".join(parts)