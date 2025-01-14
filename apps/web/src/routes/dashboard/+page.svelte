<script lang="ts">
  import { onMount } from 'svelte';
  import { authStore } from '$lib/stores/auth';
  import { api } from '$lib/api';
  import { nav_welcome } from '$lib/paraglide/messages';
  import type { WorkoutLog, WorkoutTemplate, Exercise } from '$lib/types';
  import * as Card from '$lib/components/ui/card';
  import { Button } from '$lib/components/ui/button';
  import { cn } from '$lib/utils';

  let loading = {
    workouts: false,
    exercises: false,
    measurements: false
  };
  let error: string | null = null;
  let latestWorkout: WorkoutLog | null = null;
  let latestWorkoutTemplate: WorkoutTemplate | null = null;
  let upcomingWorkout: WorkoutTemplate | null = null;
  let exerciseCount = 0;
  let measurements = {
    current: { weight: 0, body_fat: 0 },
    previous: { weight: 0, body_fat: 0 }
  };

  onMount(async () => {
    await Promise.all([
      loadLatestWorkout(),
      loadUpcomingWorkout(),
      loadExerciseCount(),
      loadMeasurements()
    ]);
  });

  async function loadLatestWorkout() {
    try {
      loading.workouts = true;
      const response = await api.get('/workouts/logs?limit=1');
      if (response.data.length > 0) {
        latestWorkout = response.data[0];
        if (latestWorkout.template_id) {
          const templateResponse = await api.get(`/workouts/templates/${latestWorkout.template_id}`);
          latestWorkoutTemplate = templateResponse.data;
        }
      }
    } catch (err) {
      console.error('Failed to load latest workout:', err);
    } finally {
      loading.workouts = false;
    }
  }

  async function loadUpcomingWorkout() {
    try {
      const response = await api.get('/workouts/templates?limit=1');
      if (response.data.length > 0) {
        upcomingWorkout = response.data[0];
      }
    } catch (err) {
      console.error('Failed to load upcoming workout:', err);
    }
  }

  async function loadExerciseCount() {
    try {
      loading.exercises = true;
      const response = await api.get('/exercises');
      exerciseCount = response.data.length;
    } catch (err) {
      console.error('Failed to load exercises:', err);
    } finally {
      loading.exercises = false;
    }
  }

  async function loadMeasurements() {
    try {
      loading.measurements = true;
      const response = await api.get('/measurements/me?limit=2');
      if (response.data.length > 0) {
        measurements.current = response.data[0];
        if (response.data.length > 1) {
          measurements.previous = response.data[1];
        }
      }
    } catch (err) {
      console.error('Failed to load measurements:', err);
    } finally {
      loading.measurements = false;
    }
  }

  function getProgressIndicator(current: number, previous: number): string {
    const diff = current - previous;
    if (diff > 0) return '↑';
    if (diff < 0) return '↓';
    return '→';
  }

  function formatDate(date: string): string {
    return new Date(date).toLocaleDateString();
  }
</script>

<div class="py-10">
  <header>
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <h1 class="scroll-m-20 text-4xl font-bold tracking-tight">
        {nav_welcome({ name: $authStore?.first_name || 'User' })}
      </h1>
    </div>
  </header>
  <main>
    <div class="max-w-7xl mx-auto sm:px-6 lg:px-8">
      <div class="px-4 py-8 sm:px-0">
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-2">

          <!-- Next Workout Card -->
          <Card.Root>
            <Card.Header class="flex flex-row items-center gap-4">
              <svg class="h-6 w-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <Card.Title>Next Workout</Card.Title>
                {#if loading.workouts}
                  <Card.Description>Loading...</Card.Description>
                {:else if upcomingWorkout}
                  <Card.Description>{upcomingWorkout.name}</Card.Description>
                  <div class="text-sm text-muted-foreground">
                    {upcomingWorkout.exercises.length} exercises
                  </div>
                {:else}
                  <Card.Description>No workouts planned</Card.Description>
                {/if}
              </div>
            </Card.Header>
            <Card.Footer class="pt-5 flex justify-end">
              <Button variant="outline" href="/dashboard/workouts?tab=sessions">
                Plan next workout
              </Button>
            </Card.Footer>
          </Card.Root>

          <!-- Exercise Library Card -->
          <Card.Root>
            <Card.Header class="flex flex-row items-center gap-4">
              <svg class="h-6 w-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
              <div>
                <Card.Title>Exercise Library</Card.Title>
                {#if loading.exercises}
                  <Card.Description>Loading...</Card.Description>
                {:else}
                  <Card.Description>{exerciseCount} exercises</Card.Description>
                  <div class="text-sm text-muted-foreground">
                    Available in library
                  </div>
                {/if}
              </div>
            </Card.Header>
            <Card.Footer class="pt-5 flex justify-end">
              <Button variant="outline" href="/dashboard/exercises">
                Browse exercises
              </Button>
            </Card.Footer>
          </Card.Root>

          <!-- Latest Workout Card -->
          <Card.Root>
            <Card.Header class="flex flex-row items-center gap-4">
              <svg class="h-6 w-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              <div>
                <Card.Title>Latest Workout</Card.Title>
                {#if loading.workouts}
                  <Card.Description>Loading...</Card.Description>
                {:else if latestWorkout}
                  <Card.Description>
                    {#if latestWorkoutTemplate}
                      {latestWorkoutTemplate.name}
                    {:else}
                      Custom Workout
                    {/if}
                  </Card.Description>
                  <div class="text-sm text-muted-foreground">
                    Completed on {formatDate(latestWorkout.created_at)}
                  </div>
                {:else}
                  <Card.Description>No workouts logged yet</Card.Description>
                {/if}
              </div>
            </Card.Header>
            <Card.Footer class="pt-5 flex justify-end">
              <Button variant="outline" href="/dashboard/workouts">
                View workout history
              </Button>
            </Card.Footer>
          </Card.Root>

          <!-- Body Measurements Card -->
          <Card.Root>
            <Card.Header class="flex flex-row items-center gap-4">
              <svg class="h-6 w-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              <div>
                <Card.Title>Body Measurements</Card.Title>
                {#if loading.measurements}
                  <Card.Description>Loading...</Card.Description>
                {:else if measurements.current.weight}
                  <Card.Description>
                    {measurements.current.weight} kg
                    <span class="text-sm text-muted-foreground">
                      {getProgressIndicator(measurements.current.weight, measurements.previous.weight)}
                    </span>
                  </Card.Description>
                  <div class="text-sm text-muted-foreground">
                    Body fat: {measurements.current.body_fat}%
                    <span>
                      {getProgressIndicator(measurements.current.body_fat, measurements.previous.body_fat)}
                    </span>
                  </div>
                {:else}
                  <Card.Description>No measurements recorded</Card.Description>
                {/if}
              </div>
            </Card.Header>
            <Card.Footer class="pt-5 flex justify-end">
              <Button variant="outline" href="/dashboard/measurements">
                Update measurements
              </Button>
            </Card.Footer>
          </Card.Root>

        </div>
      </div>
    </div>
  </main>
</div> 