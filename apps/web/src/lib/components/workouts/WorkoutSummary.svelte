<script lang="ts">
  import { onMount } from 'svelte';
  import type { WorkoutLog, Exercise } from '$lib/types';
  import { api } from '$lib/api';

  export let startDate: string | null = null;
  export let endDate: string | null = null;

  let workoutLogs: WorkoutLog[] = [];
  let exercises: Record<string, Exercise> = {};
  let loading = false;
  let error = '';

  $: {
    if (startDate && endDate) {
      loadWorkoutLogs();
    }
  }

  onMount(async () => {
    try {
      const response = await api.get('/exercises');
      exercises = response.data.reduce((acc: Record<string, Exercise>, exercise: Exercise) => {
        acc[exercise.exercise_id] = exercise;
        return acc;
      }, {});
      
      if (!startDate || !endDate) {
        // Default to last 7 days if no date range provided
        const end = new Date();
        const start = new Date();
        start.setDate(start.getDate() - 7);
        
        startDate = start.toISOString().split('T')[0];
        endDate = end.toISOString().split('T')[0];
      }
    } catch (err) {
      error = 'Failed to load exercises';
    }
  });

  async function loadWorkoutLogs() {
    if (!startDate || !endDate) return;

    loading = true;
    error = '';

    try {
      const response = await api.get('/workouts/logs', {
        params: { start_date: startDate, end_date: endDate }
      });
      workoutLogs = response.data;
    } catch (err) {
      error = 'Failed to load workout logs';
    } finally {
      loading = false;
    }
  }

  function formatDate(dateStr: string): string {
    return new Date(dateStr).toLocaleDateString();
  }

  function formatDuration(minutes: number): string {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return hours > 0 ? `${hours}h ${mins}m` : `${mins}m`;
  }

  function getExerciseName(exerciseId: string): string {
    return exercises[exerciseId]?.name || 'Unknown Exercise';
  }

  function calculateVolumeForExercise(sets: Array<{ reps: number; weight?: number; completed?: boolean }>): number {
    return sets.reduce((total, set) => {
      if (set.completed && set.weight) {
        return total + (set.reps * set.weight);
      }
      return total;
    }, 0);
  }
</script>

<div class="workout-summary">
  <h2>Workout History</h2>

  {#if error}
    <div class="error">{error}</div>
  {/if}

  <div class="date-range">
    <div class="form-group">
      <label for="start-date">Start Date</label>
      <input
        type="date"
        id="start-date"
        bind:value={startDate}
      />
    </div>
    <div class="form-group">
      <label for="end-date">End Date</label>
      <input
        type="date"
        id="end-date"
        bind:value={endDate}
      />
    </div>
  </div>

  {#if loading}
    <div class="loading">Loading workout history...</div>
  {:else if workoutLogs.length === 0}
    <div class="no-workouts">No workouts found for the selected date range</div>
  {:else}
    <div class="workout-logs">
      {#each workoutLogs as log}
        <div class="workout-log">
          <div class="workout-header">
            <div class="workout-date">{formatDate(log.date)}</div>
            {#if log.duration}
              <div class="workout-duration">{formatDuration(log.duration)}</div>
            {/if}
          </div>

          {#if log.notes}
            <div class="workout-notes">{log.notes}</div>
          {/if}

          <div class="exercises-list">
            {#each log.exercises as exercise}
              <div class="exercise-log">
                <div class="exercise-header">
                  <span class="exercise-name">{getExerciseName(exercise.exercise_id)}</span>
                  <span class="exercise-volume">
                    Volume: {calculateVolumeForExercise(exercise.sets)} kg
                  </span>
                </div>
                <div class="sets-list">
                  {#each exercise.sets as set, i}
                    <div class="set" class:completed={set.completed}>
                      <span class="set-number">Set {i + 1}:</span>
                      {#if set.weight}
                        <span class="weight">{set.weight}kg</span>
                      {/if}
                      <span class="reps">× {set.reps}</span>
                    </div>
                  {/each}
                </div>
              </div>
            {/each}
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>

<style>
  .workout-summary {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
  }

  .error {
    color: red;
    margin-bottom: 1rem;
    padding: 0.5rem;
    border: 1px solid red;
    border-radius: 4px;
  }

  .date-range {
    display: flex;
    gap: 1rem;
    margin-bottom: 2rem;
  }

  .form-group {
    flex: 1;
  }

  label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
  }

  input[type="date"] {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
  }

  .loading, .no-workouts {
    text-align: center;
    padding: 2rem;
    color: #666;
  }

  .workout-log {
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 1rem;
    margin-bottom: 1rem;
  }

  .workout-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }

  .workout-date {
    font-size: 1.2rem;
    font-weight: 500;
  }

  .workout-duration {
    color: #666;
  }

  .workout-notes {
    padding: 0.5rem;
    background-color: #f5f5f5;
    border-radius: 4px;
    margin-bottom: 1rem;
    font-style: italic;
  }

  .exercise-log {
    margin-bottom: 1rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #eee;
  }

  .exercise-log:last-child {
    border-bottom: none;
    margin-bottom: 0;
    padding-bottom: 0;
  }

  .exercise-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
  }

  .exercise-name {
    font-weight: 500;
  }

  .exercise-volume {
    color: #666;
    font-size: 0.9rem;
  }

  .sets-list {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .set {
    background-color: #f5f5f5;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.9rem;
  }

  .set.completed {
    background-color: #e8f5e9;
  }

  .set-number {
    color: #666;
  }

  .weight {
    font-weight: 500;
    margin: 0 0.25rem;
  }
</style> 