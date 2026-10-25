# llm-agents-from-scratch

不依赖任何 Agent 框架，从零手写实现三种经典智能体范式，用于理解 Agent 的底层运行机制。

模型层使用 DeepSeek API（OpenAI 兼容协议），联网搜索使用 Tavily。

## 实现的三种范式

| 范式 | 核心循环 | 所在目录 | 关键组件 |
|---|---|---|---|
| ReAct | Thought → Action → Observation 循环 | `react/` | ToolExecutor、正则解析器、Finish 终止 |
| Plan-and-Solve | 先生成完整计划，再逐步执行 | `plan_solve/` | Planner、Executor |
| Reflection | 执行 → 评审 → 改进，迭代至满意 | `reflection/` | Memory、Reflector |

三种范式共用同一个模型客户端 `common/llm_client.py`，切换模型服务商只需修改 `.env`。

## 项目结构

```
agent/
├── common/
│   ├── llm_client.py    # LLM 客户端，支持流式/非流式
│   └── utils.py         # 安全的模板渲染（避免代码中的花括号炸掉 format）
├── react/
│   ├── tools.py         # 工具定义与执行器（Tavily 搜索、安全计算器）
│   └── agent.py         # ReAct 主循环与输出解析
├── plan_solve/
│   └── agent.py         # 计划生成与逐步执行
├── reflection/
│   └── agent.py         # 代码评审与迭代改进
└── main.py              # 统一入口
```

## 快速开始

### 1. 安装依赖

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

### 2. 配置密钥

在项目根目录创建 `.env`（此文件已被 .gitignore 排除，不会上传）：

```ini
LLM_API_KEY=sk-你的DeepSeek密钥
LLM_MODEL_ID=deepseek-v4-flash
LLM_BASE_URL=https://api.deepseek.com
LLM_TIMEOUT=60
TAVILY_API_KEY=tvly-你的Tavily密钥
```

DeepSeek 密钥在 platform.deepseek.com 申请，Tavily 密钥在 tavily.com 申请（有免费额度）。

### 3. 运行

```bash
python main.py react         # ReAct：多步工具调用
python main.py plan          # Plan-and-Solve：先规划后执行
python main.py reflection    # Reflection：代码生成与自我评审
```

## 运行示例

ReAct 范式回答"买 3 只最新款华为手表要多少钱"时的典型轨迹：

```
-----第 1 步-----
Thought: 需要先搜索华为2026年最新的手表型号
Action: Search[华为2026最新手表]
Observation: 华为 WATCH GT 6 系列于2026年发布...

-----第 2 步-----
Thought: 需要查询价格后计算总价
Action: Calculator[1999*3]
Observation: 5997

-----第 3 步-----
Action: Finish[2026年最新款为华为 WATCH GT 6，购买3只共需5997元]
```

## 学习笔记

实现过程中踩过的坑，记录在此供参考：

- 输出解析是 ReAct 稳定性的命门：模型会用全角冒号、代码块包裹、一次输出多个动作，解析器必须宽容，失败时要能回灌纠错而不是崩溃。
- 模板渲染用 `str.replace` 而不是 `str.format`：Reflection 场景要把模型生成的代码塞回模板，代码里的 `{}` 会让 format 直接报 KeyError。
- 工具执行出错应转成 Observation 回灌给模型自行纠错，而不是抛异常终止整个循环。
- max_steps / max_iterations 这类硬上限必须有，防止模型死循环烧掉额度。

## 参考

- 范式讲解参照 [hello-agents 第四章：智能体经典范式构建](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter4/%E7%AC%AC%E5%9B%9B%E7%AB%A0%20%E6%99%BA%E8%83%BD%E4%BD%93%E7%BB%8F%E5%85%B8%E8%8C%83%E5%BC%8F%E6%9E%84%E5%BB%BA.md)
- [DeepSeek API 文档](https://api-docs.deepseek.com/)
- [Tavily API](https://docs.tavily.com/)

## 声明

本项目仅用于学习交流，不构成任何生产级方案。
