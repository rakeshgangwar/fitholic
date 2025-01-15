"""
Command Processor Module

This module handles the processing of voice commands for workout logging using LangGraph and LangChain.

Key Components:
1. CommandProcessor: Main class that orchestrates command processing
2. WorkoutState: TypedDict defining the state schema
3. Tool Definitions: Various tools for workout actions (log_set, navigate, etc.)

Flow:
1. Voice command is transcribed to text
2. LLM parses text into structured command
3. Appropriate tool is executed with workout state
4. Response is generated for user

TODO:
1. Add validation for exercise completion conditions (e.g., minimum reps/sets)
2. Implement proper error recovery in LangGraph nodes
3. Add support for compound commands ("log set and start rest timer")
4. Add state persistence between commands
5. Implement proper tool response schema validation
6. Add support for exercise modifications and weight suggestions
7. Implement proper workout template progression
8. Add support for supersets and circuit training
9. Implement voice command history and undo functionality
10. Add proper exercise form instructions in responses
"""

from typing import Dict, Any, List, Tuple, Optional, TypedDict, Annotated, Union
from langgraph.graph import Graph, StateGraph
from langgraph.prebuilt import ToolExecutor, ToolInvocation
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from app.core.config import settings
from datetime import datetime, date
from app.crud.workouts import workout_logs, workout_templates
from app.crud.exercises import exercises as exercise_crud
from app.schemas.workout import WorkoutLogUpdate
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from langchain.tools import Tool, BaseTool, StructuredTool
from pydantic import BaseModel, Field
import json
from app.core.logging import get_logger

logger = get_logger(__name__)

class LogSetInput(BaseModel):
    reps: int = Field(description="Number of repetitions completed")
    weight: float = Field(description="Weight used in pounds")

class NavigateExerciseInput(BaseModel):
    action: str = Field(description="Navigation action to take", enum=["next", "previous", "skip"])

class CompleteSessionInput(BaseModel):
    notes: Optional[str] = Field(default=None, description="Optional notes about the workout")

class RestTimerInput(BaseModel):
    duration: int = Field(description="Rest duration in seconds")

class WorkoutState(TypedDict):
    """State schema for workout commands"""
    user_id: str
    log_id: str
    current_exercise: Optional[Dict[str, Any]]  # Full exercise details
    template: Optional[Dict[str, Any]]  # Full template details
    messages: List[Union[HumanMessage, AIMessage]]
    transcription: str
    command: Dict[str, Any]
    execution_result: Dict[str, Any]
    response: str

class CommandProcessor:
    """Process voice commands using LangGraph"""
    
    def __init__(self):
        logger.info("Initializing CommandProcessor")
        self.llm = ChatOpenAI(
            model="gpt-4-1106-preview",
            temperature=0,
            api_key=settings.OPENAI_API_KEY
        )
        self.tools = [
            StructuredTool.from_function(
                func=self._log_set,
                name="log_set",
                description="Log a completed exercise set",
                args_schema=LogSetInput
            ),
            StructuredTool.from_function(
                func=self._navigate_exercise,
                name="navigate_exercise",
                description="Navigate to next or previous exercise, or skip current exercise",
                args_schema=NavigateExerciseInput
            ),
            StructuredTool.from_function(
                func=self._complete_session,
                name="complete_session",
                description="Complete the current workout session",
                args_schema=CompleteSessionInput
            ),
            StructuredTool.from_function(
                func=self._start_rest_timer,
                name="start_rest_timer",
                description="Start a rest timer",
                args_schema=RestTimerInput
            ),
            Tool.from_function(
                func=self._get_exercise_info,
                name="get_exercise_info",
                description="Get information about current exercise progress"
            ),
            Tool.from_function(
                func=self._help,
                name="help",
                description="Get help about available commands"
            )
        ]
        self.tool_executor = ToolExecutor(self.tools)
        self.graph = self._create_graph()
        logger.info("CommandProcessor initialized successfully")

    def _parse_command(self, state: WorkoutState) -> WorkoutState:
        """Parse voice command and determine intent"""
        logger.debug("Parsing command")
        
        # Build context message
        context = []
        if state["current_exercise"]:
            ex = state["current_exercise"]
            sets_completed = len([s for s in ex['sets'] if s.get('completed', False)])
            total_sets = len(ex['sets'])
            context.append(f"""
Current Exercise:
- Name: {ex['name']}
- Description: {ex['description']}
- Progress: {sets_completed} out of {total_sets} sets completed
- Equipment: {', '.join(ex['equipment'])}
""")
            if ex['instructions']:
                context.append(f"Instructions: {ex['instructions']}")

        if state["template"]:
            template = state["template"]
            completed_exercises = sum(1 for ex in template['exercises'] if ex.get('completed', False))
            total_exercises = len(template['exercises'])
            context.append(f"""
Workout Progress:
- Name: {template['name']}
- Description: {template['description']}
- Progress: {completed_exercises}/{total_exercises} exercises completed
""")

        messages = [
            HumanMessage(content=f"""
Process this voice command: {state['transcription']}

{' '.join(context)}

Available commands:
1. Log a set (e.g., "log 10 reps at 135 pounds")
2. Navigate exercises (e.g., "next exercise", "previous exercise", "skip this exercise")
3. Complete workout (e.g., "finish workout", "end session")
4. Start rest timer (e.g., "start 60 second rest")
5. Get exercise info (e.g., "what's my progress", "how many sets left")
6. Help (e.g., "what can I say", "help")

Determine the user's intent and return the appropriate command.
""")
        ]
        response = self.llm.invoke(messages)
        state["messages"] = messages + [response]
        return state

    def _execute_command(self, state: WorkoutState) -> WorkoutState:
        """Execute the parsed command"""
        logger.debug("Executing command")
        last_message = state["messages"][-1].content
        
        # Parse the tool name and arguments from the LLM response
        try:
            # Expected format: {"tool": "tool_name", "args": {...}}
            tool_call = self.llm.invoke([
                HumanMessage(content=f"""
Based on the command: {last_message}

Return a JSON object with two fields:
1. "tool": The name of the tool to use (one of: log_set, navigate_exercise, complete_session, start_rest_timer, get_exercise_info, help)
2. "args": The arguments for the tool as a dictionary

Example 1: For "log 10 reps at 135 pounds"
{{"tool": "log_set", "args": {{"reps": 10, "weight": 135}}}}

Example 2: For "next exercise"
{{"tool": "navigate_exercise", "args": {{"action": "next"}}}}

Example 3: For "finish workout"
{{"tool": "complete_session", "args": {{"notes": null}}}}

Format your entire response as a valid JSON object.
""")
            ]).content
            
            # Parse the JSON response
            tool_info = json.loads(tool_call)
            
            # Create a ToolInvocation
            tool_invocation = ToolInvocation(
                tool=tool_info["tool"],
                tool_input={**tool_info["args"], "state": state}  # Pass state in tool input
            )
            
            # Execute the tool
            tool_response = self.tool_executor.invoke(tool_invocation)
            state["command"] = {
                "type": tool_info["tool"],
                **tool_info["args"],
                "result": tool_response
            }
            
            return state
            
        except json.JSONDecodeError:
            logger.error(f"Failed to parse LLM response as JSON: {tool_call}")
            state["command"] = {
                "type": "error",
                "error": "Failed to understand command"
            }
            return state
        except KeyError as e:
            logger.error(f"Missing required field in tool info: {e}")
            state["command"] = {
                "type": "error",
                "error": "Invalid command format"
            }
            return state
        except Exception as e:
            logger.exception("Error executing command")
            state["command"] = {
                "type": "error",
                "error": f"Command execution failed: {str(e)}"
            }
            return state

    def _generate_response(self, state: WorkoutState) -> WorkoutState:
        """Generate natural language response"""
        logger.debug("Generating response")
        command = state["command"]
        
        context = []
        if state["current_exercise"]:
            ex = state["current_exercise"]
            context.append(f"Current exercise: {ex['name']}")
            if command["type"] == "log_set":
                context.append(f"Sets completed: {len(ex['sets'])}/{ex['target_sets']}")

        messages = [
            HumanMessage(content=f"""
Command executed: {json.dumps(command)}

{' '.join(context)}

Generate a natural, concise response to the user about what was done.
If there was an error, explain what went wrong and how to fix it.
Keep the response brief and friendly.
""")
        ]
        response = self.llm.invoke(messages)
        state["response"] = response.content
        return state

    async def process_voice_command(
        self,
        transcription: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process a voice command and return structured response"""
        logger.info(f"Processing voice command: {transcription}")
        try:
            # Get exercise and template details
            db = SessionLocal()
            current_exercise = None
            template = None
            
            if context.get("log_id"):
                log = workout_logs.get(db, id=context["log_id"])
                if log and log.exercises:
                    # Find current exercise
                    current_ex = next(
                        (ex for ex in log.exercises if not ex.get("completed", False)),
                        None
                    )
                    if current_ex:
                        # Get full exercise details
                        exercise = exercise_crud.get(db, id=current_ex["exercise_id"])
                        if exercise:
                            current_exercise = {
                                **current_ex,
                                "name": exercise.name,
                                "description": exercise.description,
                                "equipment": exercise.equipment,
                                "instructions": exercise.instructions
                            }
                
                if log.template_id:
                    template_obj = workout_templates.get(db, id=log.template_id)
                    if template_obj:
                        template = {
                            "template_id": str(template_obj.template_id),
                            "name": template_obj.name,
                            "description": template_obj.description,
                            "exercises": log.exercises  # Use exercises from log for progress tracking
                        }

            initial_state: WorkoutState = {
                "transcription": transcription,
                "current_exercise": current_exercise,
                "template": template,
                "user_id": context.get("user_id"),
                "log_id": context.get("log_id"),
                "messages": [],
                "command": {},
                "execution_result": {},
                "response": ""
            }
            
            logger.debug(f"Initial state: {initial_state}")
            
            result = self.graph.invoke(initial_state)
            return {
                "transcription": transcription,
                "response_text": result["response"],
                "response_audio": None,  # TODO: Implement text-to-speech
                "command": result["command"]
            }
        except Exception as e:
            logger.exception("Error processing voice command")
            raise e
        finally:
            db.close()

    def _log_set(self, reps: int, weight: float, state: Dict[str, Any]) -> Dict[str, Any]:
        """Log a completed exercise set"""
        logger.debug(f"Attempting to log set: reps={reps}, weight={weight}")
        try:
            db = SessionLocal()
            state = state["state"]  # Extract state from input
            
            # Get the workout log
            log = workout_logs.get(db, id=state["log_id"])
            if not log:
                logger.error(f"Workout log not found: {state['log_id']}")
                return {"success": False, "error": "Workout log not found"}

            current_exercise = next(
                (ex for ex in log.exercises if ex["exercise_id"] == state["current_exercise"]["exercise_id"]),
                None
            )
            if not current_exercise:
                logger.error(f"Current exercise not found: {state['current_exercise']['exercise_id']}")
                return {"success": False, "error": "Current exercise not found"}

            # Add the set
            current_exercise["sets"].append({
                "weight": weight,
                "reps": reps,
                "completed": True
            })
            
            # Update the workout log
            workout_logs.update(
                db,
                db_obj=log,
                obj_in={"exercises": log.exercises}
            )
            
            return {
                "success": True,
                "sets_completed": len([s for s in current_exercise["sets"] if s.get("completed", False)])
            }
        except Exception as e:
            logger.exception("Error logging set")
            return {"success": False, "error": str(e)}
        finally:
            db.close()

    def _navigate_exercise(self, action: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """Navigate to next/previous exercise or skip current exercise"""
        logger.debug(f"Navigating exercise: action={action}")
        try:
            db = SessionLocal()
            state = state["state"]  # Extract state from input
            
            # Get the workout log
            log = workout_logs.get(db, id=state["log_id"])
            if not log:
                logger.error(f"Workout log not found: {state['log_id']}")
                return {"success": False, "error": "Workout log not found"}

            current_idx = next(
                (i for i, ex in enumerate(log.exercises) if not ex.get("completed", False)),
                -1
            )
            
            if action == "next" and current_idx < len(log.exercises) - 1:
                if current_idx >= 0:
                    log.exercises[current_idx]["completed"] = True
            elif action == "previous" and current_idx > 0:
                log.exercises[current_idx - 1]["completed"] = False
            elif action == "skip" and current_idx < len(log.exercises) - 1:
                if current_idx >= 0:
                    log.exercises[current_idx]["completed"] = True
            
            # Update the workout log
            workout_logs.update(
                db,
                db_obj=log,
                obj_in={"exercises": log.exercises}
            )
            
            # Get the next exercise details
            next_idx = next(
                (i for i, ex in enumerate(log.exercises) if not ex.get("completed", False)),
                -1
            )
            next_exercise = None
            if next_idx >= 0:
                exercise = exercise_crud.get(db, id=log.exercises[next_idx]["exercise_id"])
                if exercise:
                    next_exercise = {
                        "name": exercise.name,
                        "description": exercise.description,
                        "sets_completed": len([s for s in log.exercises[next_idx]["sets"] if s.get("completed", False)]),
                        "total_sets": len(log.exercises[next_idx]["sets"])
                    }
            
            return {
                "success": True,
                "next_exercise": next_exercise
            }
        except Exception as e:
            logger.exception("Error navigating exercise")
            return {"success": False, "error": str(e)}
        finally:
            db.close()

    def _complete_session(self, notes: Optional[str], state: Dict[str, Any]) -> Dict[str, Any]:
        """Complete the workout session"""
        logger.debug("Completing workout session")
        try:
            db = SessionLocal()
            state = state["state"]  # Extract state from input
            
            # Get the workout log
            log = workout_logs.get(db, id=state["log_id"])
            if not log:
                logger.error(f"Workout log not found: {state['log_id']}")
                return {"success": False, "error": "Workout log not found"}
            
            # Update the workout log
            workout_logs.update(
                db,
                db_obj=log,
                obj_in={
                    "status": "completed",
                    "end_time": datetime.now(),
                    "notes": notes if notes else ""
                }
            )
            
            return {
                "success": True,
                "completed_exercises": sum(1 for ex in log.exercises if ex.get("completed", False)),
                "total_exercises": len(log.exercises)
            }
        except Exception as e:
            logger.exception("Error completing session")
            return {"success": False, "error": str(e)}
        finally:
            db.close()

    def _start_rest_timer(self, duration: int, state: Dict[str, Any] = None) -> Dict[str, Any]:
        """Start a rest timer"""
        logger.debug(f"Starting rest timer for {duration} seconds")
        return {
            "success": True,
            "duration": duration,
            "message": f"Started {duration} second rest timer"
        }

    def _get_exercise_info(self, state: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get information about the current exercise"""
        logger.debug("Getting exercise info")
        if not state:
            logger.error("No state provided for get_exercise_info")
            return {"success": False, "error": "No state provided"}
            
        try:
            db = SessionLocal()
            log = workout_logs.get(db, id=state["log_id"])
            if not log:
                logger.error(f"Workout log not found for id: {state['log_id']}")
                return {"success": False, "error": "Workout log not found"}

            current_exercise = next(
                (ex for ex in log.exercises if ex["exercise_id"] == state["current_exercise"]["exercise_id"]),
                None
            )
            if not current_exercise:
                logger.error(f"Current exercise not found: {state['current_exercise']['exercise_id']}")
                return {"success": False, "error": "Current exercise not found"}

            completed_sets = len([s for s in current_exercise["sets"] if s["completed"]])
            total_sets = len(current_exercise["sets"])

            logger.info(f"Exercise info - completed sets: {completed_sets}, total sets: {total_sets}")
            return {
                "success": True,
                "completed_sets": completed_sets,
                "total_sets": total_sets,
                "remaining_sets": total_sets - completed_sets
            }
        except Exception as e:
            logger.exception("Error getting exercise info")
            return {"success": False, "error": str(e)}
        finally:
            db.close()

    def _help(self, state: Dict[str, Any] = None) -> Dict[str, Any]:
        """Provide help information about available commands"""
        logger.debug("Providing help information")
        return {
            "success": True,
            "message": """Available commands:
1. Log a set: "logged X reps at Y pounds"
2. Navigate: "next exercise", "previous exercise", "skip this exercise"
3. Rest timer: "start rest timer for X seconds"
4. Complete workout: "finish workout", "end session"
5. Exercise info: "how many sets left", "show progress"
"""
        }

    def _get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Get JSON schemas for tools"""
        logger.debug("Getting tool schemas")
        return [
            {
                "type": "function",
                "function": {
                    "name": "log_set",
                    "description": "Log a completed exercise set",
                    "parameters": LogSetInput.model_json_schema()
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "navigate_exercise",
                    "description": "Navigate to next or previous exercise, or skip current exercise",
                    "parameters": NavigateExerciseInput.model_json_schema()
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "complete_session",
                    "description": "Complete the current workout session",
                    "parameters": CompleteSessionInput.model_json_schema()
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "start_rest_timer",
                    "description": "Start a rest timer",
                    "parameters": RestTimerInput.model_json_schema()
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_exercise_info",
                    "description": "Get information about current exercise progress",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "help",
                    "description": "Get help about available commands",
                    "parameters": {"type": "object", "properties": {}}
                }
            }
        ]

    def _create_graph(self) -> Graph:
        """Create the LangGraph processing pipeline"""
        logger.debug("Creating command processing graph")
        workflow = StateGraph(WorkoutState)
        
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
        
        logger.info("Command processing graph created successfully")
        return workflow.compile()
