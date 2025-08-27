# -*- coding: utf-8 -*-
"""
配置管理模块
用于动态切换不同的 LLM 供应商和模型配置。
这是一个非常灵活的设计，允许您在不修改代码的情况下，通过配置文件轻松管理多个模型。
"""

from typing import Dict, Any
import os

class ConfigManager:
    """
    配置管理类，用于处理和切换不同大模型的配置。
    """

    def __init__(self):
        # 存储所有可用的模型配置。
        # 每个配置都是一个字典，包含了调用模型所需的所有信息。
        #
        # 关键字段说明:
        #   "provider": 供应商标识，用于在 get_llm_instance 工厂函数中决定实例化哪个模型类。
        #   "display_name": 显示名称，用于在UI界面上展示给用户。
        #   "api_key": 对应模型的API密钥。
        #   "base_url": 对应模型的API基础URL。
        #   "thinking": (可选) 一个自定义字段，用于标记该模型是否支持特殊的"思考"或"推理"模式。
        #               您可以在 agent_workflow.py 中读取这个值来执行不同的逻辑。
        self.model_configs = {
            "qwen3-coder-30b-a3b-instruct": {
                "provider": "openai",
                "display_name": "Qwen3-Coder30B",
                "api_key": os.getenv("OPENAI_API_KEY"),  # 从环境变量读取
                "base_url": os.getenv("OPENAI_API_BASE"),
            },
            "qwen-turbo": {
                "provider": "qwen", # 您需要在 agent_workflow.py 的工厂函数中添加对 'qwen' 的支持
                "display_name": "通义千问-Turbo",
                "api_key": os.getenv("OPENAI_API_KEY", "sk-YOUR_QWEN_API_KEY"), # 从环境变量读取
                "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            },
            # --- 您可以在此添加更多模型配置 ---
            # "your-custom-model": {
            #     "provider": "custom_provider",
            #     "display_name": "我的模型",
            #     "api_key": "...",
            #     "base_url": "...",
            # }
        }

        # 当前激活的模型名称，默认为配置列表中的第一个模型。
        self._current_model = list(self.model_configs.keys())[0]

    def get_current_config(self) -> Dict[str, Any]:
        """
        获取当前激活模型的完整配置。
        """
        if self._current_model not in self.model_configs:
            # 如果当前模型无效，则重置为第一个
            self._current_model = list(self.model_configs.keys())[0]

        config = self.model_configs[self._current_model].copy()
        # 为了向后兼容，将模型名称也添加到配置中
        config['model'] = self._current_model
        return config

    def apply_config(self, model_name: str) -> bool:
        """
        根据模型名称切换当前的激活模型。
        
        Args:
            model_name: 要激活的模型的技术名称 (例如 "gpt-4o-mini")。
        
        Returns:
            如果切换成功，返回 True；否则返回 False。
        """
        if model_name not in self.model_configs:
            print(f"配置应用失败: 未知的模型 '{model_name}'")
            return False
        
        self._current_model = model_name
        print(f"模型已切换为: {self.model_configs[model_name]['display_name']}")
        return True

    def get_available_models(self) -> Dict[str, str]:
        """
        获取所有可用模型的字典，格式为 {技术名称: 显示名称}。
        主要用于在UI界面上生成模型选择列表。
        """
        return {k: v['display_name'] for k, v in self.model_configs.items()}

    def get_current_model_name(self) -> str:
        """
        获取当前激活的模型的技术名称。
        """
        return self._current_model