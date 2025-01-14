from typing import Dict, Any, TypedDict, List, Optional
from datetime import datetime
from langgraph.graph import StateGraph
from sqlalchemy.orm import Session
from app.agents.nodes.chat.message_parser import MessageParserNode
from app.agents.nodes.chat.exercise_creator import ExerciseCreatorNode
from app.agents.nodes.chat.workout_generator import WorkoutGeneratorNode
from app.agents.nodes.chat.motivation import MotivationNode
from app.agents.nodes.base import BaseNode
from app.core.logging import get_logger

logger = get_logger(__name__)

class ChatState(TypedDict):
    """Type definition for chat state"""
    session_id: str
    user_id: str
    user_profile: Dict[str, Any]
    chat_history: List[Dict[str, str]]
    current_message: str
    current_intent: Optional[Dict[str, Any]]
    current_state: str
    next_question: Optional[str]
    response: Optional[str]
    error: Optional[str]

class EndNode(BaseNode):
    """Node for handling the end of conversation"""
    
    def __init__(self):
        super().__init__(config=None, workflow_type="chat")
    
    async def process(self, state: ChatState) -> Dict[str, Any]:
        """Process the end of conversation"""
        # If no response is set, provide a default one
        if not state.get("response"):
            state["response"] = "Is there anything else I can help you with?"
        return state

class RouterNode(BaseNode):
    """Node for routing messages based on intent"""
    
    def __init__(self):
        super().__init__(config=None, workflow_type="chat")
    
    async def process(self, state: ChatState) -> Dict[str, Any]:
        """Route to appropriate node based on intent"""
        result = {}
        current_state = state.get("current_state", "unknown")
        logger.info(f"RouterNode - Processing state: {current_state}")
        
        # For new messages, we should always go to parse_message first
        if state.get("current_state") == "new_message":
            result["next"] = "parse_message"
            logger.info("RouterNode - New message, routing to parser")
            return result
        
        # After parsing, check confidence threshold and intent
        if state.get("current_state") == "intent_parsed":
            intent = state.get("current_intent", {})
            intent_type = intent.get("type")
            confidence = intent.get("confidence", 0)
            
            logger.info(f"RouterNode - Parsed intent - Type: {intent_type}, Confidence: {confidence}")
            
            if confidence < 0.7 or intent_type == "unknown":
                # For low confidence or unknown intents, use motivation node
                result["next"] = "motivate"
                logger.info("RouterNode - Low confidence/unknown intent, routing to motivation")
            else:
                result["next"] = {
                    "create_exercise": "create_exercise",
                    "generate_workout": "generate_workout"
                }.get(intent_type, "motivate")  # Default to motivation for unhandled intents
                logger.info(f"RouterNode - Known intent, routing to: {result['next']}")
            return result
        
        # After motivation, end the conversation
        if state.get("current_state") == "motivated":
            result["next"] = "end"
            logger.info("RouterNode - Motivation complete, ending conversation")
            return result
            
        # For gathering requirements, route back to the appropriate node
        if state.get("current_state") == "gathering_requirements":
            intent_type = state.get("current_intent", {}).get("type")
            if intent_type:
                result["next"] = {
                    "create_exercise": "create_exercise",
                    "generate_workout": "generate_workout"
                }.get(intent_type)
                if result["next"]:
                    logger.info(f"RouterNode - Continuing requirements gathering for: {intent_type}")
                    return result
            
            # If we don't have a valid intent type, end the conversation
            result["next"] = "end"
            logger.info("RouterNode - No valid intent for requirements gathering, ending conversation")
            return result
        
        # Default to end if we don't recognize the state
        result["next"] = "end"
        logger.info(f"RouterNode - Unrecognized state: {current_state}, ending conversation")
        return result

class FitnessChatWorkflow:
    """Main workflow for fitness chatbot"""
    
    def __init__(self, db: Session):
        self.db = db
        
        # Initialize nodes
        self.parser = MessageParserNode()
        self.router = RouterNode()
        self.exercise_creator = ExerciseCreatorNode()
        self.workout_generator = WorkoutGeneratorNode(db)
        self.motivation = MotivationNode()
        self.end_node = EndNode()
        
        # Build the workflow graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        # Initialize graph with state type
        graph = StateGraph(ChatState)
        
        # Add nodes
        graph.add_node("parse_message", self.parser)
        graph.add_node("route_intent", self.router)
        graph.add_node("create_exercise", self.exercise_creator)
        graph.add_node("generate_workout", self.workout_generator)
        graph.add_node("motivate", self.motivation)
        graph.add_node("end", self.end_node)
        
        # Add edges
        graph.add_edge("parse_message", "route_intent")
        
        # Add conditional edges for routing based on intent
        graph.add_conditional_edges(
            "route_intent",
            lambda x: x["next"],
            {
                "parse_message": "parse_message",
                "create_exercise": "create_exercise",
                "generate_workout": "generate_workout",
                "motivate": "motivate",
                "end": "end"
            }
        )
        
        # Add conditional edges for exercise creation flow
        graph.add_conditional_edges(
            "create_exercise",
            lambda x: (
                "end" if x.get("current_state") == "exercise_created"
                else "end" if x.get("current_state") == "error"
                else "end" if x.get("current_state") == "gathering_requirements" and x.get("response")
                else "route_intent"
            ),
            {
                "route_intent": "route_intent",
                "end": "end"
            }
        )
        
        # Add conditional edges for workout generation flow
        graph.add_conditional_edges(
            "generate_workout",
            lambda x: (
                "end" if x.get("current_state") == "workout_generated"
                else "end" if x.get("current_state") == "error"
                else "end" if x.get("current_state") == "gathering_requirements" and x.get("response")
                else "route_intent"
            ),
            {
                "route_intent": "route_intent",
                "end": "end"
            }
        )
        
        # Add edge from motivation to end
        graph.add_edge("motivate", "end")
        
        # Set entry point
        graph.set_entry_point("route_intent")
        
        return graph.compile()
    
    async def process_message(
        self,
        session_id: str,
        user_id: str,
        message: str,
        chat_history: List[Dict[str, str]],
        user_profile: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process a single message in the conversation"""
        try:
            # Initialize state
            state = ChatState(
                session_id=session_id,
                user_id=user_id,
                user_profile=user_profile or {},
                chat_history=chat_history,
                current_message=message,
                current_intent=None,
                current_state="new_message",
                next_question=None,
                response=None,
                error=None
            )
            
            # Process through graph
            result = await self.graph.ainvoke(state)
            
            # Prepare response
            now = datetime.utcnow()
            response = {
                "session_id": session_id,
                "response": result.get("response", "I'm not sure how to help with that."),
                "current_state": result.get("current_state", "unknown"),
                "error": result.get("error"),
                "created_at": now
            }
            
            # Add any generated content
            if "created_exercise" in result:
                response["created_exercise"] = result["created_exercise"]
            if "generated_workout" in result:
                response["generated_workout"] = result["generated_workout"]
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            now = datetime.utcnow()
            return {
                "session_id": session_id,
                "response": "I encountered an error processing your request. Please try again.",
                "current_state": "error",
                "error": str(e),
                "created_at": now
            } 