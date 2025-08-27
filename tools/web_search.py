import os
from langchain_tavily import TavilySearch  
from dotenv import load_dotenv
load_dotenv()

tavily_api_key = os.getenv("TAVILY_API_KEY")
tavily_tool = TavilySearch(tavily_api_key=tavily_api_key)  

# --- 使用示例 ---
if __name__ == '__main__':
    # 这是一个简单的测试，展示如何直接调用该工具。
    query = "LangGraph是什么？"
    print(f"正在使用Tavily搜索: '{query}'")
    
    try:
        # .invoke() 方法用于执行工具
        results = tavily_tool.invoke({"query": query})
        
        print("\n搜索结果:")
        print(results)
            
    except Exception as e:
        print(f"\n执行搜索时出错: {e}")
        print("请确保您已经正确安装了 langchain-tavily 并设置了 TAVILY_API_KEY 环境变量。")