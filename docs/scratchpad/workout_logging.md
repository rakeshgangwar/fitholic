## Workout Logging System Documentation

### Current Implementation
- Basic workout management system with templates
- Manual logging of sets, reps, and weights
- Basic workout summary and history viewing
- Template-based workout creation

### Identified Challenge
The current manual workout logging process is cumbersome and disruptive to the workout flow:
- Users need to input data between sets
- Disrupts rest periods
- Takes focus away from the workout
- Can lead to incomplete or inaccurate logging

### Proposed Solution: Voice-Based Workout Assistant

#### 1. Voice Interface
- Natural conversation with AI trainer
- Hands-free logging during workouts
- Context-aware exercise tracking
- Smart rest period management
- Real-time form guidance and encouragement

#### 2. Calendar Integration
- Schedule workouts in advance
- Track workout adherence
- View workout history in calendar format
- Set recurring workout schedules
- Get reminders for upcoming workouts

#### 3. Enhanced Template System
- Detailed workout templates
- Support for different workout types (strength, cardio, HIIT)
- Scheduling preferences
- Estimated duration tracking
- Difficulty levels and progression tracking

#### 4. Smart Workout Assistant Features
- Real-time encouragement and motivation
- Intelligent weight adjustment suggestions
- Automated rest period tracking
- Form reminders and technique tips
- Natural language processing for various input formats
- Performance tracking and progress insights

### Technical Architecture - Voice Assistant Implementation

#### 1. Directory Structure
```
# apps/api/app/services/voice/
├── tts_service.py          # ElevenLabs TTS integration
├── stt_service.py          # Whisper STT integration
└── voice_processor.py      # Voice command processing and routing

# apps/api/app/services/workout_assistant/
├── command_parser.py       # NLP for workout commands
├── session_manager.py      # Manage workout sessions
└── response_generator.py   # Generate contextual responses

# apps/api/app/agents/workflows/voice/
├── workout_voice_workflow.py  # Voice-based workout workflow
└── prompts/
    ├── command_recognition.py # Prompts for command understanding
    └── response_generation.py # Prompts for assistant responses
```

#### 2. Core Components

##### Voice Services
```python
class TTSService:
    """ElevenLabs text-to-speech service"""
    def synthesize_speech(self, text: str, voice_id: str) -> bytes:
        # Convert assistant responses to speech
        pass

class STTService:
    """Whisper speech-to-text service"""
    def transcribe_audio(self, audio_data: bytes) -> str:
        # Convert user's voice to text
        pass

class VoiceProcessor:
    """Process voice commands and manage voice interactions"""
    def __init__(self):
        self.tts = TTSService()
        self.stt = STTService()
        self.command_parser = CommandParser()
    
    async def process_voice_command(
        self, 
        audio_data: bytes, 
        session_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        # Process voice commands and return responses
        pass
```

##### Workout Assistant Core
```python
class CommandParser:
    """Parse and understand workout-related commands"""
    def parse_command(self, text: str) -> Dict[str, Any]:
        # Classify command type and extract relevant information
        # e.g., "logged 10 reps at 100 pounds" ->
        # {"type": "log_set", "reps": 10, "weight": 100}
        pass

class WorkoutSessionManager:
    """Manage active workout sessions"""
    def __init__(self):
        self.active_sessions: Dict[str, WorkoutSession] = {}
    
    def get_or_create_session(self, user_id: str) -> WorkoutSession:
        # Manage workout session state
        pass
```

##### Voice Workflow
```python
class WorkoutVoiceWorkflow(BaseWorkflow):
    """Handle voice-based workout interactions"""
    def __init__(self):
        self.voice_processor = VoiceProcessor()
        self.session_manager = WorkoutSessionManager()
        self.llm = get_llm("workout_voice")
    
    async def process_voice_command(
        self,
        audio_data: bytes,
        user_id: str,
        session_id: str
    ) -> Dict[str, Any]:
        # Process voice commands and generate responses
        pass
```

##### Frontend Integration
```typescript
// apps/web/src/lib/services/voice.ts
class WorkoutVoiceService {
  private mediaRecorder: MediaRecorder | null = null;
  private isListening = false;

  async startListening(): Promise<void> {
    // Initialize voice recording
  }

  async stopListening(): Promise<void> {
    // Stop recording and process command
  }

  private async processAudioChunk(chunk: Blob): Promise<void> {
    // Send audio to backend and handle response
  }
}
```

#### 3. Key Features

1. **Command Recognition**
   - Start/end workout
   - Log sets/reps/weights
   - Navigate exercises
   - Request rest timer
   - Ask for form guidance

2. **Context-Aware Responses**
   - Maintains workout session state
   - Remembers previous sets/weights
   - Understands exercise context
   - Provides relevant feedback

3. **Voice Interaction Flow**
```
User Voice Input -> Whisper STT -> Command Parser -> 
Workout Session Manager -> Response Generator -> 
ElevenLabs TTS -> Audio Response
```

### Frontend Architecture

#### 1. Directory Structure
```
# apps/web/src/
├── lib/
│   ├── components/
│   │   ├── workouts/
│   │   │   ├── VoiceWorkoutLogger.svelte    # Voice-enabled workout logging
│   │   │   ├── VoiceControls.svelte         # Voice control UI
│   │   │   └── WorkoutAssistant.svelte      # AI assistant interface
│   │   └── voice/
│   │       ├── VoiceRecorder.svelte         # Voice recording component
│   │       └── VoicePlayback.svelte         # TTS playback component
│   └── services/
│       └── voice.ts                         # Voice interaction service
└── routes/
    └── dashboard/
        └── workouts/
            ├── +page.svelte                 # Main workout page
            ├── voice/
            │   └── +page.svelte             # Voice assistant mode
            └── [id]/
                └── +page.svelte             # Workout detail page
```

#### 2. Screen Designs

##### Main Workout Page (`/workouts`)
```svelte
<Tabs defaultValue="sessions">
  <TabsList>
    <TabsTrigger value="sessions">Templates</TabsTrigger>
    <TabsTrigger value="log">Log Workout</TabsTrigger>
    <TabsTrigger value="voice">Voice Assistant</TabsTrigger>
    <TabsTrigger value="history">History</TabsTrigger>
  </TabsList>

  <!-- Existing Template and History tabs -->
  
  <!-- New Voice Assistant Tab -->
  <TabsContent value="voice">
    <WorkoutAssistant />
  </TabsContent>
</Tabs>
```

##### Voice Assistant Mode (`/workouts/voice`)
```svelte
<script lang="ts">
  import VoiceWorkoutLogger from '$lib/components/workouts/VoiceWorkoutLogger.svelte';
  import VoiceControls from '$lib/components/workouts/VoiceControls.svelte';
  import { WorkoutVoiceService } from '$lib/services/voice';
  
  const voiceService = new WorkoutVoiceService();
</script>

<div class="voice-workout-container">
  <!-- Current Exercise Display -->
  <section class="exercise-display">
    <h2>{currentExercise.name}</h2>
    <div class="exercise-details">
      <span>Target: {currentExercise.sets}x{currentExercise.reps}</span>
      <span>Rest: {currentExercise.rest}s</span>
    </div>
  </section>

  <!-- Voice Controls -->
  <VoiceControls
    on:startListening={voiceService.startListening}
    on:stopListening={voiceService.stopListening}
  />

  <!-- Assistant Feedback Display -->
  <section class="assistant-feedback">
    <div class="transcription">{lastCommand}</div>
    <div class="response">{assistantResponse}</div>
  </section>

  <!-- Exercise Progress -->
  <section class="progress-tracker">
    <div class="sets-progress">
      {completedSets} / {totalSets} sets
    </div>
    <div class="rest-timer" class:active={isResting}>
      {restTimeRemaining}s
    </div>
  </section>
</div>
```

##### Voice Controls Component
```svelte
<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { Button } from '$lib/components/ui/button';
  
  const dispatch = createEventDispatcher();
  let isListening = false;
</script>

<div class="voice-controls">
  <Button
    variant={isListening ? 'destructive' : 'primary'}
    on:click={() => {
      isListening = !isListening;
      dispatch(isListening ? 'startListening' : 'stopListening');
    }}
  >
    {isListening ? 'Stop Listening' : 'Start Voice Assistant'}
  </Button>
  
  <div class="voice-status">
    {#if isListening}
      <span class="pulse-dot"></span>
      Listening...
    {/if}
  </div>
</div>
```

#### 3. Key UI/UX Features

1. **Voice Control Status**
   - Clear visual indicators for voice activation
   - Microphone status and audio levels
   - Transcription feedback
   - Assistant response display

2. **Workout Progress**
   - Current exercise details
   - Set/rep counting
   - Rest timer visualization
   - Overall workout progress

3. **Assistant Feedback**
   - Real-time form guidance
   - Exercise transitions
   - Motivation messages
   - Performance stats

4. **Accessibility**
   - Visual feedback for voice commands
   - Alternative input methods
   - Clear error states
   - Haptic feedback support

### Benefits
1. **Improved User Experience**
   - Less disruption during workouts
   - More natural interaction
   - Better focus on exercise execution

2. **Better Data Quality**
   - More consistent logging
   - Real-time validation
   - Comprehensive workout tracking

3. **Enhanced Motivation**
   - Personal trainer-like experience
   - Immediate feedback and encouragement
   - Progress visualization

4. **Flexible Usage**
   - Works for different workout styles
   - Adapts to user preferences
   - Supports various fitness levels