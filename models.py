import os
from langchain_openai import ChatOpenAI
# --- 加载环境变量 ---
from dotenv import load_dotenv
load_dotenv()

def get_agent_model(model_config: dict):
    """
    LLM工厂函数：根据配置动态创建LLM实例。
    这是一个为模板设计的简化版本，您可以轻松扩展以支持更多模型。
    """
    provider = model_config.get("provider", "openai").lower()
    
    # 您可以在此处添加更多供应商，如Anthropic, Google, Qwen等。
    if provider == "openai":
        return ChatOpenAI(
            model=model_config.get("model_name"),
            temperature=model_config.get("temperature", 0.1),
            api_key=model_config.get("api_key"),
            base_url=model_config.get("base_url"),
            streaming=False,
        )
    else:
        raise ValueError(f"不支持的LLM供应商: {provider}")
    
def get_subagent_model():
    return ChatOpenAI(
            model=os.getenv("MODEL_NAME"),
            temperature=0.1,
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_API_BASE"),
            streaming=False,
        )