import sys

from common.llm_client import BaseAgentsLLM
from plan_solve.agent import PlanAndSolveAgent
from react.agent import ReActAgent
from react.tools import ToolExecutor, calculator, search
from reflection.agent import ReflectionAgent


def run_react():
    executor = ToolExecutor()
    executor.register("Search", "联网搜索实时信息，输入为搜索关键词", search)
    executor.register("Calculator", "四则运算，输入如 12.6/4.2", calculator)
    agent = ReActAgent(BaseAgentsLLM(), executor)
    print(agent.run("华为2026年最新出的手表是哪一款，如果买3只最新款华为手表，要多少钱？"))


def run_plan():
    agent = PlanAndSolveAgent(BaseAgentsLLM())
    agent.run("某公司2026年营收1.2亿元，同比增长20%；若2027年保持同样增速，2028年营收是多少？")


def run_reflection():
    task = "写一个函数 max_subarray_sum(nums)，求列表中和最大的连续子数组。"
    print(ReflectionAgent(BaseAgentsLLM()).run(task))


if __name__ == "__main__":
    choice = sys.argv[1] if len(sys.argv) > 1 else "react"
    {"react": run_react, "plan": run_plan, "reflection": run_reflection}[choice]()
