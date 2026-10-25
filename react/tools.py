import os
from typing import Dict, Callable

from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

def search(query: str) -> str:
    """使用 Tavily 联网搜素，返回整合后的结果"""
    tavily_key = os.getenv("TAVILY_API_KEY")
    if not tavily_key:
        raise ValueError("未找到 TAVILY_API_KEY 请检查.env文件")

    tavilyClient = TavilyClient(api_key=tavily_key)

    query = query.strip()
    if not query:
        return "错误，搜索关键词为空"

    try:
        response = tavilyClient.search(
            query,
            search_depth="basic",
            max_results=5,
            include_answer=True
        )
    except Exception as exc:
        return f"搜索出错：{exc}"

    if response.get("answer"):
        return response["answer"]

    results = response.get("results") or []
    if not results:
        return "未找到相关信息"

    formatted = []
    for r in results:
        title = r.get("title", "")
        url = r.get("url", "")
        content = r.get("content", "")
        formatted.append(f"[{title}]({url}):{content}")
    return "\n\n".join(formatted)


def calculator(expression: str) -> str:
    """只允许四则运算，防止执行任何代码"""
    allowed = set("0123456789+-*/().")
    if not set(expression) <= allowed:
        return "错误：表达式只允许数字和 + - * / ( )"
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as exc:
        return f"错误：{exc}"

class ToolExecutor:
    def __init__(self):
        self.tools: Dict[str, dict] = {}

    def register(self, name: str, description: str, func: Callable):
        self.tools[name] = {"description": description, "func": func}

    def get(self, name: str):
        tool = self.tools.get(name)
        return tool["func"] if tool else None

    def describe(self) -> str:
        return "\n".join(f"- {name}: {t['description']}" for name, t in self.tools.items())