from typing import Dict, Any
from langgraph.graph import Graph, StateGraph
from app.agents.nodes.workout import WorkoutGeneratorNode

class WorkoutGenerationWorkflow:
    """Workflow for generating personalized workouts"""
    
    def __init__(self):
        self.workout_generator = WorkoutGeneratorNode()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        # Initialize the graph
        graph = StateGraph(nodes=["generate_workout"])
        
        # Add nodes
        graph.add_node("generate_workout", self.workout_generator)
        
        # Define the end condition
        def end_condition(state: Dict[str, Any]) -> bool:
            """Check if workflow should end"""
            return "generated_workout" in state
        
        # Set the end condition
        graph.set_end_condition(end_condition)
        
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