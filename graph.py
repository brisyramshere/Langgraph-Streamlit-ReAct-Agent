import json
import uuid
from dotenv import load_dotenv
from typing import cast
# --- 加载环境变量 ---
load_dotenv()

from langchain_core.messages import ToolMessage, SystemMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

# --- 模板特定组件 ---
from state import AgentState
from prompts import AGENT_SYSTEM_PROMPT
from configs import ConfigManager
# 模板提供了示例工具，您可以按需导入或替换。
from tools.web_search import tavily_tool
from tools.sub_agent_tool import sub_agent_executor_tool
from models import get_agent_model


# --- 常量定义：增强Agent的鲁棒性 ---
MAX_EMPTY_RETRIES = 3      # 对于模型返回空内容的最多重试次数

def route_after_llm_call(state: AgentState):
    """
    路由函数：在LLM调用后，根据其输出决定下一步走向。
    这是ReAct循环的核心，包含了关键的异常处理逻辑。
    """
    last_message = state["messages"][-1]
    finish_reason = state.get('finish_reason')
    
    print(f"--- 路由 --- 完成原因: '{finish_reason}'")

    # 1. 检查是否为需要续写的可恢复错误（如内容被截断）-->continue_generation
    is_empty_response = isinstance(last_message, AIMessage) and not last_message.tool_calls and not last_message.content
    is_error_finish = finish_reason in ["length", "content_filter", "null"]
            
    # 2. 检查是否为空回复 -->discard_and_retry
    if is_error_finish or is_empty_response:
        retry_count = state.get('retry_count')
        if retry_count < MAX_EMPTY_RETRIES:
            print(f"--- 路由 --- 检测到空回复，将进入重试流程。(第 {retry_count + 1} 次)")
            return "discard_and_retry"
        else:
            print(f">>> 已达到最大空回复重试次数 ({MAX_EMPTY_RETRIES})，流程终止。")
            return END

    # 3. 默认逻辑：若有工具调用，则执行工具；否则，流程结束。
    if last_message.tool_calls:
        return "tools"
    
    return END

class AgentWorkflow:
    """
    管理Agent的工作流，包括计算图、LLM实例和工具集。
    """
    def __init__(self, model_config: dict):
        import langchain
        langchain.debug = True
        self.llm = get_agent_model(model_config)
        
        # --- 工具定义 ---
        self.tools = [
            tavily_tool,
            sub_agent_executor_tool,
        ]
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        self.tool_node = ToolNode(self.tools) # 使用LangGraph预置的ToolNode简化工具执行
        # --- 工具定义结束 ---

        self.graph = self._create_graph()

    def _discard_and_retry(self, state: AgentState):
        """
        丢弃重试节点：处理LLM返回空AIMessage的情况；此节点会移除上一条空消息，并增加重试计数器。
        """
        retry_count = state.get('retry_count', 0) + 1
         
        messages = list(state['messages'])
        messages.pop()# 移除上一条失败的空消息，这是打破无限循环的关键

        return {
            "messages": messages,
            "retry_count": retry_count
        }

    def _create_graph(self) -> StateGraph:
        """
        创建StateGraph计算图，定义所有节点和边，包括异常处理的循环。
        """
        graph_builder = StateGraph(AgentState)
        
        # 注册所有节点
        graph_builder.add_node("agent", self._call_model)
        graph_builder.add_node("tools", self.tool_node)
        graph_builder.add_node("discard_and_retry", self._discard_and_retry)
        
        # 设置入口点
        graph_builder.add_edge(START, "agent")
        
        # 设置核心的条件路由
        graph_builder.add_conditional_edges(
            "agent",
            route_after_llm_call,
            {
                "tools": "tools",
                "discard_and_retry": "discard_and_retry",
                END: END
            }
        )
        
        # 添加常规边，将工具执行和异常处理节点的输出导回Agent节点
        graph_builder.add_edge("tools", "agent")
        graph_builder.add_edge("discard_and_retry", "agent")
        
        # 编译计算图，并设置检查点以实现持久化
        # MemorySaver是简单的内存检查点，适用于开发和测试。
        return graph_builder.compile(checkpointer=MemorySaver())
    
    def _call_model(self, state: AgentState):
        """
        核心Agent节点：调用LLM，并处理动态提示词的注入。
        """
        messages = state["messages"]
            
        # --- 动态提示词注入 ---
        uploaded_file_paths_content = state.get("uploaded_file_paths")
        dynamic_system_prompt = AGENT_SYSTEM_PROMPT.replace(
            "{{uploaded_file_paths}}",
            f"```json\n{json.dumps(uploaded_file_paths_content, indent=2, ensure_ascii=False)}\n```"
        )
        
        current_messages = list(messages)
        if current_messages and current_messages[0].type == "system":
            current_messages[0].content = dynamic_system_prompt
        else:
            current_messages.insert(0, SystemMessage(content=dynamic_system_prompt))
        # --- 动态提示词注入结束 ---

        try:
            # 调用绑定了工具的LLM
            response = cast(AIMessage, self.llm_with_tools.invoke(current_messages))
            finish_reason = response.response_metadata.get("finish_reason", "unknown")
        except Exception as e:
            print(f">>> LLM调用异常: {e}")
            return {
                "messages": [AIMessage(content="LLM调用异常："+str(e))], # 返回异常信息
                "finish_reason": "error"
            }
            
        result = {
            "messages": [response],
            "finish_reason": finish_reason,
        }
            
        return result

# --- 工厂函数，方便在其他模块中创建Agent实例 ---
def create_agent_workflow(model_config: dict) -> StateGraph:
    """
    创建并返回一个新的Agent工作流实例（已编译的计算图）。
    """
    config_with_model_name = model_config.copy()
    if "model" in config_with_model_name:
         config_with_model_name["model_name"] = config_with_model_name.pop("model")

    agent_workflow = AgentWorkflow(model_config=config_with_model_name)
    return agent_workflow.graph

# --- 主程序入口：用于独立测试和调试 ---
if __name__ == "__main__":
    print("正在初始化默认Agent工作流...")
    
    # 使用配置管理器获取默认模型配置
    config_manager = ConfigManager()
    default_config = config_manager.get_current_config()
    
    # 创建可运行的计算图
    runnable = create_agent_workflow(model_config=default_config)
    
    print("默认Agent工作流已创建。")

    # --- 调用示例 ---
    # 使用唯一的线程ID来隔离不同的对话状态
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

