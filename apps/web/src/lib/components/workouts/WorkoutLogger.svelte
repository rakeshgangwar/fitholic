<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import type { WorkoutTemplate, Exercise } from '$lib/types';
  import { api } from '$lib/api';

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
    <div class="text-center py-12 bg-white rounded-lg shadow">
      <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
      </svg>
      <h3 class="mt-2 text-sm font-medium text-gray-900">No session selected</h3>
      <p class="mt-1 text-sm text-gray-500">Please select a workout session to start logging.</p>
    </div>
  {:else}
    <div class="bg-white rounded-lg shadow divide-y divide-gray-200">
      <!-- Header -->
      <div class="px-6 py-4">
        <div class="flex justify-between items-start">
          <div>
            <h2 class="text-lg font-medium text-gray-900">{template.name}</h2>
            {#if template.description}
              <p class="mt-1 text-sm text-gray-500">{template.description}</p>
            {/if}
          </div>
          {#if !startTime}
            <button
              type="button"
              class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
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
          <div class="mt-4 rounded-md bg-red-50 p-4">
            <div class="flex">
              <div class="flex-shrink-0">
                <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                </svg>
              </div>
              <div class="ml-3">
                <p class="text-sm font-medium text-red-800">{error}</p>
              </div>
            </div>
          </div>
        {/if}
      </div>

      {#if startTime}
        <!-- Progress Bar -->
        <div class="px-6 py-4 bg-gray-50">
          <div class="flex items-center">
            <div class="flex-1">
              <div class="relative">
                <div class="overflow-hidden h-2 text-xs flex rounded bg-gray-200">
                  <div
                    class="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-indigo-500"
                    style="width: {((currentExerciseIndex + 1) / template.exercises.length) * 100}%"
                  ></div>
                </div>
              </div>
            </div>
            <div class="ml-4 min-w-0 flex-1 text-sm text-gray-500">
              Exercise {currentExerciseIndex + 1} of {template.exercises.length}
            </div>
          </div>
        </div>

        <!-- Current Exercise -->
        <div class="px-6 py-4">
          {#if template.exercises[currentExerciseIndex]}
            {@const exercise = template.exercises[currentExerciseIndex]}
            <div class="space-y-4">
              <div class="flex justify-between items-center">
                <h3 class="text-lg font-medium text-gray-900">
                  {exercises[exercise.exercise_id]?.name || `Exercise ${currentExerciseIndex + 1}`}
                </h3>
                <div class="flex space-x-4">
                  <button
                    type="button"
                    class="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
                    on:click={previousExercise}
                    disabled={currentExerciseIndex === 0}
                  >
                    Previous
                  </button>
                  <button
                    type="button"
                    class="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
                    on:click={nextExercise}
                    disabled={currentExerciseIndex === template.exercises.length - 1}
                  >
                    Next
                  </button>
                </div>
              </div>

              <div class="bg-gray-50 rounded-lg p-4">
                <div class="space-y-4">
                  {#each exerciseData[exercise.exercise_id].sets as set, setIndex}
                    <div class="grid grid-cols-3 gap-4 items-center">
                      <div class="text-sm font-medium text-gray-500">Set {setIndex + 1}</div>
                      <div>
                        <label class="sr-only">Weight (kg)</label>
                        <input
                          type="number"
                          min="0"
                          step="0.5"
                          bind:value={set.weight}
                          on:input={(e) => {
                            const target = e.target as HTMLInputElement;
                            updateSet(exercise.exercise_id, setIndex, 'weight', parseFloat(target.value));
                          }}
                          class="block w-full border border-gray-300 rounded-md shadow-sm py-1.5 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                          placeholder="Weight (kg)"
                        />
                      </div>
                      <div>
                        <label class="sr-only">Reps</label>
                        <input
                          type="number"
                          min="0"
                          bind:value={set.reps}
                          on:input={(e) => {
                            const target = e.target as HTMLInputElement;
                            updateSet(exercise.exercise_id, setIndex, 'reps', parseInt(target.value));
                          }}
                          class="block w-full border border-gray-300 rounded-md shadow-sm py-1.5 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                          placeholder="Reps"
                        />
                      </div>
                    </div>
                  {/each}
                </div>
              </div>
            </div>
          {/if}
        </div>

        <!-- Notes -->
        <div class="px-6 py-4">
          <label for="notes" class="block text-sm font-medium text-gray-700">Session Notes</label>
          <div class="mt-1">
            <textarea
              id="notes"
              bind:value={notes}
              rows="3"
              class="block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              placeholder="Add any notes about your workout session..."
            ></textarea>
          </div>
        </div>

        <!-- Actions -->
        <div class="px-6 py-4 bg-gray-50">
          <div class="flex justify-end">
            <button
              type="button"
              disabled={loading}
              class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
              on:click={logWorkout}
            >
              {#if loading}
                <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Saving...
              {:else}
                Complete Session
              {/if}
            </button>
          </div>
        </div>
      {/if}
    </div>
  {/if}
</div>

<style>
  .workout-logger {
    max-width: 800px;
    margin: 0 auto;
    padding: 1rem;
  }

  .no-session {
    text-align: center;
    padding: 2rem;
    color: #666;
  }

  .session-header {
    margin-bottom: 2rem;
  }

  .session-header h2 {
    margin: 0;
    font-size: 1.5rem;
    color: #1a1a1a;
  }

  .difficulty {
    display: inline-block;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    background: #e5e7eb;
    color: #374151;
    font-size: 0.875rem;
    margin-top: 0.5rem;
  }

  .description {
    color: #4b5563;
    margin-top: 0.5rem;
  }

  .exercise-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1rem;
  }

  .exercise-card h3 {
    margin: 0 0 1rem 0;
    font-size: 1.25rem;
    color: #1a1a1a;
  }

  .sets-grid {
    display: grid;
    gap: 0.5rem;
  }

  .set-header {
    display: grid;
    grid-template-columns: 60px 1fr 1fr;
    gap: 0.5rem;
    font-weight: 500;
    color: #4b5563;
    font-size: 0.875rem;
  }

  .set-row {
    display: grid;
    grid-template-columns: 60px 1fr 1fr;
    gap: 0.5rem;
    align-items: center;
  }

  .set-number {
    color: #6b7280;
    font-size: 0.875rem;
  }

  input {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid #d1d5db;
    border-radius: 4px;
    font-size: 0.875rem;
  }

  input:focus {
    outline: none;
    border-color: #6366f1;
    ring: 2px solid #6366f1;
  }

  .actions {
    margin-top: 2rem;
    display: flex;
    justify-content: flex-end;
  }

  .log-button {
    background: #6366f1;
    color: white;
    padding: 0.75rem 1.5rem;
    border-radius: 6px;
    font-weight: 500;
    transition: background-color 0.2s;
  }

  .log-button:hover {
    background: #4f46e5;
  }

  .log-button:disabled {
    background: #9ca3af;
    cursor: not-allowed;
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