import streamlit as st
import uuid
import json
import time
from pathlib import Path
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from dotenv import load_dotenv

# --- 核心Agent组件 ---
from graph import create_agent_workflow
from configs import ConfigManager

# --- 加载环境变量 ---
load_dotenv()

# --- 页面配置 ---
st.set_page_config(page_title="通用ReAct Agent模板", page_icon="🤖", layout="wide")
st.title("🤖 通用ReAct Agent模板")
st.caption("一个支持流式响应、工具调用和过程可视化的LangGraph+Streamlit框架")

# --- 初始化 ---
if "config_manager" not in st.session_state:
    st.session_state.config_manager = ConfigManager()
config_manager = st.session_state.config_manager

def reset_session():
    """重置会话状态，但保留模型选择。"""
    model_to_keep = st.session_state.get("model_selector")
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    if model_to_keep:
        st.session_state.model_selector = model_to_keep
    st.session_state.config_manager = ConfigManager()
    
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.messages = []
    st.session_state.uploaded_file_paths = []
    st.session_state.agent_runnable = create_agent_workflow(config_manager.get_current_config())

if "session_id" not in st.session_state:
    reset_session()

# --- 渲染函数 ---

def render_tool_call(tool_call):
    """【非流式】渲染单次工具调用，解决缩进问题。"""
    # 直接使用 expander，不再嵌套在 chat_message 中
    with st.expander(f"🔧 工具调用: `{tool_call['name']}`", expanded=True):
        st.json(tool_call['args'])

def render_tool_message(msg):
    """【非流式】渲染单条工具消息。"""
    with st.expander(f"📋 工具结果: `{msg.name}`", expanded=False):
        try:
            st.json(json.loads(msg.content))
        except (json.JSONDecodeError, TypeError):
            st.code(msg.content, language='text')

def render_message_history():
    """【非流式】渲染完整的消息历史。"""
    for msg in st.session_state.messages:
        if isinstance(msg, HumanMessage):
            with st.chat_message("user"):
                st.markdown(msg.content)

        elif isinstance(msg, AIMessage):
            with st.chat_message("assistant"):
                if msg.content:
                    st.markdown(msg.content)
                if msg.tool_calls:
                    for tc in msg.tool_calls:
                        render_tool_call(tc)
        elif isinstance(msg, ToolMessage):
            with st.chat_message("assistant"):
                 render_tool_message(msg)

def process_agent_response(agent_input, config):
    """处理Agent的响应并更新UI。"""
    # 使用同步调用获取完整响应
    # response = st.session_state.agent_runnable.stream(agent_input, config=config, stream_mode = "messages")
    response = st.session_state.agent_runnable.invoke(agent_input, config=config)
    # LangGraph返回的是AgentState对象，直接访问'messages'字段
    if "messages" in response:
        # 获取新增加的消息（排除用户的原始输入）
        existing_msg_count = len(st.session_state.messages)
        new_messages = response["messages"][existing_msg_count:]
        
        for msg in new_messages:
            if isinstance(msg, AIMessage):
                # 思考过程处理
                reasoning = msg.additional_kwargs.get("reasoning") or msg.additional_kwargs.get("reasoning_content")
                if reasoning:
                    with st.chat_message("assistant"):
                        st.markdown("#### 🤔 思考过程")
                        if isinstance(reasoning, (dict, list)):
                            st.json(reasoning)
                        else:
                            st.code(str(reasoning), language='text')

                # 正常答复
                if msg.content:
                    with st.chat_message("assistant"):
                        st.markdown(msg.content, unsafe_allow_html=True)

                # 工具调用
                if msg.tool_calls:
                    for tc in msg.tool_calls:
                        with st.chat_message("assistant"):
                            render_tool_call(tc)

            # 工具消息返回
            elif isinstance(msg, ToolMessage):
                with st.chat_message("assistant"):
                    render_tool_message(msg)

            # 将消息添加到session state中
            if msg not in st.session_state.messages:
                st.session_state.messages.append(msg)

# --- 侧边栏 ---
with st.sidebar:
    # 模型选择区域
    st.header("模型配置")
    available_models_display = config_manager.get_available_models()
    current_model_name = st.session_state.get("model_selector", config_manager.get_current_model_name())
    
    model_index = 0
    if current_model_name in list(available_models_display.keys()):
        model_index = list(available_models_display.keys()).index(current_model_name)

    selected_model_name = st.selectbox(
        "选择一个模型:",
        options=list(available_models_display.keys()),
        format_func=lambda x: available_models_display[x],
        index=model_index,
        key="model_selector"
    )

    if selected_model_name != config_manager.get_current_model_name():
        config_manager.apply_config(selected_model_name)
        st.success(f"模型已切换为: {available_models_display[selected_model_name]}，请开始新的对话。")
        reset_session()
        st.rerun()

    # 文件上传区域
    st.divider()
    st.header("文件上传 (可选)")
    
    upload_dir = Path(f"temp_uploads/{st.session_state.session_id}")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    uploaded_files = st.file_uploader(
        "上传文件，Agent将在下次提问时感知到它们", 
        accept_multiple_files=True,
        key=f"file_uploader_{st.session_state.session_id}"
    )
    
    if uploaded_files:
        current_files = st.session_state.get("uploaded_file_paths", [])
        new_files_added = False
        for uploaded_file in uploaded_files:
            file_path = upload_dir / uploaded_file.name
            if str(file_path) not in current_files:
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                current_files.append(str(file_path))
                new_files_added = True
        
        if new_files_added:
            st.session_state.uploaded_file_paths = current_files
            st.success(f"已成功上传/更新 {len(uploaded_files)} 个文件。")

    if st.session_state.get("uploaded_file_paths"):
        st.write("📋 **已上传文件清单:**")
        for i, file_path in enumerate(st.session_state.uploaded_file_paths):
            st.markdown(f"&nbsp;&nbsp;`{i + 1}. {Path(file_path).name}`")
    
    # 重开对话button
    st.divider()
    if st.button("🔄 新的对话", use_container_width=True):
        reset_session()
        st.rerun()

# 渲染历史消息
render_message_history()

# 接收用户的新输入
if prompt := st.chat_input("请输入您的问题..."):
    st.session_state.messages.append(HumanMessage(content=prompt))
    with st.chat_message("user"):
        st.markdown(prompt)

    agent_input = {
        "messages": [HumanMessage(content=prompt)],
        "uploaded_file_paths": {"uploaded_file_paths": st.session_state.get("uploaded_file_paths", [])}
    }
    config = {"configurable": {"thread_id": st.session_state.session_id}}
    
    # 使用同步方式处理Agent响应
    process_agent_response(agent_input, config)
