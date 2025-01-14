<script lang="ts">
  import { onMount } from 'svelte';
  import type { WorkoutLog, WorkoutExerciseLog, Exercise } from '$lib/types';
  import { api } from '$lib/api';
  import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "$lib/components/ui/card";
  import { Alert, AlertDescription } from "$lib/components/ui/alert";
  import { Skeleton } from "$lib/components/ui/skeleton";
  import { Separator } from "$lib/components/ui/separator";

  let workouts: WorkoutLog[] = [];
  let exercises: Record<string, Exercise> = {};
  let loading = false;
  let error = '';

  onMount(async () => {
    await Promise.all([
      loadWorkoutHistory(),
      loadExercises()
    ]);
  });

  async function loadWorkoutHistory() {
    try {
      loading = true;
      const response = await api.get('/workouts/logs');
      workouts = response.data;
    } catch (err) {
      error = 'Failed to load workout history';
    } finally {
      loading = false;
    }
  }

  async function loadExercises() {
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

  function formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString();
  }

  function formatDuration(minutes: number): string {
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    return hours > 0 
      ? `${hours}h ${remainingMinutes}m`
      : `${remainingMinutes}m`;
  }

  function getExerciseName(exerciseId: string): string {
    return exercises[exerciseId]?.name || `Exercise ${exerciseId}`;
  }
</script>

<div class="space-y-6">
  <h2 class="text-2xl font-semibold">Workout History</h2>

  {#if error}
    <Alert variant="destructive">
      <AlertDescription>{error}</AlertDescription>
    </Alert>
  {/if}

  {#if loading}
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {#each Array(3) as _}
        <Card>
          <CardHeader>
            <Skeleton class="h-4 w-3/4" />
            <Skeleton class="h-3 w-1/2" />
          </CardHeader>
          <CardContent>
            <div class="space-y-4">
              <div class="flex justify-between">
                <Skeleton class="h-3 w-1/4" />
                <Skeleton class="h-3 w-1/4" />
              </div>
              <Separator />
              <div class="space-y-2">
                <Skeleton class="h-3 w-full" />
                <Skeleton class="h-3 w-3/4" />
              </div>
            </div>
          </CardContent>
        </Card>
      {/each}
    </div>
  {:else if workouts.length === 0}
    <Card>
      <CardContent class="flex flex-col items-center justify-center py-12">
        <svg class="h-12 w-12 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
        </svg>
        <p class="mt-4 text-lg font-medium">No workouts logged yet</p>
        <p class="mt-2 text-sm text-muted-foreground">Start by selecting a workout session and logging your first workout!</p>
      </CardContent>
    </Card>
  {:else}
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {#each workouts as workout}
        <Card>
          <CardHeader>
            <div class="flex justify-between items-start">
              <div>
                <CardTitle>Workout Session</CardTitle>
                <CardDescription>{formatDate(workout.date)}</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div class="space-y-4">
              <div class="grid grid-cols-2 gap-4">
                <div class="space-y-1">
                  <p class="text-sm text-muted-foreground">Duration</p>
                  <p class="text-lg font-medium">{workout.duration ? formatDuration(workout.duration) : 'N/A'}</p>
                </div>
                <div class="space-y-1">
                  <p class="text-sm text-muted-foreground">Exercises</p>
                  <p class="text-lg font-medium">{workout.exercises.length}</p>
                </div>
              </div>

              <Separator />

              <div class="space-y-2">
                {#each workout.exercises as exercise}
                  <div class="flex justify-between items-center text-sm">
                    <span>{getExerciseName(exercise.exercise_id)}</span>
                    <span class="text-muted-foreground">{exercise.sets.length} sets</span>
                  </div>
                {/each}
              </div>

              {#if workout.notes}
                <Separator />
                <div class="space-y-1.5">
                  <p class="text-sm font-medium">Notes</p>
                  <p class="text-sm text-muted-foreground">{workout.notes}</p>
                </div>
              {/if}
            </div>
          </CardContent>
        </Card>
      {/each}
    </div>
  {/if}
</div> 