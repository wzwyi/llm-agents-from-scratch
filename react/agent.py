import re

from common.llm_client import BaseAgentsLLM
from common.utils import render
from react.tools import ToolExecutor, search, calculator

REACT_PROMPT = """你是一个可以使用外部工具的智能助手。

可用工具：
{tools}

输出格式（每次只输出一个动作）：
Thought: 一句话说明你下一步要做什么
Action: 工具名[输入]

信息足够时用：
Thought: 我已经可以回答
Action: Finish[最终答案]

规则：
1. 工具名必须是上面列表中的一个，或 Finish。
2. 输入直接写在方括号内，不要加引号、不要换行。
3. 需要算术时必须调用 Calculator，不要心算。
4. 每次只输出一个 Action。

已执行步骤：
{history}

问题：{question}
"""

ACTION_RE = re.compile(r"Action\s*[:：]\s*(.+)", re.S)
CALL_RE = re.compile(r"(\w+)\[(.*)\]", re.S)

class ReActAgent:
    def __init__(self, llm: BaseAgentsLLM, tool_executor, max_steps: int = 6):
        self.llm = llm
        self.tools = tool_executor
        self.max_steps = max_steps
        self.history = []

    def _parse(self, text: str):
        match = ACTION_RE.search(text)
        if not match:
            return None, None
        call = CALL_RE.search(match.group(1).strip())
        if not call:
            return None, None
        return call.group(1).strip(), call.group(2).strip()

    def run(self, question: str):
        self.history = []
        for step in range(self.max_steps):
            prompt = render(
                REACT_PROMPT,
                tools=self.tools.describe(),
                history="\n".join(self.history) or "（暂无）",
                question=question
            )
            output = self.llm.think([{"role": "user", "content": prompt}])

            print(f"\n-----第 {step + 1} 步-----")
            print(output.strip())

            tool_name, tool_input = self._parse(output)
            if tool_name is None:
                self.history.append("Observation: 输出格式不对，请严格按 Thought/Action 两行输出。")
                continue

            if tool_name.lower() == "finish":
                return tool_input

            func = self.tools.get(tool_name)
            if func is None:
                observation = f"错误，没有名为 {tool_name} 的工具"
            else:
                observation = func(tool_input)

            print(f"Observation: {observation}")
            self.history.append((f"Action: {tool_name}[{tool_input}]"))
            self.history.append(f"Observation: {observation}")

        return "已达最大步数仍未得出结论"

if __name__ == "__main__":
    e = ToolExecutor()
    e.register('Search', '联网搜索实时信息，输入为搜索关键词', search)
    e.register('Calculator', '四则运算，输入如 12.6/4.2', calculator)
    reActAgent = ReActAgent(llm=BaseAgentsLLM(), tool_executor=e)

    text = reActAgent.run("华为2026年最新出的手表是哪一款，如果买3只最新款华为手表，要多少钱？")
    print(f"\n------------最终答案为：--------------------\n{text}")