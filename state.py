from typing import List, TypedDict, Annotated, Any
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """
    定义Agent在工作流中传递的状态。
    这是一个高度可定制的结构，您可以根据需求添加、修改或删除字段。

    Attributes:
        messages: 对话消息列表。
                  使用 `Annotated` 和 `add_messages` 来确保新消息总是被追加而不是覆盖，
                  这是LangGraph中管理对话历史的标准做法。
        
        scratchpad: 一个通用的“便笺”或“草稿纸”字段，用于存储临时的、
                    非结构化的数据或Agent在思考过程中产生的中间结果。
                    您可以在工具或节点中读写这个字段，以实现更复杂的逻辑。
                    例如，一个工具可以将分析结果存入scratchpad，
                    以便下一个节点或LLM可以访问。

        finish_reason: 上一次LLM调用的finish_reason，用于路由决策，是实现鲁棒性的关键。
        
        retry_count: 用于追踪discard_and_retry节点连续调用次数的计数器。
    """
    messages: Annotated[List[BaseMessage], add_messages]
    
    # 您可以在这里添加更多自定义的状态字段
    # 例如: user_id: str, session_id: str, etc.
    uploaded_file_paths: Any

    # --- 以下是用于增强鲁棒性的内部状态，建议保留 ---
    finish_reason: str
    retry_count: int