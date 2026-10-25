from common.llm_client import BaseAgentsLLM
from common.utils import render

PLANNER_PROMPT = """你是一个任务规划专家，请把问题拆成有序、可独立执行的子步骤。

要求：
1. 后一步可以使用前一步的结果，但不要重复。
2. 3 到 5 步为宜。
3. 只输出一个 Python 列表，不要任何解释。

格式：
["步骤1", "步骤2", "步骤3"]

问题：{question}
"""

EXECUTOR_PROMPT = """你是一个执行专家。请只解决"当前步骤"，不要提前做后面的步骤。

原始问题：{question}
完整计划：{plan}
已完成步骤与结果：
{history}

当前步骤：{current_step}

要求：直接给出这一步的结论，简洁，不要复述计划。
"""

class Planner:
    def __init__(self, llm: BaseAgentsLLM):
        self.llm = llm

    def plan(self, question: str):
        text = self.llm.think([{"role": "user", "content": render(PLANNER_PROMPT, question=question)}])
        block = text
        if "```" in text:
            block = text.split("```")[1].replace("python", "", 1)
        try:
            steps = eval(block.strip(), {"__builtins__":{}}, {})
        except Exception:
            return []
        return steps if isinstance(steps, list) else []

class Executor:
    def __init__(self, llm: BaseAgentsLLM):
        self.llm = llm

    def execute(self, question: str, plan: list) -> str:
        history = ""
        plan_text = "\n".join(f"{i}. {s}" for i, s in enumerate(plan,1))
        for i, step in enumerate(plan, 1):
            prompt = render(
                EXECUTOR_PROMPT,
                question = question,
                plan = plan_text,
                history = history or "暂无",
                current_step = step
            )
            result = self.llm.think([{"role": "user", "content": prompt}]).strip()
            print(f"[{i}/{len(plan)}] {step}\n      →{result}\n")
            history += f"步骤{i}: {step}\n结果： {result}\n"
        return history

class PlanAndSolveAgent:
    def __init__(self, llm:BaseAgentsLLM):
        self.planner = Planner(llm)
        self.executor = Executor(llm)

    def run(self, question: str):
        plan = self.planner.plan(question)
        if not plan:
            return "计划生成失败"
        print("生成计划")
        for i, step in enumerate(plan,1):
            print(f"{i}. {step}")
        print()
        return self.executor.execute(question, plan)

if __name__ == "__main__":
    planAndSolveAgent = PlanAndSolveAgent(llm=BaseAgentsLLM())
    answer = planAndSolveAgent.run("某公司2026年营收1.2亿元，同比增长20%；若2027年保持同样增速，2028年营收是多少？")
    print(f"\n------------------最终的答案是-------------------\n{answer}")