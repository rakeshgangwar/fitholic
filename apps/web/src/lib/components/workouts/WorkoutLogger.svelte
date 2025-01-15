<script lang="ts">
  import { onMount } from 'svelte';
  import { createEventDispatcher } from 'svelte';
  import type { WorkoutTemplate, Exercise, WorkoutLog } from '$lib/types';
  import { api } from '$lib/api';
  import { Card, CardContent, CardHeader, CardTitle } from "$lib/components/ui/card";
  import { Input } from "$lib/components/ui/input";
  import { Label } from "$lib/components/ui/label";
  import { Alert, AlertDescription } from "$lib/components/ui/alert";
  import { Textarea } from "$lib/components/ui/textarea";
  import { Progress } from "$lib/components/ui/progress";

  const dispatch = createEventDispatcher<{
    logSuccess: void;
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

  $: if (template) {
    loadExercises();
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

      await api.put(`/workouts/logs/${currentLogId}`, logData);
      dispatch('logSuccess');
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
      createOrUpdateLog();
      nextExercise();
    }
  }

  function getExerciseStatus(exerciseId: string): 'completed' | 'skipped' | 'pending' {
    const data = exerciseData[exerciseId];
    if (!data) return 'pending';
    if (data.completed) return data.sets.length === 0 ? 'skipped' : 'completed';
    return 'pending';
  }
</script>

<div class="max-w-3xl mx-auto">
  {#if !template}
    <Card class="text-center py-12">
      <CardContent class="flex flex-col items-center justify-center">
        <svg class="h-12 w-12 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
        </svg>
        <h3 class="mt-2 text-sm font-medium">No session selected</h3>
        <p class="mt-1 text-sm text-muted-foreground">Please select a workout session to start logging.</p>
      </CardContent>
    </Card>
  {:else}
    <Card>
      <CardHeader>
        <div class="flex justify-between items-start">
          <div>
            <CardTitle>{template.name}</CardTitle>
            {#if template.description}
              <p class="mt-1 text-sm text-muted-foreground">{template.description}</p>
            {/if}
          </div>
          {#if !startTime}
            <button 
              class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2"
              on:click={handleStart}
            >
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"></path>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              Start Session
            </button>
          {/if}
        </div>

        {#if error}
          <Alert variant="destructive" class="mt-4">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        {/if}
      </CardHeader>

      {#if startTime}
        <CardContent class="space-y-6">
          <div class="space-y-2">
            <div class="flex items-center justify-between text-sm text-muted-foreground">
              <span>Exercise {currentExerciseIndex + 1} of {template.exercises.length}</span>
              <span>{Math.round(((currentExerciseIndex + 1) / template.exercises.length) * 100)}%</span>
            </div>
            <Progress value={((currentExerciseIndex + 1) / template.exercises.length) * 100} />
          </div>

          <div class="grid grid-cols-3 gap-4 mt-4">
            {#each ['completed', 'skipped', 'pending'] as status}
              <div class="text-center p-4 bg-card rounded-lg border">
                <div class="text-2xl font-bold">
                  {template.exercises.filter(ex => getExerciseStatus(ex.exercise_id) === status).length}
                </div>
                <div class="text-sm text-muted-foreground capitalize">{status}</div>
              </div>
            {/each}
          </div>

          {#if template.exercises[currentExerciseIndex]}
            {@const exercise = template.exercises[currentExerciseIndex]}
            <div class="space-y-4">
              <div class="flex justify-between items-center">
                <div>
                  <h3 class="text-lg font-medium">
                    {exercises[exercise.exercise_id]?.name || `Exercise ${currentExerciseIndex + 1}`}
                  </h3>
                  <p class="text-sm text-muted-foreground">
                    Status: <span class="capitalize">{getExerciseStatus(exercise.exercise_id)}</span>
                  </p>
                </div>
                <div class="flex space-x-2">
                  <button 
                    type="button"
                    class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2"
                    on:click={previousExercise} 
                    disabled={currentExerciseIndex === 0}
                  >
                    Previous
                  </button>
                  <button 
                    type="button"
                    class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2"
                    on:click={skipExercise}
                  >
                    Skip
                  </button>
                  <button 
                    type="button"
                    class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2"
                    on:click={nextExercise} 
                    disabled={currentExerciseIndex === template.exercises.length - 1}
                  >
                    Next
                  </button>
                </div>
              </div>

              <!-- Exercise Sets -->
              <Card>
                <CardContent class="pt-6">
                  <div class="space-y-6">
                    <!-- Set Management -->
                    <div class="flex justify-between items-center">
                      <h4 class="text-sm font-medium">Sets ({exerciseData[exercise.exercise_id].sets.length})</h4>
                      <div class="flex space-x-2">
                        <button
                          type="button"
                          class="inline-flex items-center justify-center rounded-md text-sm font-medium bg-secondary text-secondary-foreground hover:bg-secondary/80 h-8 px-3"
                          on:click={() => addSet(exercise.exercise_id)}
                        >
                          Add Set
                        </button>
                      </div>
                    </div>

                    {#each exerciseData[exercise.exercise_id].sets as set, setIndex}
                      <div class="space-y-4 border rounded-lg p-4 relative">
                        <!-- Set Header -->
                        <div class="flex justify-between items-center">
                          <h4 class="text-sm font-medium">Set {setIndex + 1}</h4>
                          <div class="flex items-center space-x-2">
                            <button
                              type="button"
                              class="inline-flex items-center justify-center rounded-full w-6 h-6 {set.completed ? 'bg-green-500 text-white' : 'bg-gray-200'}"
                              on:click={() => updateSet(exercise.exercise_id, setIndex, 'completed', !set.completed)}
                            >
                              {#if set.completed}
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                                </svg>
                              {/if}
                            </button>
                            {#if exerciseData[exercise.exercise_id].sets.length > 1}
                              <button
                                type="button"
                                class="text-destructive hover:text-destructive/80"
                                on:click={() => removeSet(exercise.exercise_id, setIndex)}
                              >
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                                </svg>
                              </button>
                            {/if}
                          </div>
                        </div>

                        <!-- Weight Selection -->
                        <div class="space-y-2">
                          <Label>Weight (kg)</Label>
                          <div class="flex flex-wrap gap-2">
                            {#each commonWeights as weight}
                              <button
                                type="button"
                                class="inline-flex items-center justify-center px-3 py-1 rounded-md text-sm
                                  {set.weight === weight ? 'bg-primary text-primary-foreground' : 'bg-secondary text-secondary-foreground'}"
                                on:click={() => updateSet(exercise.exercise_id, setIndex, 'weight', weight)}
                              >
                                {weight}
                              </button>
                            {/each}
                            <button
                              type="button"
                              class="inline-flex items-center justify-center px-3 py-1 rounded-md text-sm bg-secondary text-secondary-foreground"
                              on:click={() => {
                                const weight = prompt('Enter custom weight in kg:');
                                if (weight && !isNaN(parseFloat(weight)) && parseFloat(weight) >= 0) {
                                  updateSet(exercise.exercise_id, setIndex, 'weight', parseFloat(weight));
                                }
                              }}
                            >
                              Custom
                            </button>
                          </div>
                          {#if set.weight > 0}
                            <p class="text-sm text-muted-foreground">Selected: {set.weight}kg</p>
                          {:else}
                            <p class="text-sm text-muted-foreground">Bodyweight</p>
                          {/if}
                        </div>

                        <!-- Reps Selection -->
                        <div class="space-y-2">
                          <Label>Reps</Label>
                          <div class="flex flex-wrap gap-2">
                            {#each commonReps as reps}
                              <button
                                type="button"
                                class="inline-flex items-center justify-center px-3 py-1 rounded-md text-sm
                                  {set.reps === reps ? 'bg-primary text-primary-foreground' : 'bg-secondary text-secondary-foreground'}"
                                on:click={() => updateSet(exercise.exercise_id, setIndex, 'reps', reps)}
                              >
                                {reps}
                              </button>
                            {/each}
                            <button
                              type="button"
                              class="inline-flex items-center justify-center px-3 py-1 rounded-md text-sm bg-secondary text-secondary-foreground"
                              on:click={() => {
                                const reps = prompt('Enter custom reps:');
                                if (reps && !isNaN(parseInt(reps)) && parseInt(reps) > 0) {
                                  updateSet(exercise.exercise_id, setIndex, 'reps', parseInt(reps));
                                }
                              }}
                            >
                              Custom
                            </button>
                          </div>
                          {#if set.reps > 0}
                            <p class="text-sm text-muted-foreground">Selected: {set.reps} reps</p>
                          {/if}
                        </div>
                      </div>
                    {/each}
                  </div>
                </CardContent>
              </Card>
            </div>
          {/if}

          <!-- Session Controls -->
          <div class="flex justify-between items-center pt-4 border-t">
            <div class="flex-1 mr-4">
              <Label>Session Notes</Label>
              <Textarea
                bind:value={notes}
                placeholder="Add any notes about your workout..."
                rows="3"
                class="mt-2"
                on:change={createOrUpdateLog}
              />
            </div>
            <div class="flex flex-col space-y-2">
              <button 
                type="button"
                class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2"
                on:click={() => window.location.reload()}
              >
                Cancel Session
              </button>
              {#if showCompleteButton}
                <button 
                  type="button"
                  class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2"
                  disabled={loading}
                  on:click={completeWorkout}
                >
                  {#if loading}
                    <svg class="animate-spin -ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Saving...
                  {:else}
                    Complete Session
                  {/if}
                </button>
              {/if}
            </div>
          </div>
        </CardContent>
      {/if}
    </Card>
  {/if}
</div> 