# 🤖 通用 ReAct Agent 模板（LangGraph + Streamlit）

本项目是一个基于 LangGraph 和 Streamlit 的通用 ReAct Agent 模板，提供了一个功能完整、架构清晰的可视化ReAct智能体框架。主要特性包括：

- 🔄 **ReAct（推理-行动）循环**：基于LangGraph的StateGraph实现完整的"思考-规划-行动-观察"工作流
- 🛠️ **工具调用系统**：内置Tavily网页搜索和子Agent工具，支持可插拔扩展
- 📊 **流式响应与过程可视化**：实时展示AI思考过程、工具调用和执行结果
- 🎯 **动态提示词注入**：自动将上传文件信息注入系统提示词，增强上下文感知
- 🔧 **鲁棒重试机制**：智能处理空回复、内容截断等异常情况，确保系统稳定性
- 🔀 **灵活模型配置**：支持多种LLM模型的动态切换和配置管理

本README基于当前代码仓库的实际结构和实现进行了全面更新。

## ✨ 核心特性

### 🏗️ 先进的 ReAct 架构
- 基于 LangGraph 的 StateGraph 构建可视化、可扩展的 Agent 工作流
- 实现完整的"思考-规划-行动-观察"循环，支持复杂任务分解
- 使用 MemorySaver 提供对话状态持久化和会话管理

### 📡 流式响应与过程展示
- 实时渲染AI思考过程、工具调用和执行结果
- 支持可展开的详细信息面板，提升用户体验
- 智能处理思考内容（reasoning）的JSON和文本格式展示

### 🛡️ 健壮的错误处理
- 自动检测和处理空回复、内容截断等异常情况
- 智能重试机制：最多3次重试，避免无限循环
- 支持多种finish_reason处理：length、content_filter、null等

### 🔧 可插拔工具系统
- 内置Tavily网页搜索工具，提供实时信息检索能力
- 子Agent工具框架，支持复杂任务委托和执行
- 工具注册和调用完全自动化，易于扩展新功能

### ⚙️ 灵活的模型配置
- ConfigManager统一管理多种LLM模型配置
- 支持OpenAI兼容接口，易于接入各类模型服务
- UI界面动态切换模型，无需重启应用

### 📁 动态提示词注入
- 自动将上传文件清单注入系统提示词
- 支持文件上下文感知，提升任务处理准确性
- 模板化提示词设计，便于定制和扩展

## 📂 项目结构

本项目采用模块化设计，各组件职责分明，便于理解和扩展：

```
Langgraph-Streamlit-ReAct-Agent/
├── 📁 tools/                  # 工具模块目录
│   ├── __init__.py
│   ├── web_search.py          # Tavily 网页搜索工具
│   └── sub_agent_tool.py      # 子 Agent 执行器
├── 📁 temp_uploads/           # 临时文件上传目录
├── 📄 __init__.py
├── 🔐 .env                    # 环境变量配置文件
├── 📋 .env.example            # 环境变量示例文件
├── ⚙️ configs.py              # ConfigManager：模型配置管理
├── 🤖 models.py               # get_agent_model：LLM工厂函数
├── 💬 prompts.py              # 系统提示词模板
├── 📊 state.py                # AgentState：工作流状态定义
├── 🔄 graph.py                # 工作流核心：StateGraph构建与路由
├── 🖥️ streamlit_app.py        # Streamlit用户界面
├── 📦 requirements.txt        # Python依赖清单
└── 📖 README.md               # 项目文档
```

### 🏗️ 核心架构组件

- **🔄 graph.py**: 工作流引擎，基于LangGraph构建ReAct循环
- **📊 state.py**: 状态管理，定义工作流中的数据结构
- **🤖 models.py**: 模型工厂，负责LLM实例的创建和配置
- **⚙️ configs.py**: 配置管理器，支持多模型动态切换
- **🖥️ streamlit_app.py**: 用户界面，提供交互和可视化能力
- **🛠️ tools/**: 工具集合，提供外部能力扩展接口

## 🚀 快速开始

### 1️⃣ 环境准备

**系统要求**: Python 3.10+ （推荐 3.11）

#### 创建虚拟环境

**Windows (PowerShell)**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS / Linux**
```bash
python -m venv .venv
source .venv/bin/activate
```

### 2️⃣ 安装依赖

```bash
pip install -r requirements.txt
```

**依赖包说明**:
- `langchain` & `langgraph`: 核心Agent框架
- `langchain-openai`: OpenAI模型支持
- `langchain-community` & `langchain-tavily`: 工具扩展
- `streamlit`: Web界面框架
- `python-dotenv`: 环境变量管理

### 3️⃣ 环境配置

在项目根目录创建 `.env` 文件（可参考 `.env.example`）：

```bash
# 必需：OpenAI兼容API配置
OPENAI_API_KEY="sk-..."              # API密钥
OPENAI_API_BASE="https://..."        # API基础URL（可选）
MODEL_NAME="qwen3-coder-30b-a3b-instruct"  # 默认模型名称

# 可选：Tavily搜索工具
TAVILY_API_KEY="tvly-..."            # 在 https://tavily.com/ 免费获取
```

### 4️⃣ 启动应用

```bash
streamlit run streamlit_app.py
```

🎉 **成功！** 浏览器将自动打开应用界面，您可以开始与AI助手对话了。

### 🔍 快速验证

1. **基础对话**: 尝试发送"你好，请介绍一下自己"
2. **工具调用**: 询问"今天的新闻有什么？"（需要Tavily API）
3. **文件上传**: 上传文档并询问相关问题
4. **模型切换**: 在侧边栏切换不同的模型配置

## 🧠 核心架构与实现详解

### 🔄 工作流引擎 (graph.py)

- **AgentWorkflow 类**: 管理整个 Agent 的工作流，包含计算图、LLM 实例和工具集
- **StateGraph 构建**: 包含三个核心节点：`agent`、`tools`、`discard_and_retry`
- **智能路由**: `route_after_llm_call` 函数根据 LLM 响应决定下一步操作
- **动态提示词注入**: 自动将上传文件信息注入系统提示词
- **检查点机制**: 使用 MemorySaver 实现对话状态持久化

### 📊 状态管理 (state.py)

- **AgentState**: 定义工作流中传递的状态结构
- **消息累积**: 使用 `add_messages` 修饰器确保消息逐步积累
- **上下文管理**: 支持文件上传和上下文信息传递
- **错误处理**: 记录 `finish_reason` 和 `retry_count` 用于异常处理

### 🤖 模型工厂 (models.py)

- **get_agent_model()**: 根据配置动态创建 LLM 实例
- **多模型支持**: 当前支持 OpenAI 兼容接口，可扩展其他提供商
- **子Agent模型**: `get_subagent_model()` 为子任务提供独立的模型实例

### ⚙️ 配置管理 (configs.py)

- **ConfigManager**: 集中管理多种 LLM 模型的配置信息
- **动态切换**: 支持在 UI 界面实时切换模型配置
- **环境变量集成**: 安全的 API 密钥管理

### 🛠️ 工具系统 (tools/)

- **web_search.py**: Tavily 网页搜索工具，提供实时信息检索
- **sub_agent_tool.py**: 子 Agent 执行器，支持复杂任务委托
- **可插拔设计**: 易于添加新工具和扩展功能

### 🖥️ 用户界面 (streamlit_app.py)

- **响应式渲染**: 实时显示 AI 思考和执行过程
- **文件上传**: 支持多文件上传和上下文注入
- **模型切换**: 动态模型配置和切换
- **会话管理**: 独立的对话会话和状态管理

## 🛠️ 扩展与定制指南

### 🔧 添加新工具

1. **创建工具文件**：在 `tools/` 目录下创建新工具
2. **注册工具**：在 `graph.py` 的 `self.tools` 列表中添加工具
3. **测试验证**：确保工具可以正常调用和执行

### 🤖 添加新模型

1. **配置模型信息**：在 `configs.py` 中添加模型配置
2. **扩展模型工厂**：在 `models.py` 中支持新的 provider
3. **环境变量**：配置相应的 API 密钥和端点

### 💬 自定义提示词

1. **基础修改**：编辑 `prompts.py` 中的 `AGENT_SYSTEM_PROMPT`
2. **动态注入**：在 `graph.py` 中自定义注入逻辑
3. **上下文管理**：保留占位符以支持文件上下文

### 📊 扩展状态管理

1. **添加字段**：在 `state.py` 的 `AgentState` 中添加自定义字段
2. **读写操作**：在工作流节点中读写新字段
3. **状态管理**：确保状态在节点间正确传递

### 🎨 界面定制

1. **UI 布局**：修改 `streamlit_app.py` 来定制界面
2. **消息渲染**：自定义消息显示格式
3. **交互组件**：添加新的控件和功能

### 🔄 工作流定制

1. **添加节点**：在 `graph.py` 中扩展工作流
2. **路由逻辑**：修改条件路由函数
3. **错误处理**：增强异常情况处理

## ⚠️ 已知限制与注意事项

### 🔧 技术限制

- **模型支持**: 当前 `models.py` 仅实现 `provider=openai` 分支，其他provider的配置需要手动实现
- **工具依赖**: Tavily搜索工具需要有效的 `TAVILY_API_KEY`，未配置时搜索功能不可用
- **推理字段**: 部分模型可能不返回 `reasoning` 字段，UI会在可用时自动渲染
- **文件大小**: 上传文件的大小受Streamlit默认限制（200MB）

### 🎯 使用建议

- **API配额**: 请注意LLM API的调用频率和配额限制
- **网络依赖**: 部分功能需要稳定的网络连接（Tavily搜索、模型API）
- **性能优化**: 大文件上传可能影响响应速度，建议适量使用
- **数据安全**: 上传的文件保存在本地临时目录，请注意敏感信息保护

## 🔧 故障排查

### 🐛 常见问题

#### Streamlit 无法启动或事件循环报错（Windows）
- **原因**: Windows系统上asyncio事件循环兼容性问题
- **解决**: 项目已在 `streamlit_app.py` 中设置相应的asyncio策略
- **备用方案**: 确保使用Python 3.10+版本

#### 工具无法调用或返回 401/403 错误
- **检查API密钥**: 确保 `.env` 中的 `OPENAI_API_KEY`、`TAVILY_API_KEY` 有效
- **检查网络**: 验证API端点的可访问性
- **自建接口**: 如使用自建/代理接口，请设置 `OPENAI_API_BASE`

#### 模型切换无效
- **配置检查**: 确保 `configs.py` 中的条目名与UI下拉一致
- **会话重置**: 切换后会重置会话并重新初始化工作流
- **日志检查**: 查看控制台输出的错误信息

#### 文件上传失败
- **文件格式**: 检查文件格式是否支持
- **文件大小**: 确保文件大小在合理范围内
- **权限检查**: 确保对 `temp_uploads/` 目录有写入权限

### 🔍 调试方法

#### 启用详细日志
```python
# 在 graph.py 中启用LangChain调试
import langchain
langchain.debug = True
```

#### 检查环境变量
```bash
# 检查环境变量是否正确加载
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('OPENAI_API_KEY'))"
```

#### 网络连接测试
```bash
# 测试API连接
curl -H "Authorization: Bearer YOUR_API_KEY" https://api.openai.com/v1/models
```

### 📞 获取帮助

- **问题反馈**: 在GitHub上提交Issue，请包含详细的错误信息和环境配置
- **功能建议**: 欢迎提交Pull Request或Feature Request
- **社区讨论**: 参与项目的Discussions发起讨论

## 📜 许可证

本模板以开源方式提供，欢迎复制、修改与分发。请遵循相应的开源协议和最佳实践。

---

🎉 **希望这个模板能帮助您快速构建自己的ReAct Agent应用！**
