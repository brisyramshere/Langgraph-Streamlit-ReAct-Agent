import os
from langchain_community.tools.tavily_search import TavilySearchResults

# --- Tavily Web Search Tool ---
# 这是一个功能强大的网页搜索工具，由Tavily提供支持。
# Agent可以调用此工具来获取互联网上的实时信息。
#
# 使用前置条件:
# 1. 安装依赖: pip install langchain-tavily
# 2. 设置环境变量:
#    在您的 .env 文件或系统中设置 TAVILY_API_KEY
#    TAVILY_API_KEY="tvly-..."
#
# 您可以在 https://tavily.com/ 免费获取API密钥。
# 实例化工具
# max_results 控制每次搜索返回的结果数量。
tavily_tool = TavilySearchResults(
    max_results=3,
    description="一个可以联网搜索的工具",
    api_key=os.getenv("TAVILY_API_KEY")  # 从环境变量读取API密钥
)


# --- 使用示例 ---
if __name__ == '__main__':
    # 这是一个简单的测试，展示如何直接调用该工具。
    query = "LangGraph是什么？"
    print(f"正在使用Tavily搜索: '{query}'")
    
    try:
        # .invoke() 方法用于执行工具
        results = tavily_tool.invoke({"query": query})
        
        print("\n搜索结果:")
        for res in results:
            print(f"- URL: {res.get('url')}")
            print(f"  标题: {res.get('title')}")
            print(f"  内容片段: {res.get('content')[:100]}...") # 打印前100个字符作为预览
            print("-" * 20)
            
    except Exception as e:
        print(f"\n执行搜索时出错: {e}")
        print("请确保您已经正确安装了 langchain-tavily 并设置了 TAVILY_API_KEY 环境变量。")