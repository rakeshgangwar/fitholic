<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  import type { WorkoutLog } from '$lib/types';
  import { format } from 'date-fns';
  import * as Card from '$lib/components/ui/card';
  import { Alert, AlertDescription } from "$lib/components/ui/alert";
  import { goto } from '$app/navigation';

  let workouts: WorkoutLog[] = [];
  let loading = false;
  let error: string | null = null;

  onMount(() => {
    loadTodaysWorkouts();
  });

  async function loadTodaysWorkouts() {
    try {
      loading = true;
      const today = format(new Date(), 'yyyy-MM-dd');
      const response = await api.get('/workouts/logs', {
        params: {
          start_date: today,
          end_date: today
        }
      });
      workouts = response.data;
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to load today\'s workouts';
    } finally {
      loading = false;
    }
  }

  function startWorkout(workout: WorkoutLog) {
    goto('/dashboard/workouts?tab=log&workout=' + workout.log_id);
  }
</script>

<Card.Root>
  <Card.Header class="flex flex-row items-center gap-4">
    <svg class="h-6 w-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
    </svg>
    <div>
      <Card.Title>Today's Workouts</Card.Title>
      <Card.Description>Your scheduled workouts for today</Card.Description>
    </div>
  </Card.Header>

  <Card.Content>
    {#if error}
      <Alert variant="destructive" class="mb-4">
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    {/if}

    {#if loading}
      <div class="flex justify-center items-center py-8">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-muted border-t-primary"></div>
      </div>
    {:else if workouts.length === 0}
      <div class="text-center py-8 text-muted-foreground">
        <p>No workouts scheduled for today</p>
        <button 
          class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2 mt-4"
          on:click={() => goto('/dashboard/workouts?tab=calendar')}
        >
          View Calendar
        </button>
      </div>
    {:else}
      <div class="space-y-4">
        {#each workouts as workout}
          <div class="flex items-center justify-between p-4 rounded-lg border bg-card">
            <div>
              <h3 class="font-medium">{workout.template?.name || 'Custom Workout'}</h3>
              <p class="text-sm text-muted-foreground">
                {workout.status === 'completed' ? 'Completed' : workout.status === 'ongoing' ? 'In Progress' : 'Not Started'}
              </p>
            </div>
            {#if workout.status !== 'completed'}
              <button 
                class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2"
                on:click={() => startWorkout(workout)}
              >
                {workout.status === 'ongoing' ? 'Continue' : 'Start'}
              </button>
            {/if}
          </div>
        {/each}
      </div>
    {/if}
  </Card.Content>
</Card.Root>
