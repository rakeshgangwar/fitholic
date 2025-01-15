<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { createEventDispatcher } from 'svelte';
  import type { WorkoutTemplate, Exercise, WorkoutLog } from '$lib/types';
  import { api } from '$lib/api';
  import { Card, CardContent, CardHeader, CardTitle } from "$lib/components/ui/card";
  import { Input } from "$lib/components/ui/input";
  import { Label } from "$lib/components/ui/label";
  import { Alert, AlertDescription } from "$lib/components/ui/alert";
  import { Textarea } from "$lib/components/ui/textarea";
  import { Progress } from "$lib/components/ui/progress";
  import { WorkoutVoiceService } from '$lib/services/voice';
  import VoiceControls from './VoiceControls.svelte';

  const dispatch = createEventDispatcher<{
    logSuccess: WorkoutLog;
  }>();

  export let template: WorkoutTemplate | null = null;

  let loading = false;
  let error = '';
  let currentExerciseIndex = 0;
  let exerciseData: Record<string, { sets: { weight: number; reps: number; completed: boolean }[]; completed: boolean }> = {};
  let startTime: string | null = null;
  let notes = '';
  let exercises: Record<string, Exercise> = {};
  let commonWeights = [0, 2.5, 5, 7.5, 10, 12.5, 15, 20, 25, 30, 35, 40, 45, 50];
  let commonReps = [5, 8, 10, 12, 15, 20];
  let currentLogId: string | null = null;

  // Voice assistant state
  let voiceService: WorkoutVoiceService;
  let isListening = false;
  let voiceError: string | null = null;
  let lastCommand = '';
  let assistantResponse = '';
  let isResting = false;
  let restTimeRemaining = 0;
  let restTimer: number;

  onMount(() => {
    loadExercises();
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
      voiceService.setCommandCallback(handleVoiceCommand);
    } catch (e) {
      voiceError = 'Failed to initialize voice assistant';
      console.error(e);
    }
  }

  function handleStartListening() {
    try {
      voiceService.startListening();
      isListening = true;
      voiceError = null;
    } catch (e) {
      voiceError = 'Failed to start listening';
      console.error(e);
    }
  }

  function handleStopListening() {
    try {
      voiceService.stopListening();
      isListening = false;
    } catch (e) {
      voiceError = 'Failed to stop listening';
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

  async function handleVoiceCommand(command: any) {
    lastCommand = command.transcription;
    
    if (command.type === 'log_set') {
      const exercise = template?.exercises[currentExerciseIndex];
      if (exercise) {
        const setIndex = exerciseData[exercise.exercise_id].sets.findIndex(s => !s.completed);
        if (setIndex !== -1) {
          updateSet(exercise.exercise_id, setIndex, 'reps', command.parameters.reps);
          updateSet(exercise.exercise_id, setIndex, 'weight', command.parameters.weight);
          updateSet(exercise.exercise_id, setIndex, 'completed', true);
        }
      }
    } else if (command.type === 'navigate_exercise') {
      if (command.parameters.action === 'next') {
        nextExercise();
      } else if (command.parameters.action === 'previous') {
        previousExercise();
      } else if (command.parameters.action === 'skip') {
        skipExercise();
      }
    } else if (command.type === 'complete_session') {
      if (command.parameters.notes) {
        notes = command.parameters.notes;
      }
      await completeWorkout();
    } else if (command.type === 'start_rest_timer') {
      startRestTimer(command.parameters.duration);
    }
    
    assistantResponse = command.response;
  }

  async function loadExercises() {
    if (!template) return;
    
    try {
      const response = await api.get('/exercises');
      const exerciseList: Exercise[] = response.data;
      exercises = exerciseList.reduce((acc, exercise) => {
        acc[exercise.exercise_id] = exercise;
        return acc;
      }, {} as Record<string, Exercise>);

      // Check for ongoing workout
      const logsResponse = await api.get('/workouts/logs', {
        params: { status: 'ongoing' }
      });
      const ongoingLogs: WorkoutLog[] = logsResponse.data;
      const ongoingLog = ongoingLogs.find(log => log.template_id === template.template_id);
      
      if (ongoingLog) {
        currentLogId = ongoingLog.log_id;
        startTime = ongoingLog.start_time;
        notes = ongoingLog.notes || '';
        
        // Restore exercise data from ongoing log
        ongoingLog.exercises.forEach(exercise => {
          exerciseData[exercise.exercise_id] = {
            sets: exercise.sets,
            completed: exercise.completed
          };
        });
      } else {
        // Initialize new exercise data
        template.exercises.forEach(exercise => {
          if (!exerciseData[exercise.exercise_id]) {
            exerciseData[exercise.exercise_id] = {
              sets: Array(exercise.sets).fill({ weight: 0, reps: 0, completed: false }),
              completed: false
            };
          }
        });
      }
    } catch (err) {
      error = 'Failed to load exercises';
    }
  }

  async function createOrUpdateLog() {
    if (!template || !startTime) return;

    try {
      loading = true;
      error = '';

      const logData = {
        template_id: template.template_id,
        date: new Date().toISOString().split('T')[0],
        start_time: startTime,
        end_time: null,
        status: 'ongoing',
        notes,
        exercises: Object.entries(exerciseData).map(([exercise_id, data]) => ({
          exercise_id,
          sets: data.sets,
          completed: data.completed
        }))
      };

      if (currentLogId) {
        await api.put(`/workouts/logs/${currentLogId}`, logData);
      } else {
        const response = await api.post('/workouts/logs', logData);
        currentLogId = response.data.log_id;
      }
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to save workout';
    } finally {
      loading = false;
    }
  }

  async function completeWorkout() {
    if (!template || !startTime || !currentLogId) return;

    try {
      loading = true;
      error = '';

      const logData = {
        end_time: new Date().toISOString(),
        status: 'completed',
        notes,
        exercises: Object.entries(exerciseData).map(([exercise_id, data]) => ({
          exercise_id,
          sets: data.sets,
          completed: data.completed
        }))
      };

      const response = await api.put(`/workouts/logs/${currentLogId}`, logData);
      dispatch('logSuccess', response.data);
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to complete workout';
    } finally {
      loading = false;
    }
  }

  function handleStart() {
    startTime = new Date().toISOString();
    createOrUpdateLog();
  }

  function updateSet(exerciseId: string, setIndex: number, field: 'weight' | 'reps' | 'completed', value: number | boolean) {
    exerciseData = {
      ...exerciseData,
      [exerciseId]: {
        ...exerciseData[exerciseId],
        sets: exerciseData[exerciseId].sets.map((set, i) => 
          i === setIndex ? { ...set, [field]: value } : set
        )
      }
    };

    // Check if all sets are completed
    const allSetsCompleted = exerciseData[exerciseId].sets.every(set => set.completed);
    if (allSetsCompleted !== exerciseData[exerciseId].completed) {
      exerciseData = {
        ...exerciseData,
        [exerciseId]: {
          ...exerciseData[exerciseId],
          completed: allSetsCompleted
        }
      };
    }

    // Save changes
    if (startTime) {
      createOrUpdateLog();
    }
  }

  $: showCompleteButton = template && startTime && 
     Object.values(exerciseData).length === template?.exercises.length &&
     Object.values(exerciseData).every(exercise => exercise.completed);

  function nextExercise() {
    if (template && currentExerciseIndex < template.exercises.length - 1) {
      currentExerciseIndex++;
    }
  }

  function previousExercise() {
    if (currentExerciseIndex > 0) {
      currentExerciseIndex--;
    }
  }

  function skipExercise() {
    if (template && currentExerciseIndex < template.exercises.length) {
      const exercise = template.exercises[currentExerciseIndex];
      exerciseData = {
        ...exerciseData,
        [exercise.exercise_id]: {
          sets: [],
          completed: true  // Mark as completed when skipped
        }
      };
      nextExercise();
    }
  }

  $: progress = template ? ((currentExerciseIndex + 1) / template.exercises.length) * 100 : 0;

  // Initialize exercise data when template changes
  $: if (template) {
    loadExercises();
  }

  // Initialize exercise data for current exercise if not exists
  $: if (template?.exercises[currentExerciseIndex] && !exerciseData[template.exercises[currentExerciseIndex].exercise_id]) {
    const exercise = template.exercises[currentExerciseIndex];
    exerciseData = {
      ...exerciseData,
      [exercise.exercise_id]: {
        sets: Array(exercise.sets).fill({ weight: 0, reps: 0, completed: false }),
        completed: false
      }
    };
  }
</script>

<div class="max-w-3xl mx-auto">
  {#if !template}
    <Card class="text-center py-12">
      <CardContent class="flex flex-col items-center justify-center">
        <svg class="h-12 w-12 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
        </svg>
        <h3 class="mt-4 text-lg font-semibold">No Workout Selected</h3>
        <p class="mt-2 text-sm text-muted-foreground">
          Please select a workout template to begin logging your exercises.
        </p>
      </CardContent>
    </Card>
  {:else}
    <Card>
      <CardHeader>
        <div class="flex justify-between items-start">
          <div>
            <CardTitle>{template.name}</CardTitle>
            <div class="text-sm text-muted-foreground mt-1">
              Exercise {currentExerciseIndex + 1} of {template.exercises.length}
            </div>
          </div>
          {#if !startTime}
            <button
              class="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
              on:click={handleStart}
            >
              Start Workout
            </button>
          {/if}
        </div>
      </CardHeader>

      {#if error || voiceError}
        <div class="px-6">
          <Alert variant="destructive">
            <AlertDescription>{error || voiceError}</AlertDescription>
          </Alert>
        </div>
      {/if}

      {#if startTime}
        <CardContent class="space-y-6">
          <!-- Progress Bar -->
          <div class="space-y-2">
            <div class="flex items-center justify-between text-sm text-muted-foreground">
              <span>Exercise {currentExerciseIndex + 1} of {template.exercises.length}</span>
              <span>{Math.round(progress)}%</span>
            </div>
            <Progress value={progress} />
          </div>

          <!-- Voice Controls -->
          <div class="border rounded-lg p-4 space-y-4">
            <VoiceControls
              {isListening}
              error={voiceError}
              on:startListening={handleStartListening}
              on:stopListening={handleStopListening}
            />
            
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

            {#if isResting}
              <div class="flex justify-center">
                <div class="text-lg font-semibold text-primary">
                  Rest Timer: {restTimeRemaining}s
                </div>
              </div>
            {/if}
          </div>

          {#if template.exercises[currentExerciseIndex]}
            {@const exercise = template.exercises[currentExerciseIndex]}
            {#if exerciseData[exercise.exercise_id]}
              <div class="space-y-4">
                <div class="flex justify-between items-center">
                  <div>
                    <h3 class="text-lg font-medium">
                      {exercises[exercise.exercise_id]?.name || `Exercise ${currentExerciseIndex + 1}`}
                    </h3>
                    <p class="text-sm text-muted-foreground">
                      Target: {exercise.sets} sets of {exercise.reps} reps
                    </p>
                  </div>
                  <div class="flex space-x-2">
                    <button
                      class="px-3 py-1 text-sm rounded-md bg-secondary text-secondary-foreground hover:bg-secondary/90"
                      on:click={previousExercise}
                      disabled={currentExerciseIndex === 0}
                    >
                      Previous
                    </button>
                    <button
                      class="px-3 py-1 text-sm rounded-md bg-secondary text-secondary-foreground hover:bg-secondary/90"
                      on:click={skipExercise}
                    >
                      Skip
                    </button>
                    <button
                      class="px-3 py-1 text-sm rounded-md bg-secondary text-secondary-foreground hover:bg-secondary/90"
                      on:click={nextExercise}
                      disabled={currentExerciseIndex === template.exercises.length - 1}
                    >
                      Next
                    </button>
                  </div>
                </div>

                <Card>
                  <CardContent class="pt-6">
                    <div class="space-y-6">
                      <!-- Set Management -->
                      <div class="flex justify-between items-center">
                        <h4 class="text-sm font-medium">Sets ({exerciseData[exercise.exercise_id].sets.length})</h4>
                      </div>

                      {#each exerciseData[exercise.exercise_id].sets as set, setIndex}
                        <div class="space-y-4 border rounded-lg p-4 relative">
                          <!-- Set Header -->
                          <div class="flex justify-between items-center">
                            <h4 class="text-sm font-medium">Set {setIndex + 1}</h4>
                            <div class="flex items-center space-x-2">
                              <label class="flex items-center space-x-2">
                                <input
                                  type="checkbox"
                                  checked={set.completed}
                                  on:change={(e) => updateSet(exercise.exercise_id, setIndex, 'completed', e.currentTarget.checked)}
                                  class="rounded border-input"
                                />
                                <span class="text-sm">Complete</span>
                              </label>
                            </div>
                          </div>

                          <!-- Weight Input -->
                          <div class="space-y-2">
                            <Label>Weight (lbs)</Label>
                            <div class="flex flex-wrap gap-2">
                              {#each commonWeights as weight}
                                <button
                                  class="px-3 py-1 text-sm rounded-md {set.weight === weight ? 'bg-primary text-primary-foreground' : 'bg-secondary text-secondary-foreground hover:bg-secondary/90'}"
                                  on:click={() => updateSet(exercise.exercise_id, setIndex, 'weight', weight)}
                                >
                                  {weight}
                                </button>
                              {/each}
                              <Input
                                type="number"
                                value={set.weight}
                                on:input={(e) => updateSet(exercise.exercise_id, setIndex, 'weight', parseFloat(e.currentTarget.value) || 0)}
                                class="w-20"
                                min="0"
                                step="0.5"
                              />
                            </div>
                          </div>

                          <!-- Reps Input -->
                          <div class="space-y-2">
                            <Label>Reps</Label>
                            <div class="flex flex-wrap gap-2">
                              {#each commonReps as reps}
                                <button
                                  class="px-3 py-1 text-sm rounded-md {set.reps === reps ? 'bg-primary text-primary-foreground' : 'bg-secondary text-secondary-foreground hover:bg-secondary/90'}"
                                  on:click={() => updateSet(exercise.exercise_id, setIndex, 'reps', reps)}
                                >
                                  {reps}
                                </button>
                              {/each}
                              <Input
                                type="number"
                                value={set.reps}
                                on:input={(e) => updateSet(exercise.exercise_id, setIndex, 'reps', parseInt(e.currentTarget.value) || 0)}
                                class="w-20"
                                min="0"
                                step="1"
                              />
                            </div>
                          </div>
                        </div>
                      {/each}
                    </div>
                  </CardContent>
                </Card>
              </div>
            {/if}
          {/if}

          <!-- Session Controls -->
          <div class="flex justify-between items-center pt-4 border-t">
            <div class="flex-1 mr-4">
              <Label for="notes">Session Notes</Label>
              <Textarea
                id="notes"
                bind:value={notes}
                on:change={createOrUpdateLog}
                placeholder="Add notes about your workout session..."
                rows="3"
              />
            </div>
            {#if showCompleteButton}
              <button
                class="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
                on:click={completeWorkout}
                disabled={loading}
              >
                Complete Workout
              </button>
            {/if}
          </div>
        </CardContent>
      {/if}
    </Card>
  {/if}
</div>

<style>
  input[type="checkbox"] {
    @apply h-4 w-4;
  }

  :global(.dark) input[type="checkbox"] {
    @apply bg-background border-input;
  }
</style>