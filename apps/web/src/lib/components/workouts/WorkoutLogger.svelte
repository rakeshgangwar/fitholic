<script lang="ts">
  import { onMount, createEventDispatcher } from 'svelte';
  import type { Exercise, WorkoutTemplate, WorkoutLog, WorkoutExerciseLog, WorkoutSetLog } from '$lib/types';
  import { api } from '$lib/api';

  const dispatch = createEventDispatcher();

  export let template: WorkoutTemplate | null = null;
  let exercises: Exercise[] = [];
  let workoutExercises: WorkoutExerciseLog[] = [];
  let duration = 0;
  let notes = '';
  let loading = false;
  let error = '';

  onMount(async () => {
    try {
      const response = await api.get('/exercises');
      exercises = response.data;
      
      if (template) {
        // Initialize workout exercises from template
        workoutExercises = template.exercises.map(templateExercise => ({
          exercise_id: templateExercise.exercise_id,
          sets: Array(templateExercise.sets).fill(null).map(() => ({
            reps: templateExercise.reps,
            weight: 0,
            completed: false
          }))
        }));
      }
    } catch (err) {
      error = 'Failed to load exercises';
    }
  });

  async function handleSubmit() {
    if (workoutExercises.length === 0) {
      error = 'Please add at least one exercise';
      return;
    }

    loading = true;
    error = '';

    const workoutData = {
      template_id: template?.template_id,
      date: new Date().toISOString().split('T')[0],
      duration,
      notes,
      exercises: workoutExercises
    };

    try {
      await api.post('/workouts/logs', workoutData);
      dispatch('success');
    } catch (err) {
      error = 'Failed to save workout log';
    } finally {
      loading = false;
    }
  }

  function updateSet(exerciseIndex: number, setIndex: number, field: string, value: number | boolean) {
    workoutExercises = workoutExercises.map((exercise, i) => {
      if (i === exerciseIndex) {
        const sets = exercise.sets.map((set, j) => {
          if (j === setIndex) {
            return { ...set, [field]: value };
          }
          return set;
        });
        return { ...exercise, sets };
      }
      return exercise;
    });
  }

  function handleNumberInput(event: Event, exerciseIndex: number, setIndex: number, field: string) {
    const input = event.target as HTMLInputElement;
    const value = parseFloat(input.value);
    if (!isNaN(value)) {
      updateSet(exerciseIndex, setIndex, field, value);
    }
  }

  function getExerciseName(exerciseId: string): string {
    return exercises.find(e => e.exercise_id === exerciseId)?.name || 'Unknown Exercise';
  }
</script>

<div class="workout-logger">
  <h2>Log Workout {template ? `- ${template.name}` : ''}</h2>

  {#if error}
    <div class="error">{error}</div>
  {/if}

  <form on:submit|preventDefault={handleSubmit}>
    <div class="form-group">
      <label for="duration">Duration (minutes)</label>
      <input
        type="number"
        id="duration"
        bind:value={duration}
        min="0"
        placeholder="How long was your workout?"
      />
    </div>

    <div class="form-group">
      <label for="notes">Notes</label>
      <textarea
        id="notes"
        bind:value={notes}
        placeholder="How was your workout? Any achievements or challenges?"
      />
    </div>

    <div class="exercises-section">
      <h3>Exercises</h3>
      
      {#if workoutExercises.length > 0}
        <div class="workout-exercises">
          {#each workoutExercises as exercise, exerciseIndex}
            <div class="exercise-item">
              <h4>{getExerciseName(exercise.exercise_id)}</h4>
              <div class="sets-table">
                <table>
                  <thead>
                    <tr>
                      <th>Set</th>
                      <th>Weight (kg)</th>
                      <th>Reps</th>
                      <th>Completed</th>
                    </tr>
                  </thead>
                  <tbody>
                    {#each exercise.sets as set, setIndex}
                      <tr>
                        <td>{setIndex + 1}</td>
                        <td>
                          <input
                            type="number"
                            min="0"
                            step="0.5"
                            bind:value={set.weight}
                            on:input={(e) => handleNumberInput(e, exerciseIndex, setIndex, 'weight')}
                          />
                        </td>
                        <td>
                          <input
                            type="number"
                            min="0"
                            bind:value={set.reps}
                            on:input={(e) => handleNumberInput(e, exerciseIndex, setIndex, 'reps')}
                          />
                        </td>
                        <td>
                          <input
                            type="checkbox"
                            bind:checked={set.completed}
                          />
                        </td>
                      </tr>
                    {/each}
                  </tbody>
                </table>
              </div>
            </div>
          {/each}
        </div>
      {:else}
        <p class="no-exercises">No exercises to log</p>
      {/if}
    </div>

    <div class="form-actions">
      <button type="submit" disabled={loading}>
        {loading ? 'Saving...' : 'Save Workout'}
      </button>
    </div>
  </form>
</div>

<style>
  .workout-logger {
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

  .form-group {
    margin-bottom: 1rem;
  }

  label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
  }

  input[type="number"], textarea {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    margin-bottom: 0.5rem;
  }

  textarea {
    min-height: 100px;
  }

  .exercises-section {
    margin-top: 2rem;
  }

  .exercise-item {
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 1rem;
    margin-bottom: 1rem;
  }

  .sets-table {
    overflow-x: auto;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 1rem;
  }

  th, td {
    padding: 0.5rem;
    text-align: left;
    border-bottom: 1px solid #ddd;
  }

  th {
    background-color: #f5f5f5;
    font-weight: 500;
  }

  td input[type="number"] {
    width: 80px;
    margin: 0;
  }

  td input[type="checkbox"] {
    width: 20px;
    height: 20px;
  }

  .no-exercises {
    text-align: center;
    color: #666;
    padding: 1rem;
    border: 1px dashed #ddd;
    border-radius: 4px;
  }

  .form-actions {
    margin-top: 2rem;
    text-align: right;
  }

  button {
    padding: 0.5rem 1rem;
    background-color: #4CAF50;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }

  button:disabled {
    background-color: #ccc;
    cursor: not-allowed;
  }
</style> 