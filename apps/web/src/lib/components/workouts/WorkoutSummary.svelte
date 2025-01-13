<script lang="ts">
  import { onMount } from 'svelte';
  import type { WorkoutLog } from '$lib/types';
  import { api } from '$lib/api';

  let workouts: WorkoutLog[] = [];
  let loading = false;
  let error = '';

  onMount(async () => {
    await loadWorkoutHistory();
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
</script>

<div class="workout-summary">
  <h2>Workout History</h2>

  {#if error}
    <div class="error">{error}</div>
  {/if}

  {#if loading}
    <div class="loading">Loading workout history...</div>
  {:else if workouts.length === 0}
    <div class="no-workouts">
      <p>No workouts logged yet.</p>
      <p>Start by selecting a workout session and logging your first workout!</p>
    </div>
  {:else}
    <div class="workouts-grid">
      {#each workouts as workout}
        <div class="workout-card">
          <div class="workout-header">
            <h3>{workout.session_name || 'Workout Session'}</h3>
            <span class="date">{formatDate(workout.start_time)}</span>
          </div>
          
          <div class="workout-stats">
            <div class="stat">
              <span class="label">Duration</span>
              <span class="value">{formatDuration(workout.duration)}</span>
            </div>
            <div class="stat">
              <span class="label">Exercises</span>
              <span class="value">{workout.exercises.length}</span>
            </div>
          </div>

          <div class="exercises-list">
            {#each workout.exercises as exercise}
              <div class="exercise-item">
                <span class="exercise-name">{exercise.name}</span>
                <span class="exercise-sets">{exercise.sets.length} sets</span>
              </div>
            {/each}
          </div>

          {#if workout.notes}
            <div class="notes">
              <h4>Notes</h4>
              <p>{workout.notes}</p>
            </div>
          {/if}
        </div>
      {/each}
    </div>
  {/if}
</div>

<style>
  .workout-summary {
    max-width: 1200px;
    margin: 0 auto;
    padding: 1rem;
  }

  h2 {
    font-size: 1.5rem;
    font-weight: 600;
    color: #1a1a1a;
    margin-bottom: 1.5rem;
  }

  .loading {
    text-align: center;
    padding: 2rem;
    color: #6b7280;
  }

  .no-workouts {
    text-align: center;
    padding: 2rem;
    color: #6b7280;
    background: #f9fafb;
    border-radius: 8px;
  }

  .workouts-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1rem;
  }

  .workout-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 1rem;
  }

  .workout-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }

  .workout-header h3 {
    margin: 0;
    font-size: 1.25rem;
    color: #1a1a1a;
  }

  .date {
    color: #6b7280;
    font-size: 0.875rem;
  }

  .workout-stats {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
    margin-bottom: 1rem;
    padding: 0.75rem;
    background: #f9fafb;
    border-radius: 6px;
  }

  .stat {
    display: flex;
    flex-direction: column;
  }

  .label {
    font-size: 0.75rem;
    color: #6b7280;
    text-transform: uppercase;
  }

  .value {
    font-size: 1.125rem;
    font-weight: 500;
    color: #1a1a1a;
  }

  .exercises-list {
    margin-bottom: 1rem;
  }

  .exercise-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem 0;
    border-bottom: 1px solid #e5e7eb;
  }

  .exercise-item:last-child {
    border-bottom: none;
  }

  .exercise-name {
    color: #374151;
    font-size: 0.875rem;
  }

  .exercise-sets {
    color: #6b7280;
    font-size: 0.75rem;
  }

  .notes {
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid #e5e7eb;
  }

  .notes h4 {
    font-size: 0.875rem;
    font-weight: 500;
    color: #374151;
    margin: 0 0 0.5rem 0;
  }

  .notes p {
    font-size: 0.875rem;
    color: #6b7280;
    margin: 0;
  }

  .error {
    background: #fee2e2;
    border: 1px solid #ef4444;
    color: #b91c1c;
    padding: 0.75rem;
    border-radius: 4px;
    margin-bottom: 1rem;
  }
</style> 