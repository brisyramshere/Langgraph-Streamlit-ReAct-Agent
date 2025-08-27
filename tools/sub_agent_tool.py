from langchain_core.tools import tool
from pydantic import BaseModel, Field
from ..models import get_subagent_model

# --- Sub-Agent Executor Tool ---
# "Sub-Agent" (子Agent) 是一种强大的模式，它允许一个主Agent将一个复杂的、
# 需要专门知识的子任务委托给另一个专门的Agent来处理。
#
# 例如:
# - 主Agent是一个通用助手，当遇到"请帮我分析这份财报"的任务时，
#   它可以调用一个专门的"财务分析Sub-Agent"。
# - 主Agent负责与用户交互，当需要执行代码时，
#   它可以调用一个"代码执行Sub-Agent"。
#
# 这个文件提供了一个Sub-Agent工具的框架和占位符。
# 您需要用自己实现的真实Agent或Chain来替换下面的示例逻辑。

class SubAgentInput(BaseModel):
    """定义Sub-Agent工具的输入格式。"""
    sub_task_description: str = Field(description="需要子Agent完成的具体任务描述。")


@tool("sub_agent_executor", args_schema=SubAgentInput)
def sub_agent_executor_tool(sub_task_description: str) -> str:
    """
    调用一个专门的子Agent来处理一个复杂的、独立的子任务。
    当主Agent遇到一个需要深度专业知识或多步推理才能解决的问题时，可以使用此工具。
    例如，可以用它来执行代码、分析复杂文档、或进行多轮的专业领域对话。
    """
    print(f"--- Sub-Agent Tool ---")
    print(f"接收到子任务: {sub_task_description}")

    # 1. 定义你的Sub-Agent (这里用一个简单的LLM Chain作为例子)
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    #
    prompt = ChatPromptTemplate.from_template("你是一个专家，请完成以下任务: {task}")
    llm = get_subagent_model()
    sub_agent_chain = prompt | llm
    response = sub_agent_chain.invoke({"task": sub_task_description})
    result = f"子任务 '{sub_task_description}' 已由Sub-Agent处理完成。处理结果：[{response.content}]"
    
    print(f"Sub-Agent返回结果: {result}")
    return result


# --- 使用示例 ---
if __name__ == '__main__':
    # 这是一个简单的测试，展示如何直接调用该工具。
    task = "请帮我分析一下最近的苹果公司财报，并总结关键亮点。"
    print(f"主Agent准备委派任务: '{task}'")
    
    try:
        # 直接调用工具函数
        output = sub_agent_executor_tool.invoke({"sub_task_description": task})
        
        print("\n工具返回给主Agent的结果:")
        print(output)
        
    except Exception as e:
        print(f"\n调用Sub-Agent工具时出错: {e}")