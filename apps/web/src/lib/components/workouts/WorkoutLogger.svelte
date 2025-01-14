<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import type { WorkoutTemplate, Exercise } from '$lib/types';
  import { api } from '$lib/api';
  import { Button } from "$lib/components/ui/button";
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
  let exerciseData: Record<string, { sets: { weight: number; reps: number }[] }> = {};
  let startTime: string | null = null;
  let notes = '';
  let exercises: Record<string, Exercise> = {};

  async function loadExercises() {
    if (!template) return;
    
    try {
      const response = await api.get('/exercises');
      const exerciseList: Exercise[] = response.data;
      exercises = exerciseList.reduce((acc, exercise) => {
        acc[exercise.exercise_id] = exercise;
        return acc;
      }, {} as Record<string, Exercise>);
    } catch (err) {
      error = 'Failed to load exercises';
    }
  }

  $: if (template) {
    loadExercises();
    template.exercises.forEach(exercise => {
      if (!exerciseData[exercise.exercise_id]) {
        exerciseData[exercise.exercise_id] = {
          sets: Array(exercise.sets).fill({ weight: 0, reps: exercise.reps })
        };
      }
    });
  }

  async function logWorkout() {
    if (!template || !startTime) return;

    try {
      loading = true;
      error = '';

      const logData = {
        session_id: template.template_id,
        start_time: startTime,
        end_time: new Date().toISOString(),
        notes,
        exercises: Object.entries(exerciseData).map(([exercise_id, data]) => ({
          exercise_id,
          sets: data.sets
        }))
      };

      await api.post('/workouts/logs', logData);
      dispatch('logSuccess');
    } catch (err) {
      error = 'Failed to log workout';
    } finally {
      loading = false;
    }
  }

  function updateSet(exerciseId: string, setIndex: number, field: 'weight' | 'reps', value: number) {
    exerciseData = {
      ...exerciseData,
      [exerciseId]: {
        sets: exerciseData[exerciseId].sets.map((set, i) => 
          i === setIndex ? { ...set, [field]: value } : set
        )
      }
    };
  }

  function handleStart() {
    startTime = new Date().toISOString();
  }

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

          {#if template.exercises[currentExerciseIndex]}
            {@const exercise = template.exercises[currentExerciseIndex]}
            <div class="space-y-4">
              <div class="flex justify-between items-center">
                <h3 class="text-lg font-medium">
                  {exercises[exercise.exercise_id]?.name || `Exercise ${currentExerciseIndex + 1}`}
                </h3>
                <div class="flex space-x-2">
                  <button 
                    class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2"
                    on:click={previousExercise}
                    disabled={currentExerciseIndex === 0}
                  >
                    Previous
                  </button>
                  <button 
                    class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2"
                    on:click={nextExercise}
                    disabled={currentExerciseIndex === template.exercises.length - 1}
                  >
                    Next
                  </button>
                </div>
              </div>

              <Card>
                <CardContent class="pt-6">
                  <div class="space-y-4">
                    {#each exerciseData[exercise.exercise_id].sets as set, setIndex}
                      <div class="grid grid-cols-3 gap-4 items-end">
                        <div class="space-y-2">
                          <Label>Set {setIndex + 1}</Label>
                          <Input
                            type="number"
                            min="0"
                            step="0.5"
                            value={set.weight}
                            on:input={(e) => {
                              const target = e.target as HTMLInputElement;
                              updateSet(exercise.exercise_id, setIndex, 'weight', parseFloat(target.value));
                            }}
                            placeholder="Weight (kg)"
                          />
                        </div>
                        <div class="space-y-2">
                          <Label>Reps</Label>
                          <Input
                            type="number"
                            min="0"
                            value={set.reps}
                            on:input={(e) => {
                              const target = e.target as HTMLInputElement;
                              updateSet(exercise.exercise_id, setIndex, 'reps', parseInt(target.value));
                            }}
                            placeholder="Reps"
                          />
                        </div>
                      </div>
                    {/each}
                  </div>
                </CardContent>
              </Card>
            </div>
          {/if}

          <div class="space-y-2">
            <Label for="notes">Session Notes</Label>
            <Textarea
              id="notes"
              bind:value={notes}
              rows="3"
              placeholder="Add any notes about your workout session..."
            />
          </div>

          <div class="flex justify-end">
            <button 
              class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2"
              disabled={loading}
              on:click={logWorkout}
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
          </div>
        </CardContent>
      {/if}
    </Card>
  {/if}
</div> 