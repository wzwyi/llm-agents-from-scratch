from typing import List, Dict, Optional

from common.llm_client import BaseAgentsLLM
from common.utils import render

INITIAL_PROMPT = """你是一位资深 Python 程序员，请完成任务并给出完整函数。

任务：{task}

要求：
1. 包含函数签名和简短文档字符串。
2. 只输出代码，不要解释，不要 Markdown 代码块。
"""

REFLECT_PROMPT = """你是一位极严格的代码评审专家，重点检查算法效率。

任务：{task}
当前代码：
{code}

要求：
1. 指出时间/空间复杂度，以及潜在 bug。
2. 如果代码已经足够好，第一行只输出：无需改进
3. 否则给出 1 到 3 条具体、可执行的改进建议。
"""

REFINE_PROMPT = """你是一位资深 Python 程序员，请根据评审意见改进代码。

任务：{task}
上一版代码：
{code}
评审意见：
{feedback}

要求：只输出改进后的完整代码，不要解释。
"""

class Memory:
    def __init__(self):
        self.records: List[Dict[str, str]] = []

    def add(self, record_type: str, content: str):
        self.records.append({"type": record_type, "content": content})

    def last_execution(self) -> Optional[str]:
        for record in reversed(self.records):
            if record["type"] == "execution":
                return record["content"]
        return None

class ReflectionAgent:
    def __init__(self, llm: BaseAgentsLLM, max_iteration: int = 3):
        self.llm = llm
        self.max_iteration = max_iteration
        self.memory = Memory()

    def _ask(self, prompt: str) -> str:
        return self.llm.think([{"role": "user", "content": prompt}]).strip()

    def run(self, task: str) -> str:
        code = self._ask(render(INITIAL_PROMPT, task=task))
        self.memory.add("execution", code)
        print("--------------初版代码--------------\n" + code + "\n")

        for i in range(self.max_iteration):
            feedback = self._ask(render(REFLECT_PROMPT, task=task, code=code))
            self.memory.add("reflection", feedback)
            print(f"---------------第{i+1}轮评审---------------\n{feedback}\n")

            if "无需改进" in feedback:
                break

            code = self._ask(render(REFINE_PROMPT, task=task, feedback=feedback, code=code))
            self.memory.add("execution", code)
            print(f"---------------第{i+1}轮改进---------------\n{code}\n")

        return self.memory.last_execution()

if __name__ == "__main__":
    reflectionAgent = ReflectionAgent(llm=BaseAgentsLLM())
    reflectionAgent.run("写一个函数 max_subarray_sum(nums)，求列表中和最大的连续子数组。")