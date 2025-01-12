from typing import Any, Dict, Optional
from langchain_core.language_models import BaseLLM
from app.agents.config import AgentConfig
from app.agents.llm_config import get_llm, LLMConfig

class BaseNode:
    """Base class for all agent nodes"""
    
    def __init__(
        self,
        config: AgentConfig,
        workflow_type: Optional[str] = None,
        llm_config: Optional[LLMConfig] = None,
        llm: Optional[BaseLLM] = None
    ):
        self.config = config
        self.llm = llm or get_llm(workflow_type=workflow_type, config=llm_config)
    
    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process the input context and return updated context"""
        raise NotImplementedError
    
    def __call__(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Make the node callable for LangGraph"""
        return self.process(context) 