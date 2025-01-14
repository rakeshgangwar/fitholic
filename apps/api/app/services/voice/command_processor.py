from typing import Dict, Any, List, Tuple
from langgraph.graph import Graph, StateGraph
from langgraph.prebuilt import ToolExecutor, ToolInvocation
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from app.core.config import settings

class CommandProcessor:
    """Process voice commands using LangGraph"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4-1106-preview",
            temperature=0,
            api_key=settings.OPENAI_API_KEY
        )
        self.tools = self._setup_tools()
        self.graph = self._create_graph()
        
    def _setup_tools(self) -> List[Dict[str, Any]]:
        """Setup available tools for the agent"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "log_set",
                    "description": "Log a completed exercise set",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "reps": {
                                "type": "integer",
                                "description": "Number of repetitions completed"
                            },
                            "weight": {
                                "type": "number",
                                "description": "Weight used in pounds"
                            }
                        },
                        "required": ["reps", "weight"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "navigate_exercise",
                    "description": "Navigate to next or previous exercise",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "direction": {
                                "type": "string",
                                "enum": ["next", "previous"],
                                "description": "Direction to navigate"
                            }
                        },
                        "required": ["direction"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "start_rest_timer",
                    "description": "Start a rest timer",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "duration": {
                                "type": "integer",
                                "description": "Rest duration in seconds"
                            }
                        },
                        "required": ["duration"]
                    }
                }
            }
        ]
    
    def _create_graph(self) -> Graph:
        """Create the LangGraph processing pipeline"""
        workflow = StateGraph(Dict)
        
        # Define nodes
        workflow.add_node("parse", self._parse_command)
        workflow.add_node("execute", self._execute_command)
        workflow.add_node("generate_response", self._generate_response)
        
        # Define edges
        workflow.add_edge("parse", "execute")
        workflow.add_edge("execute", "generate_response")
        
        # Set entry and exit points
        workflow.set_entry_point("parse")
        workflow.set_finish_point("generate_response")
        
        return workflow.compile()
    
    def _parse_command(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Parse the transcribed command into structured format"""
        messages = [
            HumanMessage(content=f"""
                Parse the following voice command into a structured format.
                Current exercise: {state.get('current_exercise', 'None')}
                Command: {state['transcription']}
                
                Available commands:
                1. Log a set: "logged X reps at Y pounds"
                2. Navigate: "next exercise" or "previous exercise"
                3. Rest timer: "start rest timer for X seconds"
                
                Return the appropriate function call.
            """)
        ]
        
        response = self.llm.invoke(messages, tools=self.tools)
        tool_calls = response.additional_kwargs.get("tool_calls", [])
        
        if tool_calls:
            state["command"] = {
                "type": tool_calls[0].function.name,
                "parameters": tool_calls[0].function.arguments
            }
        else:
            state["command"] = {
                "type": "help",
                "parameters": {}
            }
        
        return state
    
    def _execute_command(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the parsed command"""
        command = state["command"]
        
        # Here we would actually execute the command
        # For now, we'll just pass it through
        state["execution_result"] = {
            "success": True,
            "command": command
        }
        
        return state
    
    def _generate_response(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a natural language response"""
        messages = [
            HumanMessage(content=f"""
                Generate a natural, encouraging response for the user based on their command and its execution.
                Command: {state['command']}
                Execution result: {state['execution_result']}
                
                Keep the response concise and motivating.
            """)
        ]
        
        response = self.llm.invoke(messages)
        state["response"] = response.content
        
        return state
    
    async def process_command(self, transcription: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process a voice command and return structured response"""
        try:
            initial_state = {
                "transcription": transcription,
                "current_exercise": context.get("current_exercise"),
                "user_id": context.get("user_id"),
                "session_id": context.get("session_id")
            }
            
            result = self.graph.invoke(initial_state)
            
            return {
                "command": result["command"],
                "response_text": result["response"],
                "success": result["execution_result"]["success"]
            }
            
        except Exception as e:
            raise Exception(f"Command processing failed: {str(e)}")
