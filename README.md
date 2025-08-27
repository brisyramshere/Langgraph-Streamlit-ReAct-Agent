# 🤖 通用 ReAct Agent 模板（LangGraph + Streamlit）

本项目是一个基于 LangGraph 和 Streamlit 的通用 ReAct Agent 模板。它已实现：
- ReAct（推理-行动）循环
- 工具调用（Tavily 网页搜索、子 Agent 示例）
- 流式显示与过程可视化
- 动态提示词注入与文件上下文感知
- 针对空回复/截断的鲁棒重试机制

本 README 已根据当前代码仓库的实际结构与实现（graph.py、streamlit_app.py 等）更新。

## ✨ 核心特性

- 先进的 ReAct 架构：基于 LangGraph 的 StateGraph 搭建可视化、可扩展的 Agent 工作流。
- 流式响应与过程展示：聊天内容、工具调用、工具结果逐步呈现（含可展开详情）。
- 健壮的错误处理：捕获空内容与特定 finish_reason（length/content_filter/null），自动丢弃并重试（最多 3 次）。
- 可插拔工具：tools/ 下内置 Tavily 搜索与 Sub-Agent 占位工具，便于扩展。
- 灵活模型配置：通过 ConfigManager 在 UI 中动态切换模型配置（OpenAI 兼容）。
- 动态提示词注入：自动将上传文件清单注入系统提示词（AGENT_SYSTEM_PROMPT）。

## 📂 目录结构（基于当前仓库根目录）

```
react-agent-template/
├── tools/
│   ├── __init__.py
│   ├── web_search.py          # Tavily 搜索工具
│   └── sub_agent_tool.py      # 子 Agent 执行器（示例/占位）
├── __init__.py
├── .env                       # 环境变量（自行创建）
├── configs.py                 # ConfigManager：模型配置与切换
├── models.py                  # get_llm_instance：LLM 工厂（当前支持 OpenAI 兼容）
├── prompts.py                 # 系统提示词（AGENT_SYSTEM_PROMPT）
├── state.py                   # AgentState（消息、scratchpad、finish_reason、retry_count）
├── graph.py                   # 工作流与路由（StateGraph/ToolNode/MemorySaver）
├── streamlit_app.py           # Streamlit UI（聊天、上传、模型选择、流式渲染）
├── requirements.txt           # 依赖清单
└── README.md
```

与旧版 README 不同：本仓库没有 template/ 子目录；核心文件位于项目根目录，工作流文件为 graph.py（而非 agent_workflow.py），配置为 configs.py（而非 config_manager.py）。

## 🚀 快速开始

1) 准备环境（建议 Python 3.10+）

- 创建并激活虚拟环境：
  - Windows (PowerShell)
    - python -m venv .venv
    - .venv\Scripts\Activate.ps1
  - macOS / Linux
    - python -m venv .venv
    - source .venv/bin/activate

2) 安装依赖

- pip install -r requirements.txt

3) 配置环境变量（在项目根目录创建 .env）

示例：

- TAVILY_API_KEY="tvly-..."        # Tavily 搜索（可在 https://tavily.com/ 免费获取）
- OPENAI_API_KEY="sk-..."          # OpenAI 兼容 API Key
- OPENAI_API_BASE="https://..."    # 可选：自定义兼容接口 Base URL

4) 运行应用

- streamlit run streamlit_app.py

浏览器将打开可交互页面。

## 🧠 工作流与关键实现

- 文件：graph.py
  - AgentWorkflow 构建 StateGraph，包含节点：
    - agent：核心 LLM 节点（_call_model）。动态注入系统提示词，将上传文件清单（uploaded_file_paths）以 JSON 形式写入 AGENT_SYSTEM_PROMPT。
    - tools：使用 LangGraph 预置 ToolNode 执行工具（tavily_tool、sub_agent_executor_tool）。
    - discard_and_retry：丢弃上一个空回复消息，retry_count + 1，并回到 agent。
  - 条件路由（route_after_llm_call）：
    - 如果 finish_reason 属于 ["length", "content_filter", "null"] 或 AIMessage 为空（无 content 且无 tool_calls），进入 discard_and_retry，最多重试 3 次（MAX_EMPTY_RETRIES=3）。
    - 如果消息包含 tool_calls，流转至 tools。
    - 否则结束（END）。
  - Checkpoint：使用 MemorySaver 实现对话检查点；UI 以 thread_id（session_id）区分会话。

- 文件：state.py
  - AgentState 使用 Annotated[List[BaseMessage], add_messages] 管理消息累积；包含 scratchpad、finish_reason、retry_count。

- 文件：models.py
  - get_llm_instance 依据 provider 创建 LLM，目前支持 provider=openai（langchain_openai.ChatOpenAI），开启 streaming。

- 文件：configs.py
  - ConfigManager 提供多组模型配置与 UI 切换；默认包含 "Qwen3-Coder-480B"（以 OpenAI 兼容方式调用）与 "qwen-turbo" 示例配置（需要你扩展 models.py 才能生效）。

- 文件：tools/
  - web_search.py：TavilySearchResults 工具，需设置 TAVILY_API_KEY。
  - sub_agent_tool.py：子 Agent 执行器占位（@tool）；可替换为真实子 Agent 或 Chain。

- 文件：streamlit_app.py
  - Windows 上设置 asyncio WindowsProactorEventLoopPolicy，使用 nest_asyncio 以兼容 Streamlit。
  - 侧边栏支持模型选择、文件上传、开启新会话。
  - 消息区支持渲染用户消息、AI 消息、工具调用、工具结果；对于 reasoning 字段（如模型返回的 reasoning/reasoning_content），以代码块或 JSON 展示。
  - 通过 astream(..., stream_mode="messages") 实现消息级流式渲染。

## 🛠️ 扩展与定制

- 添加新工具
  - 在 tools/ 下新建 my_tool.py，定义 @tool；在 graph.py 中将工具加入 self.tools 列表即可。

- 添加/修改模型
  - 在 configs.py 的 ConfigManager.model_configs 中新增条目；
  - 如需支持新 provider（例如 qwen、anthropic 等），请在 models.py 的 get_llm_instance 中添加对应分支逻辑。

- 修改提示词与上下文注入
  - 在 prompts.py 中修改 AGENT_SYSTEM_PROMPT；
  - 注入内容格式由 graph.py 的 _call_model 决定（当前注入 uploaded_file_paths）。

- 扩展 Agent 状态
  - 在 state.py 的 AgentState 中添加自定义字段（如 user_id、domain_context 等），并在工作流节点中读写。

## ⚠️ 已知限制

- 目前 models.py 仅实现 provider=openai 分支；其他 provider 的配置在 UI 可见，但需你在 models.py 中补充实现。
- Tavily 工具需要有效的 TAVILY_API_KEY；未配置时相关功能不可用。
- 某些模型可能不返回 reasoning 字段；UI 会在存在时渲染。

## 🔧 故障排查

- Streamlit 无法启动或事件循环报错（Windows）
  - 已在 streamlit_app.py 中设置 asyncio 策略与 nest_asyncio；请确保使用的 Python 版本与依赖兼容。

- 工具无法调用或返回 401/403
  - 检查 .env 中的 OPENAI_API_KEY、TAVILY_API_KEY 是否有效；如使用自建/代理接口，设置 OPENAI_API_BASE。

- 模型切换无效
  - configs.py 中的条目名必须与 UI 下拉一致；切换后会重置会话并重新初始化工作流。

## 📜 许可证

本模板以开源方式提供，欢迎复制、修改与分发。
