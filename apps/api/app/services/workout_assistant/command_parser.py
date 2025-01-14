from typing import Dict, Any
import re
from app.agents.llm_config import get_llm

class CommandParser:
    """Parse and understand workout-related commands"""
    
    def __init__(self):
        self.llm = get_llm("workout_voice")
        self._init_command_patterns()
        
    def _init_command_patterns(self):
        """Initialize regex patterns for command recognition"""
        self.patterns = {
            "log_set": r"(?i)(?:logged?|did|completed?)\s+(\d+)\s*(?:reps?|repetitions?)\s+(?:at|with|using)?\s*(\d+)\s*(?:lbs?|pounds?)",
            "next_exercise": r"(?i)(?:next|forward|continue|move on)",
            "previous_exercise": r"(?i)(?:previous|back|return)",
            "start_rest": r"(?i)(?:start|begin|set)\s+(?:a\s+)?(?:rest|break|timer)\s+(?:for\s+)?(\d+)\s*(?:seconds?|secs?)?",
            "form_check": r"(?i)(?:how|what|check|verify).*(?:form|technique|posture)",
        }
        
    async def parse_command(
        self,
        text: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Parse command from text using regex and LLM"""
        # Try regex patterns first for common commands
        command = self._parse_with_regex(text)
        if command:
            return command
            
        # Fall back to LLM for more complex commands
        return await self._parse_with_llm(text, context)
    
    def _parse_with_regex(self, text: str) -> Dict[str, Any]:
        """Parse command using regex patterns"""
        # Check for set logging
        set_match = re.match(self.patterns["log_set"], text)
        if set_match:
            return {
                "type": "log_set",
                "reps": int(set_match.group(1)),
                "weight": int(set_match.group(2))
            }
            
        # Check for navigation commands
        if re.match(self.patterns["next_exercise"], text):
            return {
                "type": "navigation",
                "action": "next"
            }
        if re.match(self.patterns["previous_exercise"], text):
            return {
                "type": "navigation",
                "action": "previous"
            }
            
        # Check for rest timer
        rest_match = re.match(self.patterns["start_rest"], text)
        if rest_match:
            return {
                "type": "rest_timer",
                "duration": int(rest_match.group(1))
            }
            
        # Check for form guidance
        if re.match(self.patterns["form_check"], text):
            return {
                "type": "form_guidance"
            }
            
        return None
        
    async def _parse_with_llm(
        self,
        text: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Parse complex commands using LLM"""
        prompt = self._create_parsing_prompt(text, context)
        
        try:
            response = await self.llm.ainvoke(prompt)
            # Parse LLM response into command structure
            # This is a simplified version - would need proper response parsing
            return {
                "type": "custom",
                "text": text,
                "parsed_intent": response
            }
        except Exception as e:
            raise Exception(f"LLM parsing failed: {str(e)}")
    
    def _create_parsing_prompt(
        self,
        text: str,
        context: Dict[str, Any]
    ) -> str:
        """Create prompt for LLM command parsing"""
        current_exercise = context.get("current_exercise", {})
        
        return f"""
        Context: User is doing a workout.
        Current exercise: {current_exercise.get('name')}
        Target: {current_exercise.get('sets')} sets of {current_exercise.get('reps')} reps
        
        User command: "{text}"
        
        Parse this command and identify:
        1. The primary intent
        2. Any relevant numbers (sets, reps, weights)
        3. Any specific exercise references
        4. Any timing/duration references
        
        Respond in a structured format that can be parsed as a command.
        """
