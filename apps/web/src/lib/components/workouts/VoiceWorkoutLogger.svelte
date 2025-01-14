<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import type { WorkoutTemplate } from '$lib/types';
  import { WorkoutVoiceService } from '$lib/services/voice';
  import VoiceControls from './VoiceControls.svelte';
  import { Card, CardContent, CardHeader, CardTitle } from "$lib/components/ui/card";
  import { Progress } from "$lib/components/ui/progress";
  import { Alert, AlertDescription } from "$lib/components/ui/alert";
  
  export let template: WorkoutTemplate | null = null;
  
  let voiceService: WorkoutVoiceService;
  let isListening = false;
  let error: string | null = null;
  let currentExerciseIndex = 0;
  let lastCommand = '';
  let assistantResponse = '';
  let completedSets = 0;
  let isResting = false;
  let restTimeRemaining = 0;
  let restTimer: number;
  
  $: currentExercise = template?.exercises?.[currentExerciseIndex];
  $: totalSets = currentExercise?.sets || 0;
  $: progress = template ? ((currentExerciseIndex + 1) / (template.exercises?.length || 1)) * 100 : 0;
  
  onMount(() => {
    initializeVoiceService();
  });
  
  onDestroy(() => {
    if (restTimer) {
      clearInterval(restTimer);
    }
  });
  
  async function initializeVoiceService() {
    try {
      voiceService = new WorkoutVoiceService();
    } catch (e) {
      error = 'Failed to initialize voice assistant';
      console.error(e);
    }
  }
  
  function handleStartListening() {
    try {
      voiceService.startListening();
      isListening = true;
      error = null;
    } catch (e) {
      error = 'Failed to start listening';
      console.error(e);
    }
  }
  
  function handleStopListening() {
    try {
      voiceService.stopListening();
      isListening = false;
    } catch (e) {
      error = 'Failed to stop listening';
      console.error(e);
    }
  }
  
  function startRestTimer(duration: number) {
    isResting = true;
    restTimeRemaining = duration;
    
    if (restTimer) {
      clearInterval(restTimer);
    }
    
    restTimer = setInterval(() => {
      if (restTimeRemaining > 0) {
        restTimeRemaining--;
      } else {
        clearInterval(restTimer);
        isResting = false;
      }
    }, 1000);
  }
</script>

<div class="voice-workout-container space-y-6">
  {#if !template}
    <Card>
      <CardContent class="flex flex-col items-center justify-center py-12">
        <svg
          class="w-12 h-12 text-muted-foreground mb-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z M19 10v2a7 7 0 0 1-14 0v-2"
          />
        </svg>
        <h3 class="text-lg font-semibold mb-2">No Workout Selected</h3>
        <p class="text-muted-foreground text-center">
          Please select a workout template from the Templates tab to start voice-assisted training.
        </p>
      </CardContent>
    </Card>
  {:else}
    <Card>
      <CardHeader>
        <CardTitle>{template.name}</CardTitle>
        <div class="text-sm text-muted-foreground">
          Exercise {currentExerciseIndex + 1} of {template.exercises?.length || 0}
        </div>
      </CardHeader>
      
      <CardContent class="space-y-6">
        {#if error}
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        {/if}
        
        <!-- Current Exercise Display -->
        <section class="exercise-display">
          <h3 class="text-lg font-semibold">{currentExercise?.name || 'No exercise'}</h3>
          <div class="flex justify-between text-sm text-muted-foreground">
            <span>Target: {currentExercise?.sets || 0}x{currentExercise?.reps || 0}</span>
            <span>Rest: {currentExercise?.rest_duration || 60}s</span>
          </div>
        </section>
        
        <!-- Progress -->
        <div class="space-y-2">
          <Progress value={progress} />
          <div class="flex justify-between text-sm text-muted-foreground">
            <span>Progress</span>
            <span>{Math.round(progress)}%</span>
          </div>
        </div>
        
        <!-- Voice Controls -->
        <VoiceControls
          {isListening}
          {error}
          on:startListening={handleStartListening}
          on:stopListening={handleStopListening}
        />
        
        <!-- Assistant Feedback -->
        {#if lastCommand || assistantResponse}
          <div class="space-y-2 p-4 bg-muted rounded-lg">
            {#if lastCommand}
              <div class="text-sm">
                <span class="font-semibold">You:</span> {lastCommand}
              </div>
            {/if}
            {#if assistantResponse}
              <div class="text-sm">
                <span class="font-semibold">Assistant:</span> {assistantResponse}
              </div>
            {/if}
          </div>
        {/if}
        
        <!-- Exercise Progress -->
        <div class="flex justify-between items-center">
          <div class="text-sm">
            {completedSets} / {totalSets} sets
          </div>
          {#if isResting}
            <div class="text-sm font-semibold text-primary">
              Rest: {restTimeRemaining}s
            </div>
          {/if}
        </div>
      </CardContent>
    </Card>
  {/if}
</div>

<style>
  .voice-workout-container {
    max-width: 48rem;
    margin: 0 auto;
    padding: 1rem;
  }
</style>
