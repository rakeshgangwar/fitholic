from typing import Dict, Any, TypedDict, Annotated
from langgraph.graph import StateGraph
from app.agents.nodes.workout import WorkoutGeneratorNode

# Define the state type
class WorkoutState(TypedDict):
    user_profile: Dict[str, Any]
    generated_workout: Dict[str, Any]

class WorkoutGenerationWorkflow:
    """Workflow for generating personalized workouts"""
    
    def __init__(self):
        self.workout_generator = WorkoutGeneratorNode()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        # Initialize the graph with state type
        graph = StateGraph(WorkoutState)
        
        # Add nodes
        graph.add_node(self.workout_generator, "generate_workout")
        
        # Set entry and finish points
        graph.set_entry_point("generate_workout")
        graph.set_finish_point("generate_workout")
        
        # Compile the graph
        return graph.compile()
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the workout generation workflow"""
        try:
            result = await self.graph.ainvoke(context)
            return result
        except Exception as e:
            # Add proper error handling and logging
            raise Exception(f"Workflow execution failed: {str(e)}")

# Example usage:
# workflow = WorkoutGenerationWorkflow()
# result = await workflow.execute({
#     "user_profile": {
#         "fitness_goals": ["weight_loss", "muscle_gain"],
#         "fitness_level": "intermediate",
#         "available_equipment": ["dumbbells", "bench"],
#         "preferred_workout_duration": 45
#     }
# }) 